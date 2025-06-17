"""
Authentication service for the StickForStats application.

This module provides JWT-based authentication services using Django REST Framework,
adapted from the original Streamlit-based auth_system.py.
"""
import logging
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple, Union
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions

from stickforstats.mainapp.models import User

# Configure logging
logger = logging.getLogger(__name__)


class AuthService:
    """
    Authentication service for StickForStats users.
    
    This service provides methods for user registration, authentication,
    and token management.
    """
    
    def __init__(self, 
                secret_key: str = None, 
                token_expire_minutes: int = 60,
                max_failed_attempts: int = 5,
                lockout_minutes: int = 15,
                min_password_length: int = 8):
        """
        Initialize the authentication service.
        
        Args:
            secret_key: Secret key for JWT encoding/decoding (defaults to settings.SECRET_KEY)
            token_expire_minutes: JWT token expiration time in minutes
            max_failed_attempts: Maximum allowed failed login attempts before account lockout
            lockout_minutes: Duration of account lockout in minutes
            min_password_length: Minimum password length for new accounts
        """
        self.secret_key = secret_key or settings.SECRET_KEY
        self.token_expire_minutes = token_expire_minutes
        self.max_failed_attempts = max_failed_attempts
        self.lockout_minutes = lockout_minutes
        self.min_password_length = min_password_length
    
    def register_user(self, username: str, email: str, password: str) -> Tuple[bool, Optional[str]]:
        """
        Register a new user.
        
        Args:
            username: Unique username
            email: Unique email address
            password: User password (will be hashed)
            
        Returns:
            Tuple of (success, error_message)
        """
        # Validate password length
        if len(password) < self.min_password_length:
            return False, f"Password must be at least {self.min_password_length} characters long"
        
        try:
            # Check if user exists
            if User.objects.filter(username=username).exists():
                return False, "Username already exists"
            
            if User.objects.filter(email=email).exists():
                return False, "Email already exists"
            
            # Create new user
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password  # Django will handle the hashing
                )
                
                # Create user profile
                user.save()
                
            return True, None
            
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            return False, str(e)
    
    def authenticate(self, username_or_email: str, password: str, 
                    request_ip: Optional[str] = None) -> Tuple[bool, Optional[User], Optional[str], Optional[str]]:
        """
        Authenticate a user by username/email and password.
        
        Args:
            username_or_email: Username or email for authentication
            password: Password to verify
            request_ip: IP address of the authentication request
            
        Returns:
            Tuple of (success, user, token, error_message)
        """
        try:
            # Find user by username or email
            if '@' in username_or_email:
                user = User.objects.filter(email=username_or_email).first()
            else:
                user = User.objects.filter(username=username_or_email).first()
            
            if not user or not user.is_active:
                return False, None, None, "Invalid credentials"
            
            # Check if account is locked
            if user.locked_until and user.locked_until > timezone.now():
                remaining_time = int((user.locked_until - timezone.now()).total_seconds() // 60)
                return False, None, None, f"Account is locked. Try again in {remaining_time} minutes"
            
            # Verify password
            if not user.check_password(password):
                with transaction.atomic():
                    user.failed_login_attempts += 1
                    
                    # Lock account if max attempts reached
                    if user.failed_login_attempts >= self.max_failed_attempts:
                        user.locked_until = timezone.now() + timedelta(minutes=self.lockout_minutes)
                    
                    user.save()
                
                return False, None, None, "Invalid credentials"
            
            # Reset failed attempts and update login info
            with transaction.atomic():
                user.failed_login_attempts = 0
                user.last_login = timezone.now()
                if request_ip:
                    user.last_login_ip = request_ip
                user.save()
            
            # Generate token
            token = self._create_token(user)
            return True, user, token, None
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False, None, None, str(e)
    
    def validate_token(self, token: str) -> Tuple[bool, Optional[User], Optional[str]]:
        """
        Validate JWT token and return user.
        
        Args:
            token: JWT token to validate
            
        Returns:
            Tuple of (is_valid, user, error_message)
        """
        try:
            # Decode token
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # Check expiration
            exp = datetime.fromtimestamp(payload['exp'])
            if timezone.now() > timezone.make_aware(exp):
                return False, None, "Token has expired"
            
            # Get user from payload
            user_id = payload['user_id']
            user = User.objects.get(id=user_id)
            
            if not user.is_active:
                return False, None, "User is inactive"
            
            return True, user, None
            
        except jwt.ExpiredSignatureError:
            return False, None, "Token has expired"
        except jwt.InvalidTokenError:
            return False, None, "Invalid token"
        except User.DoesNotExist:
            return False, None, "User not found"
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return False, None, str(e)
    
    def _create_token(self, user: User) -> str:
        """
        Create JWT token for user.
        
        Args:
            user: User to create token for
            
        Returns:
            JWT token string
        """
        expiration = timezone.now() + timedelta(minutes=self.token_expire_minutes)
        payload = {
            'user_id': str(user.id),
            'username': user.username,
            'exp': expiration.timestamp(),
            'iat': timezone.now().timestamp()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def refresh_token(self, token: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Refresh JWT token.
        
        Args:
            token: Existing valid token
            
        Returns:
            Tuple of (success, new_token, error_message)
        """
        valid, user, error = self.validate_token(token)
        
        if not valid or not user:
            return False, None, error
        
        # Generate new token
        new_token = self._create_token(user)
        return True, new_token, None


class JWTAuthentication(BaseAuthentication):
    """
    JWT Authentication for Django REST Framework.
    
    This class provides JWT-based authentication for the REST API.
    """
    
    keyword = 'Bearer'
    auth_service = None
    
    def get_auth_service(self):
        """Get or create AuthService instance."""
        if not self.auth_service:
            self.auth_service = AuthService()
        return self.auth_service
    
    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        auth = request.headers.get('Authorization')
        if not auth:
            return None
        
        parts = auth.split()
        
        if parts[0].lower() != self.keyword.lower() or len(parts) != 2:
            raise exceptions.AuthenticationFailed('Invalid token header')
        
        token = parts[1]
        
        # Validate token
        auth_service = self.get_auth_service()
        valid, user, error = auth_service.validate_token(token)
        
        if not valid or not user:
            raise exceptions.AuthenticationFailed(error or 'Invalid token')
        
        return (user, token)
    
    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the WWW-Authenticate
        header in a 401 Unauthorized response.
        """
        return self.keyword


# Create singleton instance
auth_service = AuthService()

def get_auth_service() -> AuthService:
    """Get global auth service instance."""
    return auth_service