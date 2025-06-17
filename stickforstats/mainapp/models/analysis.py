"""
Analysis models for the StickForStats application.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
from .user import User


class Dataset(models.Model):
    """
    Represents a data file uploaded for analysis.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='datasets')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='datasets/%Y/%m/%d/')
    file_type = models.CharField(max_length=20, choices=[
        ('csv', 'CSV'),
        ('excel', 'Excel'),
        ('json', 'JSON'),
        ('other', 'Other')
    ])
    columns_info = models.JSONField(blank=True, null=True)
    has_header = models.BooleanField(default=True)
    delimiter = models.CharField(max_length=5, default=',')
    sheet_name = models.CharField(max_length=100, blank=True, null=True)
    size_bytes = models.BigIntegerField(default=0)
    row_count = models.IntegerField(default=0)
    column_count = models.IntegerField(default=0)
    checksum = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('dataset')
        verbose_name_plural = _('datasets')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.file_type})"


class AnalysisSession(models.Model):
    """
    Represents a session of data analysis with a specific goal.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analysis_sessions')
    dataset = models.ForeignKey(Dataset, on_delete=models.SET_NULL, null=True, related_name='analysis_sessions')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    module = models.CharField(max_length=100, default='core')
    status = models.CharField(max_length=20, choices=[
        ('created', 'Created'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ], default='created')
    configuration = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('analysis session')
        verbose_name_plural = _('analysis sessions')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.module})"


class AnalysisResult(models.Model):
    """
    Represents results from an analysis operation.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(AnalysisSession, on_delete=models.CASCADE, related_name='results')
    name = models.CharField(max_length=255)
    analysis_type = models.CharField(max_length=100)
    parameters = models.JSONField(default=dict)
    result_summary = models.JSONField(default=dict)
    result_detail = models.JSONField(default=dict)
    interpretation = models.TextField(blank=True, null=True)
    plot_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('analysis result')
        verbose_name_plural = _('analysis results')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.analysis_type})"


class Visualization(models.Model):
    """
    Represents a stored visualization from analysis results.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    analysis_result = models.ForeignKey(AnalysisResult, on_delete=models.CASCADE, related_name='visualizations')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    visualization_type = models.CharField(max_length=50, choices=[
        ('scatter', 'Scatter Plot'),
        ('line', 'Line Chart'),
        ('bar', 'Bar Chart'),
        ('histogram', 'Histogram'),
        ('boxplot', 'Box Plot'),
        ('heatmap', 'Heatmap'),
        ('pca', 'PCA Plot'),
        ('other', 'Other')
    ])
    figure_data = models.JSONField()
    figure_layout = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('visualization')
        verbose_name_plural = _('visualizations')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.visualization_type})"