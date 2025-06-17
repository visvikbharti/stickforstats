import unittest
from unittest.mock import patch, MagicMock
import os
import json
import pandas as pd
import tempfile
import shutil
from pathlib import Path
from django.test import TestCase
from django.conf import settings

from stickforstats.core.services.workflow.workflow_service import WorkflowService

class TestWorkflowService(TestCase):
    """Test cases for the WorkflowService."""
    
    def setUp(self):
        """Set up test data."""
        # Use a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.workflow_service = WorkflowService(storage_dir=self.temp_dir)
        
        self.test_username = "test_user"
        self.test_data = pd.DataFrame({
            'A': [1, 2, 3],
            'B': [4, 5, 6]
        })
        self.test_workflow_state = {
            'name': 'Test Workflow',
            'description': 'A test workflow',
            'type': 'test_type',
            'status': 'created'
        }
        
    def tearDown(self):
        """Clean up test data."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_create_workflow(self):
        """Test creating a new workflow."""
        # Create workflow
        result = self.workflow_service.create_workflow(
            name='Test Workflow',
            description='A test workflow',
            workflow_type='test_type',
            username=self.test_username
        )
        
        # Verify result
        self.assertIn('id', result)
        self.assertEqual(result['name'], 'Test Workflow')
        self.assertEqual(result['description'], 'A test workflow')
        self.assertEqual(result['type'], 'test_type')
        self.assertEqual(result['status'], 'created')
        self.assertEqual(result['version'], 1)
        self.assertEqual(result['username'], self.test_username)
        
        # Verify workflow was saved
        workflow_id = result['id']
        workflow_path = os.path.join(self.temp_dir, self.test_username, workflow_id, 'state.json')
        self.assertTrue(os.path.exists(workflow_path))
        
        # Read saved workflow
        with open(workflow_path, 'r') as f:
            saved_workflow = json.load(f)
            
        self.assertEqual(saved_workflow['name'], 'Test Workflow')
    
    def test_save_and_load_workflow_state(self):
        """Test saving and loading workflow state."""
        # Create unique workflow ID
        workflow_id = 'test-workflow-id'
        
        # Save workflow state
        result = self.workflow_service.save_workflow_state(
            workflow_id=workflow_id,
            state=self.test_workflow_state,
            data=self.test_data,
            username=self.test_username
        )
        self.assertTrue(result)
        
        # Verify files were created
        workflow_path = os.path.join(self.temp_dir, self.test_username, workflow_id)
        state_file = os.path.join(workflow_path, 'state.json')
        data_file = os.path.join(workflow_path, 'data.csv')
        
        self.assertTrue(os.path.exists(state_file))
        self.assertTrue(os.path.exists(data_file))
        
        # Load workflow state
        loaded_state, loaded_data = self.workflow_service.load_workflow_state(
            workflow_id=workflow_id,
            username=self.test_username
        )
        
        # Verify loaded state
        self.assertEqual(loaded_state['name'], self.test_workflow_state['name'])
        self.assertEqual(loaded_state['description'], self.test_workflow_state['description'])
        
        # Verify loaded data
        pd.testing.assert_frame_equal(loaded_data, self.test_data)
        
        # Test loading non-existent workflow
        loaded_state, loaded_data = self.workflow_service.load_workflow_state(
            workflow_id='non-existent-id',
            username=self.test_username
        )
        self.assertIsNone(loaded_state)
        self.assertIsNone(loaded_data)
    
    def test_list_workflows(self):
        """Test listing workflows."""
        # Create multiple workflows
        workflow1 = self.workflow_service.create_workflow(
            name='Workflow 1',
            description='First workflow',
            workflow_type='test_type',
            username=self.test_username
        )
        
        workflow2 = self.workflow_service.create_workflow(
            name='Workflow 2',
            description='Second workflow',
            workflow_type='other_type',
            username=self.test_username
        )
        
        # List all workflows
        workflows = self.workflow_service.list_workflows(username=self.test_username)
        
        # Verify list contains both workflows
        self.assertEqual(len(workflows), 2)
        self.assertTrue(any(w['name'] == 'Workflow 1' for w in workflows))
        self.assertTrue(any(w['name'] == 'Workflow 2' for w in workflows))
        
        # List workflows with type filter
        filtered_workflows = self.workflow_service.list_workflows(
            username=self.test_username,
            workflow_type='test_type'
        )
        
        # Verify filtered list contains only one workflow
        self.assertEqual(len(filtered_workflows), 1)
        self.assertEqual(filtered_workflows[0]['name'], 'Workflow 1')
    
    def test_delete_workflow(self):
        """Test deleting a workflow."""
        # Create workflow
        workflow = self.workflow_service.create_workflow(
            name='Test Workflow',
            description='A test workflow',
            workflow_type='test_type',
            username=self.test_username
        )
        workflow_id = workflow['id']
        
        # Verify workflow exists
        workflow_path = os.path.join(self.temp_dir, self.test_username, workflow_id)
        self.assertTrue(os.path.exists(workflow_path))
        
        # Delete workflow
        result = self.workflow_service.delete_workflow(workflow_id, self.test_username)
        self.assertTrue(result)
        
        # Verify workflow was deleted
        self.assertFalse(os.path.exists(workflow_path))
        
        # Test deleting non-existent workflow
        result = self.workflow_service.delete_workflow('non-existent-id', self.test_username)
        self.assertFalse(result)
    
    def test_update_workflow_state(self):
        """Test updating workflow state."""
        # Create workflow
        workflow = self.workflow_service.create_workflow(
            name='Test Workflow',
            description='A test workflow',
            workflow_type='test_type',
            username=self.test_username
        )
        workflow_id = workflow['id']
        
        # Update workflow state
        updates = {
            'name': 'Updated Name',
            'status': 'in_progress',
            'metadata': {'key': 'value'}
        }
        result = self.workflow_service.update_workflow_state(
            workflow_id=workflow_id,
            state_updates=updates,
            username=self.test_username
        )
        
        # Verify result
        self.assertEqual(result['name'], 'Updated Name')
        self.assertEqual(result['status'], 'in_progress')
        self.assertEqual(result['metadata'], {'key': 'value'})
        
        # Verify state was saved
        loaded_state, _ = self.workflow_service.load_workflow_state(
            workflow_id=workflow_id,
            username=self.test_username
        )
        self.assertEqual(loaded_state['name'], 'Updated Name')
        
        # Test updating non-existent workflow
        result = self.workflow_service.update_workflow_state(
            workflow_id='non-existent-id',
            state_updates=updates,
            username=self.test_username
        )
        self.assertIn('error', result)
    
    def test_add_workflow_step(self):
        """Test adding a step to a workflow."""
        # Create workflow
        workflow = self.workflow_service.create_workflow(
            name='Test Workflow',
            description='A test workflow',
            workflow_type='test_type',
            username=self.test_username
        )
        workflow_id = workflow['id']
        
        # Add step
        step_data = {
            'name': 'Test Step',
            'description': 'A test step',
            'parameters': {'param1': 'value1'}
        }
        result = self.workflow_service.add_workflow_step(
            workflow_id=workflow_id,
            step_data=step_data,
            username=self.test_username
        )
        
        # Verify result
        self.assertEqual(len(result['steps']), 1)
        self.assertEqual(result['steps'][0]['name'], 'Test Step')
        self.assertEqual(result['steps'][0]['status'], 'pending')
        
        # Verify workflow status was updated
        self.assertEqual(result['status'], 'in_progress')
        
        # Add another step
        step_data2 = {
            'name': 'Test Step 2',
            'description': 'A second test step'
        }
        result = self.workflow_service.add_workflow_step(
            workflow_id=workflow_id,
            step_data=step_data2,
            username=self.test_username
        )
        
        # Verify second step was added
        self.assertEqual(len(result['steps']), 2)
        
        # Test adding step to non-existent workflow
        result = self.workflow_service.add_workflow_step(
            workflow_id='non-existent-id',
            step_data=step_data,
            username=self.test_username
        )
        self.assertIn('error', result)
    
    def test_update_workflow_step(self):
        """Test updating a workflow step."""
        # Create workflow with a step
        workflow = self.workflow_service.create_workflow(
            name='Test Workflow',
            description='A test workflow',
            workflow_type='test_type',
            username=self.test_username
        )
        workflow_id = workflow['id']
        
        # Add step
        step_data = {
            'name': 'Test Step',
            'description': 'A test step'
        }
        workflow = self.workflow_service.add_workflow_step(
            workflow_id=workflow_id,
            step_data=step_data,
            username=self.test_username
        )
        step_id = workflow['steps'][0]['id']
        
        # Update step
        step_updates = {
            'status': 'completed',
            'results': {'metric': 0.95}
        }
        result = self.workflow_service.update_workflow_step(
            workflow_id=workflow_id,
            step_id=step_id,
            step_updates=step_updates,
            username=self.test_username
        )
        
        # Verify result
        self.assertEqual(result['steps'][0]['status'], 'completed')
        self.assertEqual(result['steps'][0]['results'], {'metric': 0.95})
        
        # Verify workflow status was updated when all steps are completed
        self.assertEqual(result['status'], 'completed')
        
        # Test updating step in non-existent workflow
        result = self.workflow_service.update_workflow_step(
            workflow_id='non-existent-id',
            step_id=step_id,
            step_updates=step_updates,
            username=self.test_username
        )
        self.assertIn('error', result)
        
        # Test updating non-existent step
        result = self.workflow_service.update_workflow_step(
            workflow_id=workflow_id,
            step_id='non-existent-id',
            step_updates=step_updates,
            username=self.test_username
        )
        self.assertIn('error', result)
    
    def test_export_import_workflow(self):
        """Test exporting and importing a workflow."""
        # Create workflow with data
        workflow = self.workflow_service.create_workflow(
            name='Test Workflow',
            description='A test workflow',
            workflow_type='test_type',
            username=self.test_username
        )
        workflow_id = workflow['id']
        
        # Save workflow state with data
        self.workflow_service.save_workflow_state(
            workflow_id=workflow_id,
            state=workflow,
            data=self.test_data,
            username=self.test_username
        )
        
        # Export workflow
        export_data = self.workflow_service.export_workflow(
            workflow_id=workflow_id,
            username=self.test_username,
            include_data=True
        )
        
        # Verify export data
        self.assertIn('workflow', export_data)
        self.assertEqual(export_data['workflow']['name'], 'Test Workflow')
        self.assertIn('data', export_data)
        
        # Import workflow
        import_result = self.workflow_service.import_workflow(
            workflow_data=export_data,
            username='another_user'
        )
        
        # Verify imported workflow
        self.assertNotEqual(import_result['id'], workflow_id)  # New ID
        self.assertEqual(import_result['name'], 'Test Workflow')
        self.assertEqual(import_result['imported_from'], workflow_id)
        
        # Load imported workflow data
        loaded_state, loaded_data = self.workflow_service.load_workflow_state(
            workflow_id=import_result['id'],
            username='another_user'
        )
        
        # Verify imported data
        self.assertEqual(loaded_state['name'], 'Test Workflow')
        pd.testing.assert_frame_equal(loaded_data, self.test_data)