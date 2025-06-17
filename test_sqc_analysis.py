"""
Test script for SQC Analysis API.

This script tests the SQC Analysis API endpoints and functionality.
"""

import os
import sys
import uuid
import requests
import unittest
from unittest.mock import patch, MagicMock
import json
import time
from pprint import pprint

# API base URL
BASE_URL = "http://localhost:8000"
headers = {}

def authenticate():
    """Authenticate and get token."""
    print("\nAuthenticating...")
    
    auth_data = {
        "username": "admin",
        "password": "admin"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/core/auth/token/", json=auth_data)
        if response.status_code == 200:
            token = response.json().get("token")
            global headers
            headers = {"Authorization": f"Token {token}"}
            print("Authentication successful!")
            return True
        else:
            print(f"Authentication failed: {response.text}")
            return False
    except Exception as e:
        print(f"Error during authentication: {str(e)}")
        return False

def upload_test_dataset():
    """Upload a test dataset for SQC analysis."""
    print("\nUploading test dataset...")
    
    # Create a simple test CSV for control chart analysis
    csv_content = """Batch,Measurement
1,10.2
1,10.3
1,10.5
1,10.1
1,10.4
2,10.7
2,10.6
2,10.9
2,10.5
2,10.8
3,10.3
3,10.2
3,10.4
3,10.3
3,10.5
4,10.6
4,10.5
4,10.7
4,10.4
4,10.8
5,11.0
5,11.2
5,11.3
5,10.9
5,11.1
"""
    
    # Create a temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp:
        temp.write(csv_content.encode('utf-8'))
        temp_path = temp.name
    
    # Upload the file
    try:
        with open(temp_path, 'rb') as f:
            files = {'file': f}
            data = {
                'name': 'SQC Test Dataset',
                'description': 'Test dataset for SQC analysis',
                'file_type': 'csv'
            }
            
            response = requests.post(
                f"{BASE_URL}/api/v1/core/datasets/", 
                headers=headers,
                data=data,
                files=files
            )
            
            if response.status_code == 201:
                dataset = response.json()
                print(f"Dataset uploaded: {dataset['name']} (ID: {dataset['id']})")
                return dataset['id']
            else:
                print(f"Failed to upload dataset: {response.text}")
                return None
    except Exception as e:
        print(f"Error uploading dataset: {str(e)}")
        return None
    finally:
        # Remove temporary file
        os.remove(temp_path)

def create_control_chart():
    """Create a control chart analysis."""
    print("\nCreating control chart analysis...")
    
    # Get dataset ID
    dataset_id = upload_test_dataset()
    if not dataset_id:
        print("Cannot create control chart without dataset.")
        return None
    
    # Create control chart request
    chart_data = {
        "dataset_id": dataset_id,
        "chart_type": "xbar_r",
        "parameter_column": "Measurement",
        "grouping_column": "Batch",
        "sample_size": 5,
        "detect_rules": True,
        "rule_set": "western_electric",
        "session_name": "Test Control Chart Analysis"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/sqc-analysis/control-charts/", 
            headers=headers,
            json=chart_data
        )
        
        if response.status_code == 201:
            chart = response.json()
            print(f"Control chart created: {chart['chart_type']} Chart (ID: {chart['id']})")
            return chart['id']
        else:
            print(f"Failed to create control chart: {response.text}")
            return None
    except Exception as e:
        print(f"Error creating control chart: {str(e)}")
        return None

def create_process_capability():
    """Create a process capability analysis."""
    print("\nCreating process capability analysis...")
    
    # Get dataset ID
    dataset_id = upload_test_dataset()
    if not dataset_id:
        print("Cannot create process capability analysis without dataset.")
        return None
    
    # Create process capability request
    capability_data = {
        "dataset_id": dataset_id,
        "parameter_column": "Measurement",
        "lower_spec_limit": 9.5,
        "upper_spec_limit": 11.5,
        "target_value": 10.5,
        "assume_normality": True,
        "transformation_method": "none",
        "session_name": "Test Process Capability Analysis"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/sqc-analysis/process-capability/", 
            headers=headers,
            json=capability_data
        )
        
        if response.status_code == 201:
            capability = response.json()
            print(f"Process capability analysis created (ID: {capability['id']})")
            # Print key capability indices
            print(f"Cp: {capability.get('cp')}, Cpk: {capability.get('cpk')}")
            print(f"Pp: {capability.get('pp')}, Ppk: {capability.get('ppk')}")
            print(f"Process yield: {capability.get('process_yield')}%")
            return capability['id']
        else:
            print(f"Failed to create process capability analysis: {response.text}")
            return None
    except Exception as e:
        print(f"Error creating process capability analysis: {str(e)}")
        return None

def create_acceptance_sampling_plan():
    """Create an acceptance sampling plan."""
    print("\nCreating acceptance sampling plan...")
    
    # Create sampling plan request
    plan_data = {
        "plan_type": "single",
        "lot_size": 1000,
        "aql": 1.0,
        "ltpd": 10.0,
        "producer_risk": 0.05,
        "consumer_risk": 0.10,
        "session_name": "Test Acceptance Sampling Plan"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/sqc-analysis/acceptance-sampling/", 
            headers=headers,
            json=plan_data
        )
        
        if response.status_code == 201:
            plan = response.json()
            print(f"Acceptance sampling plan created (ID: {plan['id']})")
            # Print key plan parameters
            print(f"Sample size: {plan.get('sample_size')}")
            print(f"Acceptance number: {plan.get('acceptance_number')}")
            return plan['id']
        else:
            print(f"Failed to create acceptance sampling plan: {response.text}")
            return None
    except Exception as e:
        print(f"Error creating acceptance sampling plan: {str(e)}")
        return None

def create_economic_design():
    """Create an economic design analysis for control charts."""
    print("\nCreating economic design analysis...")
    
    # Create economic design request
    design_data = {
        "chart_type": "xbar",
        "mean_time_to_failure": 200,
        "shift_size": 1.5,
        "std_dev": 1.0,
        "hourly_production": 500,
        "sampling_cost": 3.0,
        "fixed_sampling_cost": 10.0,
        "false_alarm_cost": 150.0,
        "hourly_defect_cost": 400.0,
        "finding_cost": 200.0,
        "min_sample_size": 2,
        "max_sample_size": 10,
        "min_sampling_interval": 0.5,
        "max_sampling_interval": 6.0,
        "session_name": "Test Economic Design Analysis"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/sqc-analysis/economic-design/", 
            headers=headers,
            json=design_data
        )
        
        if response.status_code == 201:
            design = response.json()
            print(f"Economic design analysis created (ID: {design['id']})")
            # Print optimal design parameters
            print(f"Optimal sample size: {design.get('sample_size')}")
            print(f"Optimal sampling interval: {design.get('sampling_interval')} hours")
            print(f"Optimal k factor: {design.get('k_factor')}")
            print(f"Hourly cost: ${design.get('hourly_cost')}")
            return design['id']
        else:
            print(f"Failed to create economic design analysis: {response.text}")
            return None
    except Exception as e:
        print(f"Error creating economic design analysis: {str(e)}")
        return None

def create_spc_implementation_plan():
    """Create an SPC implementation plan."""
    print("\nCreating SPC implementation plan...")
    
    # Create implementation plan request
    plan_data = {
        "plan_type": "roadmap",
        "industry": "manufacturing",
        "organization_size": "medium",
        "implementation_scope": "department",
        "existing_quality_system": "basic",
        "process_complexity": "medium",
        "session_name": "Test SPC Implementation Plan"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/sqc-analysis/spc-implementation/", 
            headers=headers,
            json=plan_data
        )
        
        if response.status_code == 201:
            plan = response.json()
            print(f"SPC implementation plan created (ID: {plan['id']})")
            return plan['id']
        else:
            print(f"Failed to create SPC implementation plan: {response.text}")
            return None
    except Exception as e:
        print(f"Error creating SPC implementation plan: {str(e)}")
        return None

def run_tests():
    """Run all tests for SQC Analysis API."""
    print("\n===== Testing SQC Analysis API =====\n")
    
    # Authenticate
    if not authenticate():
        print("Authentication failed. Aborting tests.")
        return
    
    # Run tests
    control_chart_id = create_control_chart()
    
    process_capability_id = create_process_capability()
    
    acceptance_sampling_id = create_acceptance_sampling_plan()
    
    economic_design_id = create_economic_design()
    
    implementation_plan_id = create_spc_implementation_plan()
    
    # Summary
    print("\n===== Test Summary =====")
    print(f"Control Chart Analysis: {'✓' if control_chart_id else '✗'}")
    print(f"Process Capability Analysis: {'✓' if process_capability_id else '✗'}")
    print(f"Acceptance Sampling Plan: {'✓' if acceptance_sampling_id else '✗'}")
    print(f"Economic Design Analysis: {'✓' if economic_design_id else '✗'}")
    print(f"SPC Implementation Plan: {'✓' if implementation_plan_id else '✗'}")

if __name__ == "__main__":
    run_tests()