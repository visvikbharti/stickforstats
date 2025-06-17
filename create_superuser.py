import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stickforstats.settings')
django.setup()

from stickforstats.mainapp.models.user import User

# Create superuser if it doesn't exist
try:
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Superuser 'admin' created successfully!")
    else:
        print("Superuser 'admin' already exists.")
except Exception as e:
    print(f"Error creating superuser: {e}")