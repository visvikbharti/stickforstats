"""
Test script for Probability Distributions module
"""

import os
import django
import json
import pandas as pd

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stickforstats.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

User = get_user_model()

# Get or create a test user
try:
    user = User.objects.get(username='apitest')
except User.DoesNotExist:
    user = User.objects.create_user(
        username='apitest',
        email='apitest@example.com',
        password='testpass123'
    )
    print(f"Created user: {user.username}")

# Get or create token
token, created = Token.objects.get_or_create(user=user)
print(f"Using token: {token.key}")

# Create API client
client = APIClient()
client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

print("\n" + "="*50)
print("Testing Probability Distributions Module")
print("="*50)

# Test 1: Get distribution examples
print("\n1. Testing Get Distribution Examples...")
response = client.get('/api/v1/probability-distributions/examples/')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Available distributions: {data['data']['total_distributions']}")
    print(f"Categories: {data['data']['categories']}")
else:
    print(f"Error: {response.json()}")

# Test 2: Create a Normal distribution
print("\n2. Testing Create Normal Distribution...")
response = client.post('/api/v1/probability-distributions/create/', {
    'distribution_type': 'NORMAL',
    'parameters': {
        'mu': 100,
        'sigma': 15
    },
    'generate_visualization': True
}, format='json')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    stats = data['data']['distribution']['statistics']
    print(f"Mean: {stats['mean']}")
    print(f"Std Dev: {stats['standard_deviation']}")
    print(f"Visualization generated: {'visualization' in data['data']}")
else:
    print(f"Error: {response.json()}")

# Test 3: Calculate PMF for Binomial
print("\n3. Testing Calculate PMF for Binomial...")
response = client.post('/api/v1/probability-distributions/calculate/', {
    'distribution_type': 'BINOMIAL',
    'parameters': {
        'n': 10,
        'p': 0.3
    },
    'calculation_type': 'pmf',
    'x_values': [0, 1, 2, 3, 4, 5],
    'generate_visualization': True
}, format='json')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    pmf_values = data['data']['result']['pmf_values']
    print(f"PMF values: {[round(v, 4) for v in pmf_values[:5]]}")
else:
    print(f"Error: {response.json()}")

# Test 4: Generate Random Samples
print("\n4. Testing Generate Random Samples...")
response = client.post('/api/v1/probability-distributions/sample/', {
    'distribution_type': 'EXPONENTIAL',
    'parameters': {
        'rate': 0.5
    },
    'sample_size': 100
}, format='json')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    summary = data['data']['samples']['summary']
    print(f"Sample mean: {round(summary['mean'], 2)}")
    print(f"Sample std: {round(summary['std_dev'], 2)}")
    print(f"Sample size: {len(data['data']['samples']['samples'])}")
else:
    print(f"Error: {response.json()}")

# Test 5: Fit Distribution to Data
print("\n5. Testing Fit Distribution to Data...")
# Load example data
df = pd.read_csv('example_data/probability_distributions/student_test_scores_normal.csv')
response = client.post('/api/v1/probability-distributions/fit/', {
    'data': df['test_score'].tolist()[:100],  # Use first 100 values
    'distribution_type': 'NORMAL'
}, format='json')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    fitted_params = data['data']['fit_result']['fitted_parameters']
    gof = data['data']['fit_result']['goodness_of_fit']
    print(f"Fitted parameters: μ={round(fitted_params['mu'], 2)}, σ={round(fitted_params['sigma'], 2)}")
    print(f"KS test p-value: {round(gof['ks_p_value'], 4)}")
else:
    print(f"Error: {response.json()}")

# Test 6: Compare Binomial Approximations
print("\n6. Testing Compare Binomial Approximations...")
response = client.post('/api/v1/probability-distributions/approximations/', {
    'n': 100,
    'p': 0.03,
    'approximation_types': ['POISSON', 'NORMAL']
}, format='json')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    comparison = data['data']['comparison']
    print(f"n*p = {comparison['parameters']['np']}")
    print(f"Better approximation: {comparison.get('better_approximation', 'N/A')}")
    if 'POISSON' in comparison['errors']:
        print(f"Poisson max error: {round(comparison['errors']['POISSON']['max_error'], 4)}")
    if 'NORMAL' in comparison['errors']:
        print(f"Normal max error: {round(comparison['errors']['NORMAL']['max_error'], 4)}")
else:
    print(f"Error: {response.json()}")

# Test 7: Process Capability Analysis
print("\n7. Testing Process Capability Analysis...")
response = client.post('/api/v1/probability-distributions/process-capability/', {
    'mean': 10.02,
    'std_dev': 0.15,
    'lsl': 9.5,
    'usl': 10.5
}, format='json')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    capability = data['data']['capability']
    indices = capability['capability_indices']
    defects = capability['defect_rates']
    print(f"Cp = {round(indices['cp'], 3)}")
    print(f"Cpk = {round(indices['cpk'], 3)}")
    print(f"Defect PPM = {round(defects['ppm'], 0)}")
else:
    print(f"Error: {response.json()}")

# Test 8: Simulate Poisson Process
print("\n8. Testing Simulate Poisson Process...")
response = client.post('/api/v1/probability-distributions/poisson-process/', {
    'rate': 2.5,
    'duration': 10,
    'num_simulations': 5
}, format='json')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    simulation = data['data']['simulation']
    print(f"Expected events: {simulation['parameters']['expected_events']}")
    print(f"Event counts in simulations: {simulation['event_counts']}")
else:
    print(f"Error: {response.json()}")

# Test 9: Calculate Probability
print("\n9. Testing Calculate Probability...")
response = client.post('/api/v1/probability-distributions/calculate/', {
    'distribution_type': 'NORMAL',
    'parameters': {
        'mu': 0,
        'sigma': 1
    },
    'calculation_type': 'probability',
    'probability_type': 'BETWEEN',
    'values': {
        'x1': -1,
        'x2': 1
    }
}, format='json')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    prob = data['data']['result']['probability']
    print(f"P(-1 < X < 1) = {round(prob, 4)} (should be ~0.6827)")
else:
    print(f"Error: {response.json()}")

print("\n" + "="*50)
print("Probability Distributions Module Testing Complete!")
print("="*50)