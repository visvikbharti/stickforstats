"""
Simplified test script for the PCA Analysis module API endpoints.
"""

import os
import django
import requests
import json
import sys
import traceback

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stickforstats.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

# Get test user token
User = get_user_model()
try:
    user = User.objects.get(email='testadmin@example.com')
    token, _ = Token.objects.get_or_create(user=user)
    TOKEN = token.key
except:
    print("Error getting user token. Make sure testadmin@example.com exists.")
    sys.exit(1)

# Base URL for API
BASE_URL = "http://localhost:8000"
headers = {"Authorization": f"Token {TOKEN}"}

def test_demo_project():
    """Test creating a demo project directly."""
    print("\nTesting demo project creation...")
    
    # Use Django ORM to create the project and demo data
    from stickforstats.pca_analysis.models import PCAProject
    from stickforstats.pca_analysis.services.data_processor import DataProcessorService
    
    try:
        # Create the project
        project = PCAProject.objects.create(
            name="Direct Demo Project",
            description="Created directly via Django ORM",
            user=user,
            scaling_method="STANDARD"
        )
        
        print(f"Created project: {project.name} (ID: {project.id})")
        
        # Create demo data
        try:
            summary = DataProcessorService.create_demo_data(project.id)
            print(f"Demo data created: {summary}")
        except Exception as e:
            print(f"Error creating demo data: {str(e)}")
            traceback.print_exc()
        
        return project.id
    except Exception as e:
        print(f"Error in test_demo_project: {str(e)}")
        traceback.print_exc()
        return None

def main():
    """Run the test."""
    test_demo_project()

if __name__ == "__main__":
    main()