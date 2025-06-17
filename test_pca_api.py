"""
Test script for the PCA Analysis API endpoints.
"""

import os
import django
import requests
import json
import sys

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

def list_pca_projects():
    """List all PCA projects"""
    print("\nListing PCA projects...")
    response = requests.get(f"{BASE_URL}/api/v1/pca-analysis/projects/", headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        # Check if the response is paginated
        if isinstance(response_data, dict) and 'results' in response_data:
            projects = response_data['results']
        else:
            projects = response_data

        print(f"Found {len(projects)} projects")
        for project in projects:
            print(f"- {project['name']} (ID: {project['id']})")
        return projects
    else:
        print(f"Error listing projects: {response.text}")
        return []

def get_project_details(project_id):
    """Get details of a specific project"""
    print(f"\nGetting details for project {project_id}...")
    response = requests.get(f"{BASE_URL}/api/v1/pca-analysis/projects/{project_id}/", headers=headers)
    
    if response.status_code == 200:
        project = response.json()
        print(f"Project: {project['name']}")
        print(f"Samples: {project['sample_count']}")
        print(f"Genes: {project['gene_count']}")
        print(f"Sample Groups: {project['group_count']}")
        return project
    else:
        print(f"Error getting project details: {response.text}")
        return None

def list_sample_groups(project_id):
    """List sample groups for a project"""
    print(f"\nListing sample groups for project {project_id}...")
    response = requests.get(f"{BASE_URL}/api/v1/pca-analysis/projects/{project_id}/groups/", headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        # Check if the response is paginated
        if isinstance(response_data, dict) and 'results' in response_data:
            groups = response_data['results']
        else:
            groups = response_data

        print(f"Found {len(groups)} sample groups")
        for group in groups:
            print(f"- {group['name']} (ID: {group['id']})")
        return groups
    else:
        print(f"Error listing sample groups: {response.text}")
        return []

def create_demo_project():
    """Create a demo project through the API"""
    print("\nCreating a demo project...")
    data = {
        "project_name": "API Demo Project",
        "project_description": "Created through the API",
        "scaling_method": "STANDARD"
    }
    response = requests.post(f"{BASE_URL}/api/v1/pca-analysis/projects/create_demo/",
                           headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        print(f"Success! Demo project created: {result.get('project_id')}")
        return result.get('project_id')
    else:
        print(f"Failed to create demo project: {response.text}")
        return None

def main():
    """Run the tests"""
    # List existing projects
    print("\n=== BEFORE DEMO CREATION ===")
    projects_before = list_pca_projects()

    # Create a demo project
    demo_project_id = create_demo_project()

    # List projects again to see the new one
    print("\n=== AFTER DEMO CREATION ===")
    projects_after = list_pca_projects()

    # If we have a demo project, get its details
    if demo_project_id:
        get_project_details(demo_project_id)
        list_sample_groups(demo_project_id)

if __name__ == "__main__":
    main()