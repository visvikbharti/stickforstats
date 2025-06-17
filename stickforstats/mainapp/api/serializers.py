"""
Serializers for the StickForStats MainApp API.
"""

from rest_framework import serializers
from typing import Dict, Any, List

class StatisticalTestSerializer(serializers.Serializer):
    """Serializer for statistical test requests."""
    test_type = serializers.CharField(required=True)
    parameters = serializers.DictField(required=False, default=dict)


class AdvancedAnalysisSerializer(serializers.Serializer):
    """Serializer for advanced analysis requests."""
    analysis_type = serializers.CharField(required=True)
    parameters = serializers.DictField(required=False, default=dict)


class BayesianAnalysisSerializer(serializers.Serializer):
    """Serializer for Bayesian analysis requests."""
    analysis_type = serializers.CharField(required=True)
    parameters = serializers.DictField(required=False, default=dict)


class VisualizationSerializer(serializers.Serializer):
    """Serializer for visualizations in reports."""
    title = serializers.CharField(required=True)
    visualization_type = serializers.CharField(required=True)
    description = serializers.CharField(required=False, allow_blank=True)
    figure_data = serializers.DictField(required=True)


class AnalysisResultSerializer(serializers.Serializer):
    """Serializer for analysis results in reports."""
    name = serializers.CharField(required=True)
    analysis_type = serializers.CharField(required=True)
    parameters = serializers.DictField(required=False, default=dict)
    results = serializers.DictField(required=True)
    visualizations = VisualizationSerializer(many=True, required=False)


class ReportGenerationSerializer(serializers.Serializer):
    """Serializer for report generation requests."""
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=False, allow_blank=True)
    format = serializers.ChoiceField(choices=['pdf', 'html', 'docx'], required=False, default='pdf')
    analyses = serializers.ListField(
        child=serializers.JSONField(),
        required=True
    )
    include_visualizations = serializers.BooleanField(required=False, default=True)
    include_raw_data = serializers.BooleanField(required=False, default=False)


class ReportSerializer(serializers.Serializer):
    """Serializer for report metadata."""
    id = serializers.CharField(required=True)
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=False, allow_blank=True)
    user_id = serializers.CharField(required=True)
    created_at = serializers.DateTimeField(required=True)
    report_format = serializers.CharField(required=True)
    file_path = serializers.CharField(required=True)
    analyses = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )