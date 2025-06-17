from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as token_views
from .views import (
    DatasetViewSet, AnalysisViewSet, VisualizationViewSet,
    ReportViewSet, WorkflowViewSet, GuidanceViewSet, UserPreferenceViewSet,
    StatisticalTestView, DescriptiveStatsView, CorrelationAnalysisView,
    RegressionAnalysisView, TimeSeriesAnalysisView, BayesianAnalysisView,
    ModuleStatusView, ValidateModulesView, TroubleshootModuleView
)
from .auth_views import (
    RegisterView, LoginView, LogoutView, UserProfileView, ChangePasswordView
)
from .advanced_stats_mock import mock_models_list, mock_analysis

router = DefaultRouter()
router.register(r'datasets', DatasetViewSet, basename='dataset')
router.register(r'analyses', AnalysisViewSet, basename='analysis')
router.register(r'visualizations', VisualizationViewSet, basename='visualization')
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'workflows', WorkflowViewSet, basename='workflow')
router.register(r'guidance', GuidanceViewSet, basename='guidance')
router.register(r'preferences', UserPreferenceViewSet, basename='preference')

urlpatterns = [
    path('', include(router.urls)),

    # Authentication endpoints
    path('auth/register/', RegisterView.as_view(), name='api_register'),
    path('auth/login/', LoginView.as_view(), name='api_login'),
    path('auth/logout/', LogoutView.as_view(), name='api_logout'),
    path('auth/profile/', UserProfileView.as_view(), name='api_profile'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='api_change_password'),
    path('auth/token/', token_views.obtain_auth_token, name='api_token_auth'),  # Keep for backward compatibility

    # Statistical Analysis API endpoints
    path('statistics/test/', StatisticalTestView.as_view(), name='statistical_test'),
    path('statistics/descriptive/', DescriptiveStatsView.as_view(), name='descriptive_stats'),
    path('statistics/correlation/', CorrelationAnalysisView.as_view(), name='correlation_analysis'),
    path('statistics/regression/', RegressionAnalysisView.as_view(), name='regression_analysis'),
    path('statistics/time-series/', TimeSeriesAnalysisView.as_view(), name='time_series_analysis'),
    path('statistics/bayesian/', BayesianAnalysisView.as_view(), name='bayesian_analysis'),

    # Module Integration API endpoints
    path('modules/status/', ModuleStatusView.as_view(), name='module_status'),
    path('modules/validate/', ValidateModulesView.as_view(), name='validate_modules'),
    path('modules/troubleshoot/<str:module_name>/', TroubleshootModuleView.as_view(), name='troubleshoot_module'),
    
    # Mock Advanced Statistics endpoints (temporary)
    path('advanced-statistics/models/', mock_models_list, name='mock_advanced_stats_models'),
    path('advanced-statistics/analysis/', mock_analysis, name='mock_advanced_stats_analysis'),
]