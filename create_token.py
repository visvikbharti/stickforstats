import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stickforstats.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

# Get or create token for admin user
try:
    user = User.objects.get(email='admin@example.com')
    token, created = Token.objects.get_or_create(user=user)
    if created:
        print(f"Token created for user '{user.username}': {token.key}")
    else:
        print(f"Token already exists for user '{user.username}': {token.key}")
except User.DoesNotExist:
    print("Admin user not found.")
except Exception as e:
    print(f"Error creating token: {e}")