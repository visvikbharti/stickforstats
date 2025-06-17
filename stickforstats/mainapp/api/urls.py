"""
URL configuration for the StickForStats MainApp API.
"""

from django.urls import path
from .views import (
    StatisticalTestView,
    AdvancedAnalysisView,
    BayesianAnalysisView,
    ReportGeneratorView,
    ReportListView,
    ReportDetailView,
)
from .workflow_views import (
    WorkflowListCreateView,
    WorkflowDetailView,
    WorkflowStepListCreateView,
    WorkflowStepDetailView,
    WorkflowExecuteView,
    WorkflowExecutionStatusView,
    WorkflowStepStatusUpdateView,
    WorkflowCloneView,
    WorkflowExportView,
    WorkflowImportView,
    WorkflowExecutionHistoryView,
)

urlpatterns = [
    # Statistical Tests API
    path('statistical-tests/', StatisticalTestView.as_view(), name='statistical-tests'),
    
    # Advanced Analysis API
    path('advanced-analysis/', AdvancedAnalysisView.as_view(), name='advanced-analysis'),
    
    # Bayesian Analysis API
    path('bayesian-analysis/', BayesianAnalysisView.as_view(), name='bayesian-analysis'),
    
    # Report Generator API
    path('reports/generate/', ReportGeneratorView.as_view(), name='report-generate'),
    path('reports/', ReportListView.as_view(), name='report-list'),
    path('reports/<str:report_id>/', ReportDetailView.as_view(), name='report-detail'),
    
    # Workflow API
    path('workflows/', WorkflowListCreateView.as_view(), name='workflow-list-create'),
    path('workflows/<uuid:id>/', WorkflowDetailView.as_view(), name='workflow-detail'),
    path('workflows/<uuid:workflow_id>/steps/', WorkflowStepListCreateView.as_view(), name='workflow-step-list-create'),
    path('workflows/<uuid:workflow_id>/steps/<uuid:id>/', WorkflowStepDetailView.as_view(), name='workflow-step-detail'),
    path('workflows/<uuid:workflow_id>/execute/', WorkflowExecuteView.as_view(), name='workflow-execute'),
    path('workflows/<uuid:workflow_id>/execution-status/', WorkflowExecutionStatusView.as_view(), name='workflow-execution-status'),
    path('workflows/<uuid:workflow_id>/steps/<uuid:step_id>/status/', WorkflowStepStatusUpdateView.as_view(), name='workflow-step-status-update'),
    path('workflows/<uuid:workflow_id>/clone/', WorkflowCloneView.as_view(), name='workflow-clone'),
    path('workflows/<uuid:workflow_id>/export/', WorkflowExportView.as_view(), name='workflow-export'),
    path('workflows/import/', WorkflowImportView.as_view(), name='workflow-import'),
    path('workflows/execution-history/', WorkflowExecutionHistoryView.as_view(), name='workflow-execution-history'),
]