import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stickforstats.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# List all users
try:
    users = User.objects.all()
    print(f"Total users: {users.count()}")
    for user in users:
        print(f"User: {user.username}, Email: {user.email}, ID: {user.id}")
except Exception as e:
    print(f"Error listing users: {e}")
    
# Check the User model
print(f"\nUser model: {User.__name__}")
print(f"User model table: {User._meta.db_table}")
print(f"User model app label: {User._meta.app_label}")
print(f"User model module: {User.__module__}")