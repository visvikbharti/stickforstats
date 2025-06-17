"""
Serializers for workflow-related models and API endpoints.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from stickforstats.mainapp.models import Workflow, WorkflowStep, Dataset, AnalysisSession, AnalysisResult

User = get_user_model()


class WorkflowStepDependencySerializer(serializers.ModelSerializer):
    """Serializer for workflow step dependencies."""
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    
    class Meta:
        model = WorkflowStep
        fields = ['id', 'name']


class WorkflowStepSerializer(serializers.ModelSerializer):
    """Serializer for workflow steps."""
    id = serializers.UUIDField(read_only=True)
    workflow_id = serializers.UUIDField(source='workflow.id', read_only=True)
    analysis_session_id = serializers.UUIDField(source='analysis_session.id', read_only=True, allow_null=True)
    depends_on = WorkflowStepDependencySerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    started_at = serializers.DateTimeField(read_only=True)
    completed_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = WorkflowStep
        fields = [
            'id', 'workflow_id', 'name', 'description', 'step_type', 
            'order', 'configuration', 'execution_status', 'analysis_session_id',
            'depends_on', 'is_required', 'timeout_seconds', 'created_at',
            'updated_at', 'started_at', 'completed_at'
        ]
        read_only_fields = ['id', 'workflow_id', 'created_at', 'updated_at', 'started_at', 'completed_at']


class WorkflowStepCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating workflow steps."""
    depends_on_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        write_only=True
    )
    
    class Meta:
        model = WorkflowStep
        fields = [
            'name', 'description', 'step_type', 'order', 'configuration',
            'is_required', 'timeout_seconds', 'depends_on_ids'
        ]
    
    def create(self, validated_data):
        depends_on_ids = validated_data.pop('depends_on_ids', [])
        workflow = self.context['workflow']
        
        # Create the step
        step = WorkflowStep.objects.create(workflow=workflow, **validated_data)
        
        # Add dependencies
        if depends_on_ids:
            dependencies = WorkflowStep.objects.filter(
                workflow=workflow,
                id__in=depends_on_ids
            )
            step.depends_on.set(dependencies)
        
        return step


class WorkflowSerializer(serializers.ModelSerializer):
    """Serializer for workflow objects."""
    id = serializers.UUIDField(read_only=True)
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    dataset = serializers.SlugRelatedField(slug_field='name', read_only=True)
    steps = WorkflowStepSerializer(many=True, read_only=True)
    steps_count = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    completed_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Workflow
        fields = [
            'id', 'user', 'name', 'description', 'dataset', 'status',
            'metadata', 'is_template', 'is_public', 'created_at',
            'updated_at', 'completed_at', 'steps', 'steps_count'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'completed_at', 'steps']
    
    def get_steps_count(self, obj):
        """Get the count of steps in the workflow."""
        return obj.steps.count()


class WorkflowCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating workflow objects."""
    dataset_id = serializers.UUIDField(required=False, allow_null=True, write_only=True)
    
    class Meta:
        model = Workflow
        fields = [
            'name', 'description', 'dataset_id', 'metadata', 
            'is_template', 'is_public'
        ]
    
    def create(self, validated_data):
        dataset_id = validated_data.pop('dataset_id', None)
        user = self.context['request'].user
        
        # Get the dataset if provided
        dataset = None
        if dataset_id:
            try:
                dataset = Dataset.objects.get(id=dataset_id)
                # Check if user has access to dataset
                if dataset.user != user and not dataset.is_public:
                    raise serializers.ValidationError(
                        {"dataset_id": "You do not have access to this dataset."}
                    )
            except Dataset.DoesNotExist:
                raise serializers.ValidationError(
                    {"dataset_id": "Dataset not found."}
                )
        
        # Create the workflow
        workflow = Workflow.objects.create(
            user=user,
            dataset=dataset,
            **validated_data
        )
        
        return workflow


class WorkflowUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating workflow objects."""
    dataset_id = serializers.UUIDField(required=False, allow_null=True, write_only=True)
    
    class Meta:
        model = Workflow
        fields = [
            'name', 'description', 'dataset_id', 'metadata', 
            'is_template', 'is_public', 'status'
        ]
    
    def update(self, instance, validated_data):
        dataset_id = validated_data.pop('dataset_id', None)
        user = self.context['request'].user
        
        # Get the dataset if provided
        if dataset_id:
            try:
                dataset = Dataset.objects.get(id=dataset_id)
                # Check if user has access to dataset
                if dataset.user != user and not dataset.is_public:
                    raise serializers.ValidationError(
                        {"dataset_id": "You do not have access to this dataset."}
                    )
                instance.dataset = dataset
            except Dataset.DoesNotExist:
                raise serializers.ValidationError(
                    {"dataset_id": "Dataset not found."}
                )
        
        # Update fields
        for field in validated_data:
            setattr(instance, field, validated_data[field])
        
        instance.save()
        return instance


class WorkflowDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for workflow objects with step details."""
    id = serializers.UUIDField(read_only=True)
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    dataset = serializers.SerializerMethodField()
    steps = WorkflowStepSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    completed_at = serializers.DateTimeField(read_only=True)
    execution_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Workflow
        fields = [
            'id', 'user', 'name', 'description', 'dataset', 'status',
            'metadata', 'is_template', 'is_public', 'created_at',
            'updated_at', 'completed_at', 'steps', 'execution_status'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'completed_at', 'steps']
    
    def get_dataset(self, obj):
        """Get detailed dataset information."""
        if not obj.dataset:
            return None
            
        return {
            'id': str(obj.dataset.id),
            'name': obj.dataset.name,
            'description': obj.dataset.description,
            'file_type': obj.dataset.file_type,
            'row_count': obj.dataset.row_count,
            'column_count': obj.dataset.column_count,
            'created_at': obj.dataset.created_at.isoformat() if obj.dataset.created_at else None
        }
    
    def get_execution_status(self, obj):
        """Get workflow execution status."""
        # This would be populated from the execution service in the view
        return self.context.get('execution_status', {})


class WorkflowExecutionSerializer(serializers.Serializer):
    """Serializer for workflow execution requests."""
    execute_from_step = serializers.IntegerField(required=False, min_value=0)


class WorkflowStepStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating workflow step status."""
    status = serializers.ChoiceField(choices=[
        'pending', 'in_progress', 'completed', 'failed', 'skipped'
    ])
    error_message = serializers.CharField(required=False, allow_blank=True)


class WorkflowCloneSerializer(serializers.Serializer):
    """Serializer for cloning a workflow."""
    name = serializers.CharField(required=False)
    include_sessions = serializers.BooleanField(default=False)


class WorkflowExportSerializer(serializers.Serializer):
    """Serializer for exporting a workflow."""
    include_data = serializers.BooleanField(default=False)


class WorkflowImportSerializer(serializers.Serializer):
    """Serializer for importing a workflow."""
    file = serializers.FileField()
    name = serializers.CharField(required=False)
    import_data = serializers.BooleanField(default=False)