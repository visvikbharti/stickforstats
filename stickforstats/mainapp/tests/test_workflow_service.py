import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import uuid
from datetime import datetime

from django.test import TestCase
from django.contrib.auth import get_user_model

from stickforstats.mainapp.services.workflow.workflow_service import WorkflowService
from stickforstats.mainapp.models.workflow import Workflow, WorkflowStep, WorkflowExecution

User = get_user_model()


class WorkflowServiceTestCase(TestCase):
    """
    Test cases for the WorkflowService.
    """
    
    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.test_user = User.objects.create_user(
            username='workflowuser',
            email='workflow@example.com',
            password='workflowpass'
        )
        
        # Initialize the service
        self.workflow_service = WorkflowService()
        
        # Create a test workflow
        self.test_workflow = Workflow.objects.create(
            id=uuid.uuid4(),
            user=self.test_user,
            name="Test Workflow",
            description="Test workflow description",
            status="draft"
        )
        
        # Create test workflow steps
        self.test_steps = [
            WorkflowStep.objects.create(
                id=uuid.uuid4(),
                workflow=self.test_workflow,
                name="Data Loading Step",
                description="Step for loading data",
                step_type="data_load",
                parameters=json.dumps({
                    "source": "file",
                    "file_path": "test/data.csv"
                }),
                order=0,
                status="pending"
            ),
            WorkflowStep.objects.create(
                id=uuid.uuid4(),
                workflow=self.test_workflow,
                name="Data Transformation",
                description="Step for transforming data",
                step_type="data_transform",
                parameters=json.dumps({
                    "operations": [
                        {"type": "filter", "column": "col1", "expression": "col1 > 10"}
                    ]
                }),
                order=1,
                status="pending",
                depends_on=[str(step.id) for step in WorkflowStep.objects.filter(workflow=self.test_workflow, order=0)]
            ),
            WorkflowStep.objects.create(
                id=uuid.uuid4(),
                workflow=self.test_workflow,
                name="Statistical Analysis",
                description="Step for statistical analysis",
                step_type="statistical_analysis",
                parameters=json.dumps({
                    "analysis_type": "descriptive",
                    "parameters": {
                        "variables": ["col1", "col2"]
                    }
                }),
                order=2,
                status="pending",
                depends_on=[str(step.id) for step in WorkflowStep.objects.filter(workflow=self.test_workflow, order=1)]
            )
        ]
    
    def test_get_workflow(self):
        """Test retrieving a workflow."""
        # Get the workflow
        workflow = self.workflow_service.get_workflow(str(self.test_workflow.id))
        
        # Verify the workflow
        self.assertEqual(workflow.id, self.test_workflow.id)
        self.assertEqual(workflow.name, "Test Workflow")
        self.assertEqual(workflow.status, "draft")
    
    def test_get_workflow_steps(self):
        """Test retrieving workflow steps."""
        # Get the workflow steps
        steps = self.workflow_service.get_workflow_steps(str(self.test_workflow.id))
        
        # Verify the steps
        self.assertEqual(len(steps), 3)
        self.assertEqual(steps[0].name, "Data Loading Step")
        self.assertEqual(steps[1].name, "Data Transformation")
        self.assertEqual(steps[2].name, "Statistical Analysis")
        
        # Verify the order
        self.assertEqual(steps[0].order, 0)
        self.assertEqual(steps[1].order, 1)
        self.assertEqual(steps[2].order, 2)
    
    def test_create_workflow(self):
        """Test creating a new workflow."""
        # Create a new workflow
        workflow_data = {
            "name": "New Test Workflow",
            "description": "New workflow description",
            "status": "draft"
        }
        
        workflow = self.workflow_service.create_workflow(self.test_user, workflow_data)
        
        # Verify the workflow
        self.assertEqual(workflow.name, "New Test Workflow")
        self.assertEqual(workflow.description, "New workflow description")
        self.assertEqual(workflow.status, "draft")
        self.assertEqual(workflow.user, self.test_user)
    
    def test_update_workflow(self):
        """Test updating a workflow."""
        # Update the workflow
        workflow_data = {
            "name": "Updated Workflow",
            "description": "Updated description",
            "status": "active"
        }
        
        updated_workflow = self.workflow_service.update_workflow(
            str(self.test_workflow.id),
            self.test_user,
            workflow_data
        )
        
        # Verify the updated workflow
        self.assertEqual(updated_workflow.name, "Updated Workflow")
        self.assertEqual(updated_workflow.description, "Updated description")
        self.assertEqual(updated_workflow.status, "active")
    
    def test_delete_workflow(self):
        """Test deleting a workflow."""
        # Delete the workflow
        self.workflow_service.delete_workflow(str(self.test_workflow.id), self.test_user)
        
        # Verify the workflow is deleted
        with self.assertRaises(Workflow.DoesNotExist):
            Workflow.objects.get(id=self.test_workflow.id)
    
    def test_create_workflow_step(self):
        """Test creating a workflow step."""
        # Create a step
        step_data = {
            "name": "New Step",
            "description": "New step description",
            "step_type": "visualization",
            "parameters": {
                "viz_type": "scatter",
                "parameters": {
                    "x": "col1",
                    "y": "col2"
                }
            },
            "order": 3,
            "depends_on": [str(self.test_steps[2].id)]
        }
        
        step = self.workflow_service.create_workflow_step(
            str(self.test_workflow.id),
            self.test_user,
            step_data
        )
        
        # Verify the step
        self.assertEqual(step.name, "New Step")
        self.assertEqual(step.step_type, "visualization")
        self.assertEqual(step.order, 3)
        self.assertEqual(step.depends_on, [str(self.test_steps[2].id)])
        
        # Verify parameters
        parameters = json.loads(step.parameters)
        self.assertEqual(parameters["viz_type"], "scatter")
        self.assertEqual(parameters["parameters"]["x"], "col1")
        self.assertEqual(parameters["parameters"]["y"], "col2")
    
    @patch('stickforstats.mainapp.services.workflow.workflow_execution_service.WorkflowExecutionService.execute_workflow')
    def test_execute_workflow(self, mock_execute):
        """Test executing a workflow."""
        # Mock the execution result
        mock_result = {
            "execution_id": str(uuid.uuid4()),
            "status": "in_progress",
            "started_at": datetime.now().isoformat(),
            "steps": [
                {"id": str(self.test_steps[0].id), "status": "queued"},
                {"id": str(self.test_steps[1].id), "status": "pending"},
                {"id": str(self.test_steps[2].id), "status": "pending"}
            ]
        }
        mock_execute.return_value = mock_result
        
        # Execute the workflow
        result = self.workflow_service.execute_workflow(
            str(self.test_workflow.id),
            self.test_user
        )
        
        # Verify the result
        self.assertEqual(result["status"], "in_progress")
        self.assertEqual(len(result["steps"]), 3)
        self.assertEqual(result["steps"][0]["status"], "queued")
        
        # Verify the execution service was called
        mock_execute.assert_called_once_with(
            str(self.test_workflow.id),
            self.test_user,
            None
        )
    
    def test_get_execution_status(self):
        """Test getting execution status."""
        # Create a mock execution
        execution = WorkflowExecution.objects.create(
            id=uuid.uuid4(),
            workflow=self.test_workflow,
            status="in_progress",
            started_at=datetime.now(),
            current_step=self.test_steps[0],
            current_step_index=0,
            result=json.dumps({
                "steps": [
                    {"id": str(self.test_steps[0].id), "status": "running"},
                    {"id": str(self.test_steps[1].id), "status": "pending"},
                    {"id": str(self.test_steps[2].id), "status": "pending"}
                ]
            })
        )
        
        # Get the execution status
        status = self.workflow_service.get_execution_status(str(self.test_workflow.id))
        
        # Verify the status
        self.assertEqual(status["status"], "in_progress")
        self.assertEqual(status["current_step_index"], 0)
        self.assertEqual(status["current_step_name"], self.test_steps[0].name)
        
        # Verify steps
        steps = json.loads(status["result"])["steps"]
        self.assertEqual(len(steps), 3)
        self.assertEqual(steps[0]["status"], "running")
        self.assertEqual(steps[1]["status"], "pending")
        self.assertEqual(steps[2]["status"], "pending")
    
    def test_cancel_execution(self):
        """Test cancelling a workflow execution."""
        # Create a mock execution
        execution = WorkflowExecution.objects.create(
            id=uuid.uuid4(),
            workflow=self.test_workflow,
            status="in_progress",
            started_at=datetime.now(),
            current_step=self.test_steps[0],
            current_step_index=0,
            result=json.dumps({
                "steps": [
                    {"id": str(self.test_steps[0].id), "status": "running"},
                    {"id": str(self.test_steps[1].id), "status": "pending"},
                    {"id": str(self.test_steps[2].id), "status": "pending"}
                ]
            })
        )
        
        # Cancel the execution
        result = self.workflow_service.cancel_execution(str(self.test_workflow.id), self.test_user)
        
        # Verify the result
        self.assertEqual(result["status"], "cancelled")
        
        # Verify the execution is cancelled
        updated_execution = WorkflowExecution.objects.get(id=execution.id)
        self.assertEqual(updated_execution.status, "cancelled")


if __name__ == '__main__':
    unittest.main()