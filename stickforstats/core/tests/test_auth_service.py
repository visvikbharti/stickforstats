import unittest
from unittest.mock import patch, MagicMock
import os
import json
from pathlib import Path
from django.test import TestCase
from django.conf import settings
import jwt
from django.contrib.auth.hashers import make_password

from stickforstats.core.services.auth.auth_service import AuthService, JWTAuthentication

class TestAuthService(TestCase):
    """Test cases for the AuthService."""
    
    def setUp(self):
        """Set up test data."""
        self.auth_service = AuthService()
        self.test_username = "test_user"
        self.test_password = "test_password"
        self.test_email = "test@example.com"
        
        # Clear users file before each test
        users_file = self.auth_service._get_users_file_path()
        if os.path.exists(users_file):
            os.remove(users_file)
            
        # Initialize empty users dict
        self.auth_service.users = {}
        
    def tearDown(self):
        """Clean up test data."""
        # Remove test users file if it exists
        users_file = self.auth_service._get_users_file_path()
        if os.path.exists(users_file):
            os.remove(users_file)
    
    def test_register_user(self):
        """Test registering a new user."""
        # Register user
        result = self.auth_service.register_user(
            username=self.test_username,
            password=self.test_password,
            email=self.test_email
        )
        
        # Verify result
        self.assertIn('user', result)
        self.assertIn('token', result)
        self.assertEqual(result['user']['username'], self.test_username)
        self.assertEqual(result['user']['email'], self.test_email)
        
        # Verify user was saved
        self.assertIn(self.test_username, self.auth_service.users)
        user_record = self.auth_service.users[self.test_username]
        self.assertEqual(user_record['username'], self.test_username)
        self.assertEqual(user_record['email'], self.test_email)
        
        # Verify password was hashed
        self.assertNotEqual(user_record['password'], self.test_password)
        
        # Test duplicate username
        duplicate_result = self.auth_service.register_user(
            username=self.test_username,
            password="different_password",
            email="different@example.com"
        )
        self.assertIn('error', duplicate_result)
        self.assertEqual(duplicate_result['error'], 'Username already exists')
    
    def test_login_user(self):
        """Test logging in a user."""
        # Register user first
        self.auth_service.register_user(
            username=self.test_username,
            password=self.test_password,
            email=self.test_email
        )
        
        # Login with correct credentials
        login_result = self.auth_service.login_user(
            username=self.test_username,
            password=self.test_password
        )
        
        # Verify result
        self.assertIn('user', login_result)
        self.assertIn('token', login_result)
        self.assertEqual(login_result['user']['username'], self.test_username)
        
        # Login with incorrect password
        bad_login = self.auth_service.login_user(
            username=self.test_username,
            password="wrong_password"
        )
        self.assertIn('error', bad_login)
        
        # Login with non-existent user
        nonexistent_login = self.auth_service.login_user(
            username="nonexistent_user",
            password=self.test_password
        )
        self.assertIn('error', nonexistent_login)
    
    def test_validate_token(self):
        """Test validating JWT tokens."""
        # Register user
        result = self.auth_service.register_user(
            username=self.test_username,
            password=self.test_password,
            email=self.test_email
        )
        token = result['token']
        
        # Validate token
        is_valid, user_info = self.auth_service.validate_token(token)
        self.assertTrue(is_valid)
        self.assertEqual(user_info['username'], self.test_username)
        
        # Validate invalid token
        is_valid, user_info = self.auth_service.validate_token("invalid.token.string")
        self.assertFalse(is_valid)
        self.assertIsNone(user_info)
        
        # Validate expired token
        with patch('jwt.decode') as mock_decode:
            mock_decode.side_effect = jwt.ExpiredSignatureError()
            is_valid, user_info = self.auth_service.validate_token(token)
            self.assertFalse(is_valid)
            self.assertIsNone(user_info)
    
    def test_update_user(self):
        """Test updating user information."""
        # Register user first
        self.auth_service.register_user(
            username=self.test_username,
            password=self.test_password,
            email=self.test_email
        )
        
        # Update user
        updates = {
            'email': 'new@example.com',
            'full_name': 'Test User',
            'password': 'new_password'
        }
        result = self.auth_service.update_user(self.test_username, updates)
        
        # Verify result
        self.assertEqual(result['email'], 'new@example.com')
        self.assertEqual(result['full_name'], 'Test User')
        
        # Verify user was updated in storage
        user_record = self.auth_service.users[self.test_username]
        self.assertEqual(user_record['email'], 'new@example.com')
        self.assertEqual(user_record['full_name'], 'Test User')
        
        # Verify login with new password works
        login_result = self.auth_service.login_user(
            username=self.test_username,
            password='new_password'
        )
        self.assertIn('user', login_result)
        
        # Verify update for non-existent user
        nonexistent_update = self.auth_service.update_user('nonexistent_user', updates)
        self.assertIn('error', nonexistent_update)
    
    def test_delete_user(self):
        """Test deleting a user."""
        # Register user first
        self.auth_service.register_user(
            username=self.test_username,
            password=self.test_password,
            email=self.test_email
        )
        
        # Delete user
        result = self.auth_service.delete_user(self.test_username)
        self.assertTrue(result)
        
        # Verify user is deleted
        self.assertNotIn(self.test_username, self.auth_service.users)
        
        # Verify delete non-existent user
        nonexistent_delete = self.auth_service.delete_user('nonexistent_user')
        self.assertFalse(nonexistent_delete)
    
    def test_has_permission(self):
        """Test permission checking."""
        # Register users with different roles
        self.auth_service.register_user(
            username='admin_user',
            password='admin_pass',
            email='admin@example.com',
            role='admin'
        )
        
        self.auth_service.register_user(
            username='regular_user',
            password='user_pass',
            email='user@example.com',
            role='user'
        )
        
        # Test admin permissions
        self.assertTrue(self.auth_service.has_permission('admin_user', 'any:permission'))
        
        # Test regular user permissions
        self.assertTrue(self.auth_service.has_permission('regular_user', 'data:read'))
        self.assertFalse(self.auth_service.has_permission('regular_user', 'user:admin'))
        
        # Test non-existent user
        self.assertFalse(self.auth_service.has_permission('nonexistent_user', 'data:read'))
        
    def test_jwt_authentication(self):
        """Test JWT authentication for Django."""
        # Create a mock request
        mock_request = MagicMock()
        mock_request.META = {}
        
        # Create JWT authentication instance
        jwt_auth = JWTAuthentication()
        
        # Test with no Authorization header
        result = jwt_auth.authenticate(mock_request)
        self.assertIsNone(result)
        
        # Test with valid header but invalid token
        mock_request.META['HTTP_AUTHORIZATION'] = 'Bearer invalid.token'
        
        with self.assertRaises(Exception):  # Should raise AuthenticationFailed
            jwt_auth.authenticate(mock_request)
            
        # Test with valid token
        # Register user
        result = self.auth_service.register_user(
            username=self.test_username,
            password=self.test_password,
            email=self.test_email
        )
        token = result['token']
        
        # Mock validate_token to return success
        with patch('stickforstats.core.services.auth.auth_service.AuthService.validate_token') as mock_validate:
            mock_validate.return_value = (True, {
                'username': self.test_username,
                'id': '12345',
                'role': 'user',
                'permissions': ['data:read']
            })
            
            mock_request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'
            user, auth_token = jwt_auth.authenticate(mock_request)
            
            # Verify authentication succeeded
            self.assertEqual(user.username, self.test_username)
            self.assertEqual(user.role, 'user')
            self.assertTrue(user.is_authenticated)