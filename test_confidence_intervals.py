import os
import django
import requests
import json
import numpy as np

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stickforstats.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

# Get the token
user = User.objects.get(email='testadmin@example.com')
token, _ = Token.objects.get_or_create(user=user)
token_key = token.key

base_url = 'http://127.0.0.1:8000/api/v1'
headers = {
    'Authorization': f'Token {token_key}',
    'Content-Type': 'application/json'
}

# Test creating a confidence interval project
def test_create_project():
    url = f"{base_url}/confidence-intervals/projects/"
    data = {
        "name": "Test Confidence Interval Project",
        "description": "A project to test confidence intervals API",
        "is_public": False
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"Create project status code: {response.status_code}")
    
    if response.status_code == 201:
        project_data = response.json()
        print(f"Created project: {project_data['name']} (ID: {project_data['id']})")
        return project_data['id']
    else:
        print(f"Failed to create project: {response.text}")
        return None

# Test creating interval data
def test_create_interval_data(project_id):
    url = f"{base_url}/confidence-intervals/data/"
    
    # Generate sample data - normal distribution with mean 100 and std dev 15
    np.random.seed(42)
    sample_data = np.random.normal(100, 15, 50).tolist()
    
    data = {
        "project": project_id,
        "name": "Sample Normal Data",
        "description": "Normally distributed sample data for confidence interval analysis",
        "data_type": "NORMAL",
        "data": {
            "values": sample_data,
            "parameters": {
                "mean": 100,
                "std_dev": 15
            }
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"Create interval data status code: {response.status_code}")
    
    if response.status_code == 201:
        data_response = response.json()
        print(f"Created interval data: {data_response['name']} (ID: {data_response['id']})")
        return data_response['id']
    else:
        print(f"Failed to create interval data: {response.text}")
        return None

# Test calculating a confidence interval
def test_calculate_interval(project_id, data_id):
    url = f"{base_url}/confidence-intervals/calculate/calculate/"

    # Generate sample data - normal distribution with mean 100 and std dev 15
    np.random.seed(42)
    sample_data = np.random.normal(100, 15, 50).tolist()

    data = {
        "project_id": project_id,
        "data_id": data_id,
        "interval_type": "MEAN_T",
        "confidence_level": 0.95,
        "name": "Mean Confidence Interval (t)",
        "description": "95% confidence interval for the population mean using t-distribution",
        "numeric_data": sample_data  # Include the actual data points
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"Calculate interval status code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Interval result: {json.dumps(result, indent=2)}")
    else:
        print(f"Failed to calculate interval: {response.text}")

if __name__ == "__main__":
    print("Testing Confidence Intervals API...")
    project_id = test_create_project()
    
    if project_id:
        data_id = test_create_interval_data(project_id)
        
        if data_id:
            test_calculate_interval(project_id, data_id)