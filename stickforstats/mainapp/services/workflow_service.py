"""
Workflow management service for the StickForStats application.

This module provides services for managing analysis workflows, adapted 
from the original Streamlit-based workflow_manager.py.
"""
import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, Union
import pandas as pd

from django.conf import settings
from django.db import transaction
from django.db.models import Q, Prefetch
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from stickforstats.mainapp.models import (
    User, AnalysisSession, Dataset, Workflow, WorkflowStep
)

# Configure logging
logger = logging.getLogger(__name__)


class WorkflowService:
    """
    Manages analysis workflows, including saving and loading states,
    handling data persistence, and workflow lifecycle management.
    """
    
    def __init__(self, base_storage_path: str = None):
        """
        Initialize the workflow service.
        
        Args:
            base_storage_path: Base path for storing files (defaults to settings.MEDIA_ROOT)
        """
        self.base_storage_path = base_storage_path or getattr(settings, 'MEDIA_ROOT', 'media')
        self._ensure_storage_directories()
    
    def _ensure_storage_directories(self) -> None:
        """Ensure required storage directories exist."""
        directories = [
            os.path.join(self.base_storage_path, "workflows"),
            os.path.join(self.base_storage_path, "workflow_templates"),
            os.path.join(self.base_storage_path, "workflow_exports")
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def create_workflow(self, 
                      user: User,
                      name: str, 
                      description: Optional[str] = None,
                      dataset: Optional[Dataset] = None,
                      initial_session: Optional[AnalysisSession] = None,
                      metadata: Optional[Dict[str, Any]] = None,
                      is_template: bool = False,
                      is_public: bool = False) -> Workflow:
        """
        Create a new workflow.
        
        Args:
            user: User who owns the workflow
            name: Workflow name
            description: Optional description
            dataset: Optional dataset to analyze
            initial_session: Optional initial analysis session
            metadata: Optional metadata
            is_template: Whether this is a reusable template
            is_public: Whether this workflow is public
            
        Returns:
            Created Workflow instance
        """
        try:
            workflow = Workflow.objects.create(
                user=user,
                name=name,
                description=description,
                dataset=dataset,
                initial_session=initial_session,
                metadata=metadata or {},
                status='draft',
                is_template=is_template,
                is_public=is_public
            )
            logger.info(f"Created workflow {workflow.id} for user {user.username}")
            return workflow
        except Exception as e:
            logger.error(f"Error creating workflow: {str(e)}")
            raise
    
    def add_workflow_step(self,
                        workflow: Workflow,
                        name: str,
                        step_type: str,
                        order: int,
                        configuration: Dict[str, Any],
                        description: Optional[str] = None,
                        analysis_session: Optional[AnalysisSession] = None,
                        depends_on: Optional[List[WorkflowStep]] = None,
                        is_required: bool = True,
                        timeout_seconds: int = 3600) -> WorkflowStep:
        """
        Add a step to a workflow.
        
        Args:
            workflow: Workflow to add step to
            name: Step name
            step_type: Type of analysis step
            order: Order of execution (lower numbers execute first)
            configuration: Step configuration parameters
            description: Optional step description
            analysis_session: Optional associated analysis session
            depends_on: Optional list of steps this step depends on
            is_required: Whether this step is required for workflow completion
            timeout_seconds: Maximum execution time in seconds
            
        Returns:
            Created WorkflowStep instance
        """
        try:
            with transaction.atomic():
                step = WorkflowStep.objects.create(
                    workflow=workflow,
                    name=name,
                    step_type=step_type,
                    order=order,
                    configuration=configuration,
                    description=description,
                    analysis_session=analysis_session,
                    is_required=is_required,
                    timeout_seconds=timeout_seconds,
                    execution_status='pending'
                )
                
                # Add dependencies if provided
                if depends_on:
                    step.depends_on.set(depends_on)
                
                logger.info(f"Added step {step.id} to workflow {workflow.id}")
                return step
        except Exception as e:
            logger.error(f"Error adding workflow step: {str(e)}")
            raise
    
    def get_workflow(self, workflow_id: Union[str, uuid.UUID]) -> Optional[Workflow]:
        """
        Retrieve a workflow by ID.
        
        Args:
            workflow_id: UUID of the workflow
            
        Returns:
            Workflow if found, None otherwise
        """
        try:
            return Workflow.objects.select_related(
                'user', 'dataset', 'initial_session'
            ).prefetch_related(
                'steps'
            ).get(id=workflow_id)
        except Workflow.DoesNotExist:
            logger.warning(f"Workflow {workflow_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error retrieving workflow {workflow_id}: {str(e)}")
            return None
    
    def list_workflows(self, 
                     user: Optional[User] = None,
                     include_public: bool = False,
                     include_templates: bool = False,
                     status: Optional[str] = None,
                     limit: int = 100) -> List[Workflow]:
        """
        List available workflows.
        
        Args:
            user: Optional user to filter by
            include_public: Whether to include public workflows
            include_templates: Whether to include template workflows
            status: Optional status filter
            limit: Maximum number of workflows to return
            
        Returns:
            List of Workflow instances
        """
        try:
            # Build base query
            query = Workflow.objects.all()
            
            # Apply user filter if provided
            if user:
                query = query.filter(
                    Q(user=user) | (Q(is_public=True) if include_public else Q())
                )
            elif not include_public:
                # If no user and not including public, show nothing
                return []
            
            # Apply template filter
            if not include_templates:
                query = query.filter(is_template=False)
            
            # Apply status filter if provided
            if status:
                query = query.filter(status=status)
            
            # Get workflows with related data
            return query.select_related(
                'user', 'dataset'
            ).prefetch_related(
                'steps'
            ).order_by('-created_at')[:limit]
            
        except Exception as e:
            logger.error(f"Error listing workflows: {str(e)}")
            return []
    
    def update_workflow_status(self, 
                             workflow: Workflow, 
                             status: str, 
                             save_completed_time: bool = True) -> bool:
        """
        Update workflow status.
        
        Args:
            workflow: Workflow to update
            status: New status
            save_completed_time: Whether to save completed time for 'completed' status
            
        Returns:
            True if successful, False otherwise
        """
        try:
            workflow.status = status
            
            if status == 'completed' and save_completed_time:
                workflow.completed_at = datetime.now()
            
            workflow.save(update_fields=['status', 'completed_at', 'updated_at'])
            logger.info(f"Updated workflow {workflow.id} status to {status}")
            return True
        except Exception as e:
            logger.error(f"Error updating workflow status: {str(e)}")
            return False
    
    def update_step_status(self,
                        step: WorkflowStep,
                        status: str,
                        update_timestamps: bool = True) -> bool:
        """
        Update workflow step status.
        
        Args:
            step: WorkflowStep to update
            status: New status
            update_timestamps: Whether to update timestamps
            
        Returns:
            True if successful, False otherwise
        """
        try:
            step.execution_status = status
            
            if update_timestamps:
                if status == 'in_progress' and not step.started_at:
                    step.started_at = datetime.now()
                elif status in ('completed', 'failed', 'skipped') and not step.completed_at:
                    step.completed_at = datetime.now()
            
            step.save()
            
            # Update overall workflow status if needed
            self._check_and_update_workflow_status(step.workflow)
            
            logger.info(f"Updated step {step.id} status to {status}")
            return True
        except Exception as e:
            logger.error(f"Error updating step status: {str(e)}")
            return False
    
    def _check_and_update_workflow_status(self, workflow: Workflow) -> None:
        """
        Check and update workflow status based on steps.
        
        Args:
            workflow: Workflow to check and update
        """
        try:
            # Get all steps
            steps = workflow.steps.all()
            
            if not steps:
                return
            
            # Count steps by status
            total_steps = len(steps)
            completed_steps = sum(1 for step in steps if step.execution_status == 'completed')
            failed_steps = sum(1 for step in steps if step.execution_status == 'failed')
            skipped_steps = sum(1 for step in steps if step.execution_status == 'skipped')
            in_progress_steps = sum(1 for step in steps if step.execution_status == 'in_progress')
            
            # Check if workflow is complete
            if completed_steps + skipped_steps == total_steps:
                # All steps completed or skipped
                self.update_workflow_status(workflow, 'completed')
            elif failed_steps > 0:
                # At least one step failed
                if all(step.execution_status in ('completed', 'failed', 'skipped') for step in steps):
                    # All steps are done (completed, failed, or skipped)
                    self.update_workflow_status(workflow, 'failed')
            elif in_progress_steps > 0:
                # At least one step in progress
                self.update_workflow_status(workflow, 'in_progress', save_completed_time=False)
                
        except Exception as e:
            logger.error(f"Error checking workflow status: {str(e)}")
    
    def delete_workflow(self, workflow: Workflow) -> bool:
        """
        Delete a workflow and its steps.
        
        Args:
            workflow: Workflow to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with transaction.atomic():
                # Delete steps first
                workflow.steps.all().delete()
                
                # Delete workflow
                workflow.delete()
                
                logger.info(f"Deleted workflow {workflow.id}")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting workflow: {str(e)}")
            return False
    
    def clone_workflow(self, 
                     workflow: Workflow, 
                     user: User,
                     name: Optional[str] = None,
                     include_sessions: bool = False) -> Optional[Workflow]:
        """
        Clone a workflow for a user.
        
        Args:
            workflow: Workflow to clone
            user: User to own the cloned workflow
            name: Optional name for the cloned workflow
            include_sessions: Whether to clone associated sessions
            
        Returns:
            Cloned Workflow if successful, None otherwise
        """
        try:
            with transaction.atomic():
                # Clone workflow
                new_workflow = Workflow.objects.create(
                    user=user,
                    name=name or f"Copy of {workflow.name}",
                    description=workflow.description,
                    dataset=workflow.dataset,  # Reference same dataset
                    initial_session=None,  # Don't copy initial session
                    metadata=workflow.metadata.copy(),
                    status='draft',
                    is_template=False,
                    is_public=False
                )
                
                # Clone steps
                step_mapping = {}  # Maps original step IDs to new step IDs
                
                for step in workflow.steps.all().order_by('order'):
                    new_step = WorkflowStep.objects.create(
                        workflow=new_workflow,
                        name=step.name,
                        description=step.description,
                        step_type=step.step_type,
                        order=step.order,
                        configuration=step.configuration.copy(),
                        analysis_session=None,  # Don't copy analysis sessions
                        is_required=step.is_required,
                        timeout_seconds=step.timeout_seconds,
                        execution_status='pending'
                    )
                    
                    step_mapping[step.id] = new_step
                
                # Update dependencies
                for original_step in workflow.steps.all():
                    if original_step.depends_on.exists():
                        new_step = step_mapping[original_step.id]
                        for dependency in original_step.depends_on.all():
                            if dependency.id in step_mapping:
                                new_step.depends_on.add(step_mapping[dependency.id])
                
                logger.info(f"Cloned workflow {workflow.id} to {new_workflow.id}")
                return new_workflow
                
        except Exception as e:
            logger.error(f"Error cloning workflow: {str(e)}")
            return None
    
    def export_workflow(self, workflow: Workflow, include_data: bool = False) -> Optional[str]:
        """
        Export workflow to JSON file.
        
        Args:
            workflow: Workflow to export
            include_data: Whether to include dataset data
            
        Returns:
            Path to exported file if successful, None otherwise
        """
        try:
            # Create export directory
            export_dir = os.path.join(self.base_storage_path, 'workflow_exports')
            os.makedirs(export_dir, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"workflow_export_{workflow.id}_{timestamp}.json"
            filepath = os.path.join(export_dir, filename)
            
            # Prepare workflow data
            workflow_data = {
                'id': str(workflow.id),
                'name': workflow.name,
                'description': workflow.description,
                'metadata': workflow.metadata,
                'created_at': workflow.created_at.isoformat(),
                'user': workflow.user.username,
                'steps': []
            }
            
            # Add steps
            for step in workflow.steps.all().order_by('order'):
                step_data = {
                    'id': str(step.id),
                    'name': step.name,
                    'description': step.description,
                    'step_type': step.step_type,
                    'order': step.order,
                    'configuration': step.configuration,
                    'is_required': step.is_required,
                    'dependencies': [str(dep.id) for dep in step.depends_on.all()]
                }
                workflow_data['steps'].append(step_data)
            
            # Add dataset info if exists
            if workflow.dataset:
                workflow_data['dataset'] = {
                    'id': str(workflow.dataset.id),
                    'name': workflow.dataset.name,
                    'file_type': workflow.dataset.file_type,
                    'columns_info': workflow.dataset.columns_info
                }
                
                # Include actual data if requested
                if include_data and workflow.dataset.file:
                    try:
                        # Handle different file types
                        file_path = workflow.dataset.file.path
                        if workflow.dataset.file_type == 'csv':
                            df = pd.read_csv(file_path)
                            workflow_data['dataset']['data'] = df.to_dict(orient='records')
                        elif workflow.dataset.file_type == 'excel':
                            df = pd.read_excel(file_path)
                            workflow_data['dataset']['data'] = df.to_dict(orient='records')
                    except Exception as data_e:
                        logger.error(f"Error including dataset data: {str(data_e)}")
            
            # Write to file
            with open(filepath, 'w') as f:
                json.dump(workflow_data, f, indent=2)
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting workflow: {str(e)}")
            return None
    
    def import_workflow(self, 
                      user: User, 
                      filepath: str, 
                      import_data: bool = False) -> Optional[Workflow]:
        """
        Import workflow from JSON file.
        
        Args:
            user: User to own the imported workflow
            filepath: Path to the JSON file
            import_data: Whether to import dataset data
            
        Returns:
            Imported Workflow if successful, None otherwise
        """
        try:
            # Read workflow data
            with open(filepath, 'r') as f:
                workflow_data = json.load(f)
            
            with transaction.atomic():
                # Create workflow
                workflow = Workflow.objects.create(
                    user=user,
                    name=workflow_data['name'],
                    description=workflow_data.get('description'),
                    metadata=workflow_data.get('metadata', {}),
                    status='draft',
                    is_template=False,
                    is_public=False
                )
                
                # Create or link dataset if exists
                dataset = None
                if 'dataset' in workflow_data:
                    dataset_info = workflow_data['dataset']
                    
                    # Look for existing dataset with same name
                    existing_dataset = Dataset.objects.filter(
                        user=user, 
                        name=dataset_info['name']
                    ).first()
                    
                    if existing_dataset:
                        dataset = existing_dataset
                    elif import_data and 'data' in dataset_info:
                        # Create new dataset from data
                        try:
                            # Convert data to DataFrame
                            df = pd.DataFrame(dataset_info['data'])
                            
                            # Save to temp file
                            temp_dir = os.path.join(self.base_storage_path, 'temp')
                            os.makedirs(temp_dir, exist_ok=True)
                            temp_file = os.path.join(temp_dir, f"{dataset_info['name']}.csv")
                            df.to_csv(temp_file, index=False)
                            
                            # Create dataset
                            with open(temp_file, 'rb') as f:
                                content = f.read()
                                
                            file_path = f"datasets/{user.id}/{dataset_info['name']}.csv"
                            file_storage = default_storage.save(file_path, ContentFile(content))
                            
                            dataset = Dataset.objects.create(
                                user=user,
                                name=dataset_info['name'],
                                file_type='csv',
                                file=file_storage,
                                columns_info=dataset_info.get('columns_info', {}),
                                row_count=len(df),
                                column_count=len(df.columns),
                                size_bytes=len(content)
                            )
                        except Exception as data_e:
                            logger.error(f"Error importing dataset: {str(data_e)}")
                    
                    # Link dataset to workflow
                    if dataset:
                        workflow.dataset = dataset
                        workflow.save(update_fields=['dataset'])
                
                # Create steps
                step_mapping = {}  # Maps original step IDs to new step objects
                
                for step_data in sorted(workflow_data.get('steps', []), key=lambda s: s.get('order', 0)):
                    step = WorkflowStep.objects.create(
                        workflow=workflow,
                        name=step_data['name'],
                        description=step_data.get('description'),
                        step_type=step_data['step_type'],
                        order=step_data.get('order', 0),
                        configuration=step_data.get('configuration', {}),
                        is_required=step_data.get('is_required', True),
                        timeout_seconds=step_data.get('timeout_seconds', 3600),
                        execution_status='pending'
                    )
                    
                    step_mapping[step_data['id']] = step
                
                # Set up dependencies
                for step_data in workflow_data.get('steps', []):
                    if 'dependencies' in step_data and step_data['dependencies']:
                        step = step_mapping[step_data['id']]
                        
                        for dep_id in step_data['dependencies']:
                            if dep_id in step_mapping:
                                step.depends_on.add(step_mapping[dep_id])
                
                logger.info(f"Imported workflow {workflow.id} for user {user.username}")
                return workflow
                
        except Exception as e:
            logger.error(f"Error importing workflow: {str(e)}")
            return None


# Create singleton instance
workflow_service = WorkflowService()

def get_workflow_service() -> WorkflowService:
    """Get global workflow service instance."""
    return workflow_service