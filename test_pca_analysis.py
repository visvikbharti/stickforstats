"""
Test script for the PCA Analysis module API endpoints.
"""

import json
import requests
import sys
import os
import django
import traceback

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stickforstats.settings')
django.setup()

# Change this to match your server setup
BASE_URL = "http://localhost:8000"

# Test user credentials
USERNAME = "pcatest"
PASSWORD = "testpass123"

# Create a superuser if it doesn't exist
def ensure_user_exists():
    from django.contrib.auth import get_user_model
    from rest_framework.authtoken.models import Token
    User = get_user_model()

    # Check if the user exists
    user = User.objects.filter(username=USERNAME).first()
    if not user:
        print(f"Creating test user {USERNAME}...")
        try:
            user = User.objects.create_user(
                username=USERNAME,
                email="pca@test.com",
                password=PASSWORD
            )
            print("Test user created successfully.")
        except Exception as e:
            print(f"Error creating test user: {str(e)}")
            traceback.print_exc()
            return False
    else:
        print(f"Test user {USERNAME} already exists.")
    
    # Ensure token exists
    token, _ = Token.objects.get_or_create(user=user)
    print(f"Token: {token.key}")
    return True

def test_pca_analysis():
    """Test the PCA Analysis module API endpoints."""
    
    print("\n==== Testing PCA Analysis Module ====\n")
    
    # Authenticate
    print("Logging in...")
    auth_resp = requests.post(
        f"{BASE_URL}/api/v1/core/auth/login/",
        json={"username": USERNAME, "password": PASSWORD}
    )

    # For debugging - check what endpoints are available
    if auth_resp.status_code != 200:
        print("Authentication failed. Let's see what endpoints are available...")
        resp = requests.get(f"{BASE_URL}/api/v1/core/")
        print(f"Core API endpoints: {resp.text}")
    
    if auth_resp.status_code != 200:
        print(f"Authentication failed: {auth_resp.text}")
        return False
    
    token = auth_resp.json()['token']
    headers = {"Authorization": f"Token {token}"}
    
    # Test creating a demo project
    print("\n1. Creating demo project...")
    create_demo_resp = requests.post(
        f"{BASE_URL}/api/v1/pca-analysis/projects/create_demo/",
        headers=headers,
        json={
            "project_name": "Test Demo Project",
            "project_description": "A test demo project for PCA analysis",
            "scaling_method": "STANDARD"
        }
    )
    
    if create_demo_resp.status_code != 200:
        print(f"Demo project creation failed: {create_demo_resp.text}")
        return False
    
    print("Success! Demo project created:")
    project_data = create_demo_resp.json()
    print(json.dumps(project_data, indent=2))
    
    project_id = project_data['project_id']
    
    # Test listing projects
    print("\n2. Listing projects...")
    list_projects_resp = requests.get(
        f"{BASE_URL}/api/v1/pca-analysis/projects/",
        headers=headers
    )
    
    if list_projects_resp.status_code != 200:
        print(f"Project listing failed: {list_projects_resp.text}")
        return False
    
    print(f"Found {len(list_projects_resp.json())} projects")
    
    # Test retrieving the project
    print("\n3. Retrieving project details...")
    project_detail_resp = requests.get(
        f"{BASE_URL}/api/v1/pca-analysis/projects/{project_id}/",
        headers=headers
    )
    
    if project_detail_resp.status_code != 200:
        print(f"Project retrieval failed: {project_detail_resp.text}")
        return False
    
    print("Success! Project details retrieved:")
    print(json.dumps(project_detail_resp.json(), indent=2))
    
    # Test listing sample groups
    print("\n4. Listing sample groups...")
    groups_resp = requests.get(
        f"{BASE_URL}/api/v1/pca-analysis/projects/{project_id}/groups/",
        headers=headers
    )
    
    if groups_resp.status_code != 200:
        print(f"Sample group listing failed: {groups_resp.text}")
        return False
    
    print(f"Found {len(groups_resp.json())} sample groups")
    
    # Test running PCA analysis
    print("\n5. Running PCA analysis...")
    run_pca_resp = requests.post(
        f"{BASE_URL}/api/v1/pca-analysis/projects/{project_id}/run_pca/",
        headers=headers,
        json={"n_components": 3}
    )
    
    if run_pca_resp.status_code != 200:
        print(f"PCA analysis run failed: {run_pca_resp.text}")
        return False
    
    print("Success! PCA analysis started:")
    print(json.dumps(run_pca_resp.json(), indent=2))
    
    # Test listing PCA results (might be empty if the task is still running)
    print("\n6. Listing PCA results...")
    results_resp = requests.get(
        f"{BASE_URL}/api/v1/pca-analysis/results/",
        headers=headers
    )
    
    if results_resp.status_code != 200:
        print(f"PCA results listing failed: {results_resp.text}")
        return False
    
    print(f"Found {len(results_resp.json())} PCA results")
    
    # If we found any results, try to get visualizations
    if results_resp.json():
        result_id = results_resp.json()[0]['id']
        
        print("\n7. Listing visualizations for the result...")
        visualizations_resp = requests.get(
            f"{BASE_URL}/api/v1/pca-analysis/results/{result_id}/visualizations/",
            headers=headers
        )
        
        if visualizations_resp.status_code != 200:
            print(f"Visualizations listing failed: {visualizations_resp.text}")
        else:
            print(f"Found {len(visualizations_resp.json())} visualizations")
    
    print("\nPCA Analysis module tests completed successfully!")
    return True


