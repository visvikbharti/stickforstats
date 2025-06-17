from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'documents', views.DocumentViewSet, basename='document')
router.register(r'conversations', views.ConversationViewSet, basename='conversation')

# URL patterns
urlpatterns = [
    # Router generated URLs
    path('', include(router.urls)),
    
    # Custom view URLs
    path('query/', views.QueryView.as_view(), name='query'),
    path('feedback/', views.FeedbackView.as_view(), name='feedback'),
    path('recent-queries/', views.RecentQueriesView.as_view(), name='recent-queries'),
    
    # Cache management endpoints
    path('cache/stats/', views.CacheStatsView.as_view(), name='cache-stats'),
    path('cache/manage/', views.CacheManagementView.as_view(), name='cache-manage'),
    
    # Monitoring endpoints
    path('monitoring/dashboard/', views.MonitoringDashboardView.as_view(), name='monitoring-dashboard'),
    path('monitoring/alerts/', views.AlertingView.as_view(), name='monitoring-alerts'),
    
    # Add Prometheus metrics endpoint
    # path('metrics/', include('django_prometheus.urls')),  # Temporarily disabled
]