"""
Core Module Information

This module registers the Core module with the central module registry.
"""

from typing import Dict, Any
from .registry import ModuleRegistry

def register(registry: ModuleRegistry) -> None:
    """
    Register the Core module with the registry.
    
    Args:
        registry: The module registry to register with
    """
    module_info = {
        'name': 'Core',
        'display_name': 'StickForStats Core',
        'description': 'Core functionality for StickForStats platform including authentication, data management, visualization, and cross-module integration.',
        'version': '1.1.0',
        'author': 'StickForStats Team',
        'entry_point': 'stickforstats.core.views.dashboard',
        'api_namespace': 'stickforstats.core.api.urls',
        'frontend_path': '/',
        'capabilities': [
            'authentication',
            'data_management',
            'visualization',
            'reporting',
            'workflow_management',
            'module_integration',
            'basic_statistics'
        ],
        'dependencies': [],  # Core has no dependencies
        'icon': 'Dashboard',
        'category': 'Core',
        'order': 0,
        'enabled': True,
        'metadata': {
            'primary_color': '#3F51B5',
            'supports_interactive_visualization': True,
            'supports_data_import': True,
            'supports_data_export': True,
            'supports_reporting': True,
            'supports_user_management': True,
            'supports_workflow_management': True
        },
        'services': {
            'auth': {
                'service': 'stickforstats.core.services.auth.auth_service.AuthService',
                'description': 'Authentication and authorization service'
            },
            'data': {
                'service': 'stickforstats.core.services.data_service.DataService',
                'description': 'Data management service'
            },
            'dataset': {
                'service': 'stickforstats.core.services.dataset_service.DatasetService',
                'description': 'Dataset management service'
            },
            'visualization': {
                'service': 'stickforstats.core.services.visualization.visualization_service.VisualizationService',
                'description': 'Visualization service'
            },
            'report': {
                'service': 'stickforstats.core.services.report.report_service.ReportService',
                'description': 'Report generation service'
            },
            'workflow': {
                'service': 'stickforstats.core.services.workflow.workflow_service.WorkflowService',
                'description': 'Workflow management service'
            },
            'session': {
                'service': 'stickforstats.core.services.session.session_service.SessionService',
                'description': 'Session management service'
            },
            'guidance': {
                'service': 'stickforstats.core.services.guidance.guidance_service.GuidanceService',
                'description': 'User guidance and recommendations service'
            },
            'error_handler': {
                'service': 'stickforstats.core.services.error_handler.ErrorHandler',
                'description': 'Error handling service'
            }
        },
        'documentation_url': '/docs/core',
        'tutorials': [
            {
                'title': 'Getting Started with StickForStats',
                'url': '/tutorials/core/getting-started'
            },
            {
                'title': 'Managing Datasets',
                'url': '/tutorials/core/datasets'
            },
            {
                'title': 'Creating Reports',
                'url': '/tutorials/core/reports'
            },
            {
                'title': 'Building Workflows',
                'url': '/tutorials/core/workflows'
            },
            {
                'title': 'User Management',
                'url': '/tutorials/core/users'
            }
        ]
    }
    
    registry.register_module('core', module_info)