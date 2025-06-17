"""
MainApp Module Information

This module registers the MainApp module with the central module registry.
This is the core application module containing comprehensive functionality
migrated from the original Streamlit-based application.
"""

from typing import Dict, Any
from ..core.registry import ModuleRegistry

def register(registry: ModuleRegistry) -> None:
    """
    Register the MainApp module with the registry.
    
    Args:
        registry: The module registry to register with
    """
    module_info = {
        'name': 'MainApp',
        'display_name': 'StickForStats Main Application',
        'description': 'Core functionality for statistical analysis including basic and advanced statistical methods, data processing, visualization, and workflow management.',
        'version': '1.1.0',
        'author': 'StickForStats Team',
        'entry_point': 'stickforstats.mainapp.views.main_dashboard',
        'api_namespace': 'stickforstats.mainapp.urls',
        'frontend_path': '/',
        'capabilities': [
            # Basic Statistics
            'descriptive_statistics',
            'normality_tests',
            'correlation_analysis',
            'regression_analysis',
            'hypothesis_testing',
            'data_visualization',
            
            # Advanced Statistics
            'time_series_analysis',
            'multivariate_analysis',
            'cluster_analysis',
            'factor_analysis',
            'bayesian_statistics',
            'machine_learning',
            
            # Data Management
            'data_preprocessing',
            'data_transformation',
            'data_validation',
            'dataset_management',
            
            # Workflow Management
            'analysis_workflows',
            'batch_processing',
            'result_comparison',
            'session_management',
            
            # Reporting
            'report_generation',
            'result_export',
            'visualization_export',
            
            # User Management
            'user_authentication',
            'project_management',
            'collaboration',
        ],
        'dependencies': ['core'],
        'icon': 'Analytics',
        'category': 'Core',
        'order': 1,
        'enabled': True,
        'metadata': {
            'primary_color': '#2196F3',
            'supports_interactive_visualization': True,
            'supports_batch_processing': True,
            'supports_workflows': True,
            'supports_reporting': True,
            'supports_projects': True,
            'supports_collaboration': True,
            'is_core_application': True
        },
        'services': {
            # Core services based on original code structure
            'auth_service': {
                'service': 'stickforstats.mainapp.services.auth_service.AuthService',
                'description': 'User authentication and authorization service'
            },
            'session_service': {
                'service': 'stickforstats.mainapp.services.session_service.SessionService',
                'description': 'User session management service'
            },
            'workflow_service': {
                'service': 'stickforstats.mainapp.services.workflow_service.WorkflowService',
                'description': 'Workflow management service'
            },
            
            # Data processing services
            'data_validation': {
                'service': 'stickforstats.mainapp.services.data_processing.data_validator.DataValidator',
                'description': 'Data validation and cleaning service'
            },
            'data_service': {
                'service': 'stickforstats.mainapp.services.data_service.DataService',
                'description': 'Data management and processing service'
            },
            'error_handler': {
                'service': 'stickforstats.mainapp.services.error_handler.ErrorHandler',
                'description': 'Error handling and management service'
            },
            
            # Statistical analysis services
            'statistical_tests': {
                'service': 'stickforstats.mainapp.services.statistical_tests.StatisticalTestsService',
                'description': 'Basic statistical testing service'
            },
            'advanced_statistical_analysis': {
                'service': 'stickforstats.mainapp.services.advanced_statistical_analysis.AdvancedStatisticalAnalysisService',
                'description': 'Advanced statistical methods and algorithms'
            },
            'bayesian_analysis': {
                'service': 'stickforstats.mainapp.services.bayesian_analysis.BayesianAnalysisService',
                'description': 'Bayesian statistical methods'
            },
            'machine_learning': {
                'service': 'stickforstats.mainapp.services.machine_learning.MachineLearningService',
                'description': 'Machine learning models and algorithms'
            },
            'time_series': {
                'service': 'stickforstats.mainapp.services.time_series.TimeSeriesService',
                'description': 'Time series analysis and forecasting'
            },
            'integrated_analysis': {
                'service': 'stickforstats.mainapp.services.integrated_analysis.IntegratedAnalysisService',
                'description': 'Integrated statistical workflow service'
            },
            
            # Visualization and reporting services
            'visualization': {
                'service': 'stickforstats.mainapp.services.visualization.VisualizationService',
                'description': 'Data visualization service'
            },
            'advanced_plotting': {
                'service': 'stickforstats.mainapp.services.advanced_plotting.AdvancedPlottingService',
                'description': 'Advanced data visualization service'
            },
            'report_generator': {
                'service': 'stickforstats.mainapp.services.report_generator.ReportGeneratorService',
                'description': 'Report generation and export service'
            },
        },
        'documentation_url': '/docs/mainapp',
        'tutorials': [
            {
                'title': 'Getting Started with StickForStats',
                'url': '/tutorials/getting-started'
            },
            {
                'title': 'Basic Statistical Analysis',
                'url': '/tutorials/basic-statistics'
            },
            {
                'title': 'Advanced Statistical Methods',
                'url': '/tutorials/advanced-statistics'
            },
            {
                'title': 'Data Visualization Techniques',
                'url': '/tutorials/data-visualization'
            },
            {
                'title': 'Creating Analysis Workflows',
                'url': '/tutorials/analysis-workflows'
            },
            {
                'title': 'Working with Projects',
                'url': '/tutorials/projects'
            },
            {
                'title': 'Generating Reports',
                'url': '/tutorials/reporting'
            },
            {
                'title': 'Machine Learning Capabilities',
                'url': '/tutorials/machine-learning'
            },
            {
                'title': 'Time Series Analysis',
                'url': '/tutorials/time-series'
            },
            {
                'title': 'Bayesian Statistics',
                'url': '/tutorials/bayesian'
            }
        ]
    }
    
    registry.register_module('mainapp', module_info)