def test_pca_simplified_api():
    """Test the simplified PCA API endpoints."""
    
    print("\n\n==== Testing Simplified PCA API ====\n")
    
    # Authenticate
    print("Logging in...")
    auth_resp = requests.post(
        f"{BASE_URL}/api/v1/core/auth/login/",
        json={"username": USERNAME, "password": PASSWORD}
    )
    
    if auth_resp.status_code != 200:
        print(f"Authentication failed: {auth_resp.text}")
        return False
    
    token = auth_resp.json()['token']
    headers = {"Authorization": f"Token {token}"}
    
    # Test Quick PCA
    print("\n1. Testing Quick PCA...")
    import pandas as pd
    
    # Create sample data
    data_matrix = [
        [8.2, 7.9, 8.1, 7.8, 8.3, 5.1, 4.9, 5.2, 4.8, 5.3],
        [7.9, 8.1, 8.0, 8.2, 7.8, 4.9, 5.1, 5.0, 5.2, 4.8],
        [8.1, 8.0, 7.9, 8.1, 8.2, 5.0, 5.2, 4.9, 5.1, 5.0],
        [5.1, 4.9, 5.2, 4.8, 5.3, 8.2, 7.9, 8.1, 7.8, 8.3],
        [4.9, 5.1, 5.0, 5.2, 4.8, 7.9, 8.1, 8.0, 8.2, 7.8],
        [5.0, 5.2, 4.9, 5.1, 5.0, 8.1, 8.0, 7.9, 8.1, 8.2],
        [4.2, 4.1, 3.9, 4.0, 4.3, 4.2, 4.1, 3.9, 4.0, 4.3],
        [3.9, 4.0, 4.2, 4.1, 3.8, 3.9, 4.0, 4.2, 4.1, 3.8],
        [4.1, 3.9, 4.0, 3.8, 4.2, 4.1, 3.9, 4.0, 3.8, 4.2]
    ]
    
    sample_names = ['TypeA_1', 'TypeA_2', 'TypeA_3', 'TypeB_1', 'TypeB_2', 'TypeB_3', 'TypeC_1', 'TypeC_2', 'TypeC_3']
    feature_names = ['Gene1', 'Gene2', 'Gene3', 'Gene4', 'Gene5', 'Gene6', 'Gene7', 'Gene8', 'Gene9', 'Gene10']
    
    quick_pca_data = {
        'data_matrix': data_matrix,
        'sample_names': sample_names,
        'feature_names': feature_names,
        'n_components': 3,
        'scaling_method': 'standard',
        'generate_visualizations': True
    }
    
    quick_pca_resp = requests.post(
        f"{BASE_URL}/api/v1/pca-analysis/quick/",
        headers=headers,
        json=quick_pca_data
    )
    
    if quick_pca_resp.status_code != 200:
        print(f"Quick PCA failed: {quick_pca_resp.text}")
        return False
    
    print("Success! Quick PCA results:")
    quick_result = quick_pca_resp.json()
    print(f"- Components computed: {quick_result['data']['results']['n_components_used']}")
    print(f"- Variance explained: {[f'{v:.1f}%' for v in quick_result['data']['results']['explained_variance_ratio']]}")
    print(f"- Visualizations: {list(quick_result['data']['visualizations'].keys())}")
    
    # Test Gene Contribution
    print("\n2. Testing Gene Contribution Analysis...")
    gene_contrib_data = {
        'loadings': quick_result['data']['results']['loadings'],
        'feature_names': feature_names,
        'n_top_genes': 5,
        'pc_index': 0
    }
    
    gene_contrib_resp = requests.post(
        f"{BASE_URL}/api/v1/pca-analysis/gene-contribution/",
        headers=headers,
        json=gene_contrib_data
    )
    
    if gene_contrib_resp.status_code != 200:
        print(f"Gene contribution failed: {gene_contrib_resp.text}")
        return False
    
    print("Success! Gene contribution results:")
    contrib_result = gene_contrib_resp.json()
    print(f"- Top genes: {contrib_result['data']['results']['top_genes']}")
    print(f"- Contributions: {[f'{v:.2f}' for v in contrib_result['data']['results']['contributions']]}")
    
    # Test PCA Simulation
    print("\n3. Testing PCA Educational Simulation...")
    simulation_resp = requests.get(
        f"{BASE_URL}/api/v1/pca-analysis/simulation/",
        headers=headers
    )
    
    if simulation_resp.status_code != 200:
        print(f"PCA simulation failed: {simulation_resp.text}")
        return False
    
    print("Success! PCA simulation generated")
    sim_result = simulation_resp.json()
    print(f"- Animation created: {'animation' in sim_result['data']['simulation']}")
    print(f"- Educational steps: {len(sim_result['data']['simulation']['explanation']['steps'])}")
    
    # Test Demo Data
    print("\n4. Testing Demo Data Generation...")
    
    # Get available demos
    demo_list_resp = requests.get(
        f"{BASE_URL}/api/v1/pca-analysis/demo/",
        headers=headers
    )
    
    if demo_list_resp.status_code != 200:
        print(f"Demo list failed: {demo_list_resp.text}")
        return False
    
    print("Available demos:", list(demo_list_resp.json()['data']['demos'].keys()))
    
    # Generate gene expression demo
    demo_data = {'demo_type': 'gene_expression'}
    demo_gen_resp = requests.post(
        f"{BASE_URL}/api/v1/pca-analysis/demo/",
        headers=headers,
        json=demo_data
    )
    
    if demo_gen_resp.status_code != 200:
        print(f"Demo generation failed: {demo_gen_resp.text}")
        return False
    
    print("Success! Generated demo dataset")
    demo_result = demo_gen_resp.json()
    print(f"- Samples: {len(demo_result['data']['metadata']['sample_names'])}")
    print(f"- Features: {len(demo_result['data']['metadata'].get('gene_names', []))}")
    
    print("\nSimplified PCA API tests completed successfully!")
    return True


if __name__ == "__main__":
    # Make sure we have a test user
    if not ensure_user_exists():
        sys.exit(1)

    # Run the tests
    success = test_pca_analysis()
    if success:
        success = test_pca_simplified_api()
    
    if not success:
        sys.exit(1)
    
    print("\n✅ All PCA tests passed!")