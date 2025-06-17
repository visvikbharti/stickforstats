"""
Test script for the DOE Analysis module API endpoints.
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

def test_doe_endpoints():
    """Test DOE Analysis endpoints"""
    print("\nTesting DOE Analysis endpoints...")
    
    # Check the main DOE endpoint
    response = requests.get(f"{BASE_URL}/api/v1/doe-analysis/", headers=headers)
    if response.status_code == 200:
        print("DOE Analysis API is accessible")
        print(f"Available endpoints: {response.text}")
    else:
        print(f"Error accessing DOE Analysis API: {response.text}")
        return False
    
    return True

def create_experiment_design():
    """Create a new experiment design"""
    print("\nCreating experiment design...")
    
    # Define a simple 2^2 factorial design
    design_data = {
        "name": "Test Factorial Design",
        "description": "A simple 2^2 factorial design for testing",
        "design_type": "FACTORIAL_DESIGN",
        "num_factors": 2,
        "num_runs": 4,
        "num_center_points": 0,
        "num_replicates": 1,
        "is_randomized": True,
        "factor_details": {
            "factors": [
                {"name": "Temperature", "symbol": "A", "type": "CONTINUOUS_FACTOR", "low": 25, "high": 35, "units": "°C"},
                {"name": "Pressure", "symbol": "B", "type": "CONTINUOUS_FACTOR", "low": 1, "high": 5, "units": "bar"}
            ]
        },
        "response_details": {
            "responses": [
                {"name": "Yield", "symbol": "Y", "units": "%", "objective": "maximize"}
            ]
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/doe-analysis/experiment-designs/",
        headers=headers,
        json=design_data
    )
    
    if response.status_code == 201:
        design = response.json()
        print(f"Created experiment design: {design['name']} (ID: {design['id']})")
        return design['id']
    else:
        print(f"Error creating experiment design: {response.text}")
        return None

def main():
    """Run the DOE Analysis tests"""
    # Test the DOE endpoints
    if not test_doe_endpoints():
        return
    
    # Create an experiment design
    design_id = create_experiment_design()
    if design_id:
        print(f"Successfully created experiment design with ID {design_id}")
    else:
        print("Failed to create experiment design")

if __name__ == "__main__":
    main()