import os
import django
import requests
from pathlib import Path

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stickforstats.settings')
django.setup()

from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

# Get the token
user = User.objects.get(email='testadmin@example.com')
token, _ = Token.objects.get_or_create(user=user)

# API URL
api_url = 'http://127.0.0.1:8000/api/v1/core/datasets/'

# File path
file_path = Path('/Users/vishalbharti/Downloads/StickForStats_Migration/new_project/test_data.csv')

# Create dataset directly using Django ORM
from stickforstats.mainapp.models.analysis import Dataset

with open(file_path, 'rb') as f:
    file_content = f.read()

# Create a SimpleUploadedFile instance
uploaded_file = SimpleUploadedFile(
    name=file_path.name,
    content=file_content,
    content_type='text/csv'
)

# Create the dataset
dataset = Dataset.objects.create(
    user=user,
    name='Test Dataset',
    description='A test dataset created programmatically',
    file=uploaded_file,
    file_type='csv',
    has_header=True,
    delimiter=',',
    row_count=5,
    column_count=5,
    columns_info={
        "column1": {"type": "numeric", "missing": 0},
        "column2": {"type": "categorical", "missing": 0},
        "column3": {"type": "datetime", "missing": 0},
        "column4": {"type": "numeric", "missing": 0},
        "column5": {"type": "text", "missing": 0}
    }
)

print(f"Dataset created with ID: {dataset.id}")

# Now test retrieving datasets using the API
response = requests.get(
    api_url,
    headers={
        'Authorization': f'Token {token.key}'
    }
)

print(f"API Response Status: {response.status_code}")
print(f"API Response Content: {response.json()}")