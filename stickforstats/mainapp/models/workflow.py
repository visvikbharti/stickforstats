"""
Workflow models for the StickForStats application.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
from .user import User
from .analysis import Dataset, AnalysisSession


class Workflow(models.Model):
    """
    Represents a complete data analysis workflow with multiple steps.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workflows')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    dataset = models.ForeignKey(Dataset, on_delete=models.SET_NULL, null=True, related_name='workflows')
    initial_session = models.ForeignKey(AnalysisSession, on_delete=models.SET_NULL, null=True, blank=True, related_name='workflow_starts')
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('archived', 'Archived')
    ], default='draft')
    metadata = models.JSONField(default=dict)
    is_template = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('workflow')
        verbose_name_plural = _('workflows')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class WorkflowStep(models.Model):
    """
    Represents a single step in a workflow.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='steps')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    step_type = models.CharField(max_length=100, choices=[
        ('data_loading', 'Data Loading'),
        ('data_preprocessing', 'Data Preprocessing'),
        ('visualization', 'Visualization'),
        ('statistical_test', 'Statistical Test'),
        ('machine_learning', 'Machine Learning'),
        ('advanced_statistics', 'Advanced Statistics'),
        ('report_generation', 'Report Generation'),
        ('other', 'Other')
    ])
    order = models.PositiveIntegerField(default=0)
    configuration = models.JSONField(default=dict)
    execution_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped')
    ], default='pending')
    analysis_session = models.ForeignKey(AnalysisSession, on_delete=models.SET_NULL, null=True, blank=True, related_name='workflow_steps')
    depends_on = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='dependents')
    is_required = models.BooleanField(default=True)
    timeout_seconds = models.IntegerField(default=3600)  # Default 1 hour timeout
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('workflow step')
        verbose_name_plural = _('workflow steps')
        ordering = ['workflow', 'order']
    
    def __str__(self):
        return f"{self.name} ({self.step_type})"