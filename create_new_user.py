import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stickforstats.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

# Create a new admin user
try:
    # First check if the user already exists by email
    email = 'testadmin@example.com'
    username = 'testadmin'
    password = 'testadmin'
    
    if User.objects.filter(email=email).exists():
        user = User.objects.get(email=email)
        print(f"User {user.username} already exists with email {email}")
    else:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"Created new superuser with username: {user.username}, email: {user.email}")
    
    # Create or get token
    token, created = Token.objects.get_or_create(user=user)
    if created:
        print(f"Token created: {token.key}")
    else:
        print(f"Token already exists: {token.key}")
        
except Exception as e:
    print(f"Error creating user: {e}")