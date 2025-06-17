"""
API views for workflow management and execution.
"""

import json
import logging
from typing import Dict, Any, List, Optional
import uuid

from django.http import Http404, FileResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db import transaction

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from stickforstats.mainapp.models import Workflow, WorkflowStep, AnalysisSession, Dataset
from stickforstats.mainapp.services.workflow_service import get_workflow_service
from stickforstats.mainapp.services.workflow_execution_service import get_workflow_execution_service
from .workflow_serializers import (
    WorkflowSerializer, WorkflowCreateSerializer, WorkflowUpdateSerializer,
    WorkflowDetailSerializer, WorkflowStepSerializer, WorkflowStepCreateSerializer,
    WorkflowExecutionSerializer, WorkflowStepStatusUpdateSerializer,
    WorkflowCloneSerializer, WorkflowExportSerializer, WorkflowImportSerializer
)

logger = logging.getLogger(__name__)


class WorkflowListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating workflows.
    
    GET: List workflows for the current user
    POST: Create a new workflow
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WorkflowSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # Process filters
        include_public = self.request.query_params.get('include_public', 'false').lower() == 'true'
        include_templates = self.request.query_params.get('include_templates', 'false').lower() == 'true'
        status_filter = self.request.query_params.get('status')
        
        # Call workflow service
        workflow_service = get_workflow_service()
        workflows = workflow_service.list_workflows(
            user=user,
            include_public=include_public,
            include_templates=include_templates,
            status=status_filter
        )
        
        return workflows
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WorkflowCreateSerializer
        return WorkflowSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class WorkflowDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting a workflow.
    
    GET: Retrieve workflow details
    PUT/PATCH: Update workflow
    DELETE: Delete workflow
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WorkflowDetailSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        user = self.request.user
        
        # Base query - user's workflows or public workflows
        return Workflow.objects.filter(
            user=user
        ).select_related(
            'user', 'dataset', 'initial_session'
        ).prefetch_related(
            'steps'
        )
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return WorkflowUpdateSerializer
        return WorkflowDetailSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        
        # Add execution status if available
        workflow_id = self.kwargs.get('id')
        if workflow_id:
            workflow_execution_service = get_workflow_execution_service()
            execution_status = workflow_execution_service.get_execution_status(workflow_id)
            context['execution_status'] = execution_status
            
        return context
    
    def destroy(self, request, *args, **kwargs):
        workflow = self.get_object()
        
        # Use workflow service to delete
        workflow_service = get_workflow_service()
        success = workflow_service.delete_workflow(workflow)
        
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"error": "Failed to delete workflow"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WorkflowStepListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating workflow steps.
    
    GET: List steps for a workflow
    POST: Add a step to a workflow
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WorkflowStepSerializer
    
    def get_workflow(self):
        """Get the workflow for the step."""
        workflow_id = self.kwargs.get('workflow_id')
        user = self.request.user
        
        try:
            return Workflow.objects.get(id=workflow_id, user=user)
        except Workflow.DoesNotExist:
            raise Http404("Workflow not found or you do not have permission to access it")
    
    def get_queryset(self):
        workflow = self.get_workflow()
        return WorkflowStep.objects.filter(
            workflow=workflow
        ).select_related(
            'workflow', 'analysis_session'
        ).prefetch_related(
            'depends_on'
        ).order_by('order')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WorkflowStepCreateSerializer
        return WorkflowStepSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['workflow'] = self.get_workflow()
        return context
    
    def create(self, request, *args, **kwargs):
        workflow = self.get_workflow()
        
        # Check workflow status
        if workflow.status not in ['draft', 'active']:
            return Response(
                {"error": "Cannot add steps to a completed or archived workflow"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Use workflow service to add step
        workflow_service = get_workflow_service()
        try:
            with transaction.atomic():
                # Create step
                step = serializer.save()
                
                # Update workflow status if needed
                if workflow.status == 'draft' and workflow.steps.count() > 0:
                    workflow_service.update_workflow_status(workflow, 'active', save_completed_time=False)
                
                return Response(
                    WorkflowStepSerializer(step).data, 
                    status=status.HTTP_201_CREATED
                )
                
        except Exception as e:
            logger.error(f"Error adding workflow step: {str(e)}")
            return Response(
                {"error": f"Failed to create workflow step: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WorkflowStepDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting a workflow step.
    
    GET: Retrieve step details
    PUT/PATCH: Update step
    DELETE: Delete step
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WorkflowStepSerializer
    lookup_field = 'id'
    
    def get_workflow(self):
        """Get the workflow for the step."""
        workflow_id = self.kwargs.get('workflow_id')
        user = self.request.user
        
        try:
            return Workflow.objects.get(id=workflow_id, user=user)
        except Workflow.DoesNotExist:
            raise Http404("Workflow not found or you do not have permission to access it")
    
    def get_queryset(self):
        workflow = self.get_workflow()
        return WorkflowStep.objects.filter(
            workflow=workflow
        ).select_related(
            'workflow', 'analysis_session'
        ).prefetch_related(
            'depends_on'
        )
    
    def update(self, request, *args, **kwargs):
        step = self.get_object()
        workflow = step.workflow
        
        # Check workflow status
        if workflow.status not in ['draft', 'active']:
            return Response(
                {"error": "Cannot update steps in a completed or archived workflow"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Check step status
        if step.execution_status not in ['pending', 'failed']:
            return Response(
                {"error": "Cannot update a step that has been executed"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Process updates
        try:
            # Handle special case for dependencies
            if 'depends_on_ids' in request.data:
                depends_on_ids = request.data.pop('depends_on_ids')
                dependencies = WorkflowStep.objects.filter(
                    workflow=workflow,
                    id__in=depends_on_ids
                )
                step.depends_on.set(dependencies)
            
            return super().update(request, *args, **kwargs)
            
        except Exception as e:
            logger.error(f"Error updating workflow step: {str(e)}")
            return Response(
                {"error": f"Failed to update workflow step: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, *args, **kwargs):
        step = self.get_object()
        workflow = step.workflow
        
        # Check workflow status
        if workflow.status not in ['draft', 'active']:
            return Response(
                {"error": "Cannot delete steps from a completed or archived workflow"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Check step status
        if step.execution_status not in ['pending', 'failed']:
            return Response(
                {"error": "Cannot delete a step that has been executed successfully"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Check for dependent steps
        dependent_steps = WorkflowStep.objects.filter(depends_on=step)
        if dependent_steps.exists():
            return Response(
                {"error": "Cannot delete a step that other steps depend on"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return super().destroy(request, *args, **kwargs)


class WorkflowExecuteView(APIView):
    """
    API endpoint for executing a workflow.
    
    POST: Start workflow execution
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, workflow_id):
        user = request.user
        
        try:
            # Validate input
            serializer = WorkflowExecutionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Execute workflow
            workflow_execution_service = get_workflow_execution_service()
            result = workflow_execution_service.execute_workflow(
                workflow_id=workflow_id,
                user=user,
                execute_from_step=serializer.validated_data.get('execute_from_step')
            )
            
            if result.get('status') == 'error':
                return Response(
                    {"error": result.get('message', 'Unknown error')},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error executing workflow: {str(e)}")
            return Response(
                {"error": f"Failed to execute workflow: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WorkflowExecutionStatusView(APIView):
    """
    API endpoint for checking workflow execution status.
    
    GET: Get execution status
    DELETE: Cancel execution
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, workflow_id):
        user = request.user
        
        try:
            # Get execution status
            workflow_execution_service = get_workflow_execution_service()
            status_result = workflow_execution_service.get_execution_status(workflow_id)
            
            if status_result.get('status') == 'error':
                return Response(
                    {"error": status_result.get('message', 'Unknown error')},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            return Response(status_result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting workflow execution status: {str(e)}")
            return Response(
                {"error": f"Failed to get execution status: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, workflow_id):
        user = request.user
        
        try:
            # Cancel execution
            workflow_execution_service = get_workflow_execution_service()
            result = workflow_execution_service.cancel_execution(workflow_id, user)
            
            if result.get('status') == 'error':
                return Response(
                    {"error": result.get('message', 'Unknown error')},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error cancelling workflow execution: {str(e)}")
            return Response(
                {"error": f"Failed to cancel execution: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WorkflowStepStatusUpdateView(APIView):
    """
    API endpoint for updating a workflow step's status.
    
    PUT: Update step status
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request, workflow_id, step_id):
        user = request.user
        
        try:
            # Get workflow
            workflow = Workflow.objects.get(id=workflow_id, user=user)
            
            # Get step
            step = WorkflowStep.objects.get(id=step_id, workflow=workflow)
            
            # Validate input
            serializer = WorkflowStepStatusUpdateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Update status
            workflow_service = get_workflow_service()
            success = workflow_service.update_step_status(
                step=step,
                status=serializer.validated_data['status'],
                error_message=serializer.validated_data.get('error_message')
            )
            
            if not success:
                return Response(
                    {"error": "Failed to update step status"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
            return Response(
                WorkflowStepSerializer(step).data,
                status=status.HTTP_200_OK
            )
            
        except Workflow.DoesNotExist:
            return Response(
                {"error": "Workflow not found or you do not have permission to access it"},
                status=status.HTTP_404_NOT_FOUND
            )
        except WorkflowStep.DoesNotExist:
            return Response(
                {"error": "Step not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating workflow step status: {str(e)}")
            return Response(
                {"error": f"Failed to update step status: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WorkflowCloneView(APIView):
    """
    API endpoint for cloning a workflow.
    
    POST: Clone workflow
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, workflow_id):
        user = request.user
        
        try:
            # Get the source workflow
            workflow_service = get_workflow_service()
            source_workflow = workflow_service.get_workflow(workflow_id)
            
            if not source_workflow:
                return Response(
                    {"error": "Workflow not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            # Check permissions
            if source_workflow.user != user and not source_workflow.is_public:
                return Response(
                    {"error": "You do not have permission to clone this workflow"},
                    status=status.HTTP_403_FORBIDDEN
                )
                
            # Validate input
            serializer = WorkflowCloneSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Clone workflow
            new_name = serializer.validated_data.get('name')
            include_sessions = serializer.validated_data.get('include_sessions', False)
            
            cloned_workflow = workflow_service.clone_workflow(
                workflow=source_workflow,
                user=user,
                name=new_name,
                include_sessions=include_sessions
            )
            
            if not cloned_workflow:
                return Response(
                    {"error": "Failed to clone workflow"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
            return Response(
                WorkflowSerializer(cloned_workflow).data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f"Error cloning workflow: {str(e)}")
            return Response(
                {"error": f"Failed to clone workflow: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WorkflowExportView(APIView):
    """
    API endpoint for exporting a workflow.
    
    GET: Export workflow to JSON file
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, workflow_id):
        user = request.user
        
        try:
            # Get the workflow
            workflow_service = get_workflow_service()
            workflow = workflow_service.get_workflow(workflow_id)
            
            if not workflow:
                return Response(
                    {"error": "Workflow not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            # Check permissions
            if workflow.user != user:
                return Response(
                    {"error": "You do not have permission to export this workflow"},
                    status=status.HTTP_403_FORBIDDEN
                )
                
            # Validate parameters
            include_data = request.query_params.get('include_data', 'false').lower() == 'true'
            
            # Export workflow
            filepath = workflow_service.export_workflow(
                workflow=workflow,
                include_data=include_data
            )
            
            if not filepath:
                return Response(
                    {"error": "Failed to export workflow"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
            # Serve the file
            response = FileResponse(open(filepath, 'rb'))
            filename = f"workflow_{workflow.name.replace(' ', '_')}_{timezone.now().strftime('%Y%m%d')}.json"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        except Exception as e:
            logger.error(f"Error exporting workflow: {str(e)}")
            return Response(
                {"error": f"Failed to export workflow: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WorkflowImportView(APIView):
    """
    API endpoint for importing a workflow.
    
    POST: Import workflow from JSON file
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def post(self, request):
        user = request.user
        
        try:
            # Validate input
            serializer = WorkflowImportSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Get file
            file_obj = serializer.validated_data['file']
            
            # Save to temporary file
            import_dir = 'temp/workflow_imports'
            os.makedirs(import_dir, exist_ok=True)
            temp_filepath = f"{import_dir}/{file_obj.name}"
            
            with default_storage.open(temp_filepath, 'wb+') as destination:
                for chunk in file_obj.chunks():
                    destination.write(chunk)
            
            # Import workflow
            workflow_service = get_workflow_service()
            imported_workflow = workflow_service.import_workflow(
                user=user,
                filepath=default_storage.path(temp_filepath),
                import_data=serializer.validated_data.get('import_data', False)
            )
            
            # Clean up temp file
            default_storage.delete(temp_filepath)
            
            if not imported_workflow:
                return Response(
                    {"error": "Failed to import workflow"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
            return Response(
                WorkflowSerializer(imported_workflow).data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f"Error importing workflow: {str(e)}")
            return Response(
                {"error": f"Failed to import workflow: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WorkflowExecutionHistoryView(APIView):
    """
    API endpoint for getting workflow execution history.
    
    GET: Get execution history for the current user
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        try:
            # Get limit parameter
            limit = int(request.query_params.get('limit', 20))
            
            # Get execution history
            workflow_execution_service = get_workflow_execution_service()
            history = workflow_execution_service.get_execution_history(user, limit=limit)
            
            return Response(history, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting workflow execution history: {str(e)}")
            return Response(
                {"error": f"Failed to get execution history: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )