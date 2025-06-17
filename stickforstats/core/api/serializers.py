from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Analysis
from stickforstats.mainapp.models.analysis import Dataset, Visualization
from stickforstats.mainapp.models.workflow import Workflow, WorkflowStep

# Define placeholder models for backward compatibility
# These will be replaced with proper implementations as needed
class DataValidationResult:
    pass

class Report:
    pass

class GuidanceRecommendation:
    pass

class UserPreference:
    pass

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User objects."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']

class DatasetSerializer(serializers.ModelSerializer):
    """Serializer for Dataset objects."""
    class Meta:
        model = Dataset
        fields = ['id', 'user', 'name', 'description', 'file', 'file_type',
                 'created_at', 'updated_at', 'has_header', 'delimiter',
                 'row_count', 'column_count', 'columns_info']
        read_only_fields = ['id', 'created_at', 'updated_at']

class DataValidationResultSerializer(serializers.ModelSerializer):
    """Serializer for DataValidationResult objects."""
    class Meta:
        model = DataValidationResult
        fields = ['id', 'dataset', 'validation_type', 'created_at', 
                 'is_valid', 'validation_messages']
        read_only_fields = ['id', 'created_at']

class VisualizationSerializer(serializers.ModelSerializer):
    """Serializer for Visualization objects."""
    class Meta:
        model = Visualization
        fields = ['id', 'analysis', 'title', 'description', 'visualization_type',
                 'created_at', 'updated_at', 'parameters', 'figure_data', 'image_path']
        read_only_fields = ['id', 'created_at', 'updated_at']

class AnalysisSerializer(serializers.ModelSerializer):
    """Serializer for Analysis objects."""
    visualizations = VisualizationSerializer(many=True, read_only=True)
    
    class Meta:
        model = Analysis
        fields = ['id', 'user', 'name', 'description', 'analysis_type',
                 'created_at', 'updated_at', 'parameters', 'results', 
                 'metadata', 'visualizations']
        read_only_fields = ['id', 'created_at', 'updated_at']

class AnalysisCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Analysis objects."""
    visualizations = serializers.ListField(
        child=serializers.DictField(), 
        required=False,
        write_only=True
    )
    
    class Meta:
        model = Analysis
        fields = ['id', 'user', 'name', 'description', 'analysis_type',
                 'parameters', 'results', 'metadata', 'visualizations']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        visualizations_data = validated_data.pop('visualizations', [])
        analysis = Analysis.objects.create(**validated_data)
        
        # Create visualizations for the analysis
        for viz_data in visualizations_data:
            Visualization.objects.create(analysis=analysis, **viz_data)
        
        return analysis

class ReportSerializer(serializers.ModelSerializer):
    """Serializer for Report objects."""
    class Meta:
        model = Report
        fields = ['id', 'user', 'name', 'description', 'report_type',
                 'created_at', 'analyses', 'file_path', 'parameters']
        read_only_fields = ['id', 'created_at']

class WorkflowSerializer(serializers.ModelSerializer):
    """Serializer for Workflow objects."""
    class Meta:
        model = Workflow
        fields = ['id', 'user', 'name', 'description', 'created_at',
                 'updated_at', 'dataset', 'steps', 'status']
        read_only_fields = ['id', 'created_at', 'updated_at']

class GuidanceRecommendationSerializer(serializers.ModelSerializer):
    """Serializer for GuidanceRecommendation objects."""
    class Meta:
        model = GuidanceRecommendation
        fields = ['id', 'user', 'created_at', 'context_data', 
                 'recommendation_type', 'recommendation', 'applied']
        read_only_fields = ['id', 'created_at']

class UserPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for UserPreference objects."""
    class Meta:
        model = UserPreference
        fields = ['id', 'user', 'created_at', 'updated_at', 'preferences']
        read_only_fields = ['id', 'created_at', 'updated_at']

# Specialized serializers for specific operations

class DataUploadSerializer(serializers.Serializer):
    """Serializer for data upload operations."""
    file = serializers.FileField()
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    validate = serializers.BooleanField(default=True)

class AnalysisRequestSerializer(serializers.Serializer):
    """Serializer for analysis requests."""
    dataset_id = serializers.UUIDField()
    analysis_type = serializers.CharField(max_length=100)
    parameters = serializers.DictField(default=dict)
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)

class ReportGenerationSerializer(serializers.Serializer):
    """Serializer for report generation requests."""
    analysis_ids = serializers.ListField(child=serializers.UUIDField())
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    report_format = serializers.ChoiceField(choices=['pdf', 'html', 'docx'], default='pdf')
    include_visualizations = serializers.BooleanField(default=True)
    include_raw_data = serializers.BooleanField(default=False)

class GuidanceRequestSerializer(serializers.Serializer):
    """Serializer for guidance requests."""
    dataset_id = serializers.UUIDField()
    user_goals = serializers.DictField(required=False, default=dict)

# Statistical Analysis Serializers

class StatisticalTestRequestSerializer(serializers.Serializer):
    """Serializer for general statistical test requests."""
    dataset_id = serializers.UUIDField()
    test_type = serializers.CharField(max_length=100)
    parameters = serializers.DictField(default=dict)

    # Common test parameters
    variables = serializers.ListField(child=serializers.CharField(), required=False)
    groups = serializers.CharField(required=False, allow_null=True)
    dependent_var = serializers.CharField(required=False, allow_null=True)
    independent_vars = serializers.ListField(child=serializers.CharField(), required=False)
    alpha = serializers.FloatField(default=0.05, required=False)

class DescriptiveStatsRequestSerializer(serializers.Serializer):
    """Serializer for descriptive statistics requests."""
    dataset_id = serializers.UUIDField()
    variables = serializers.ListField(child=serializers.CharField())
    include_quartiles = serializers.BooleanField(default=True, required=False)
    include_normality = serializers.BooleanField(default=True, required=False)
    include_histogram = serializers.BooleanField(default=True, required=False)

class CorrelationAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for correlation analysis requests."""
    dataset_id = serializers.UUIDField()
    variables = serializers.ListField(child=serializers.CharField())
    method = serializers.ChoiceField(
        choices=['pearson', 'spearman', 'kendall', 'point_biserial'],
        default='pearson',
        required=False
    )
    include_p_values = serializers.BooleanField(default=True, required=False)

class RegressionAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for regression analysis requests."""
    dataset_id = serializers.UUIDField()
    dependent_var = serializers.CharField()
    independent_vars = serializers.ListField(child=serializers.CharField())
    regression_type = serializers.ChoiceField(
        choices=['linear', 'multiple', 'polynomial', 'logistic', 'ridge', 'lasso'],
        default='linear',
        required=False
    )
    include_diagnostics = serializers.BooleanField(default=True, required=False)

class ClusteringAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for clustering analysis requests."""
    dataset_id = serializers.UUIDField()
    variables = serializers.ListField(child=serializers.CharField())
    method = serializers.ChoiceField(
        choices=['kmeans', 'hierarchical', 'dbscan', 'gaussian_mixture'],
        default='kmeans',
        required=False
    )
    n_clusters = serializers.IntegerField(default=3, required=False)
    standardize = serializers.BooleanField(default=True, required=False)

class TimeSeriesAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for time series analysis requests."""
    dataset_id = serializers.UUIDField()
    time_var = serializers.CharField()
    value_var = serializers.CharField()
    frequency = serializers.CharField(required=False, allow_null=True)
    analysis_type = serializers.ChoiceField(
        choices=['decomposition', 'trend', 'seasonality', 'forecast'],
        default='decomposition',
        required=False
    )
    forecast_periods = serializers.IntegerField(default=10, required=False)

class BayesianAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for Bayesian analysis requests."""
    dataset_id = serializers.UUIDField()
    analysis_type = serializers.ChoiceField(
        choices=['inference', 'regression', 'hierarchical', 'ab_testing'],
        default='inference'
    )
    parameters = serializers.DictField(default=dict)
    iterations = serializers.IntegerField(default=1000, required=False)
    tune = serializers.IntegerField(default=500, required=False)
    chains = serializers.IntegerField(default=2, required=False)