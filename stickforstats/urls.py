from stickforstats.health.views import health_check
"""
Main URL configuration for the StickForStats Django project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

# Simple view for testing
def index(request):
    return HttpResponse("<h1>StickForStats Migration Project</h1><p>The server is running.</p>")

urlpatterns = [
    path("health/", health_check, name="health_check"),    path('admin/', admin.site.urls),
    path('', index, name='index'),

    # Core API
    path('api/v1/core/', include('stickforstats.core.api.urls')),

    # Modules - gradually enabling as we fix issues
    path('api/v1/rag/', include('stickforstats.rag_system.api.urls')),
    path('api/v1/confidence-intervals/', include('stickforstats.confidence_intervals.api.urls')),
    path('api/v1/probability-distributions/', include('stickforstats.probability_distributions.api.urls')),
    path('api/v1/sqc-analysis/', include('stickforstats.sqc_analysis.api.urls')),
    path('api/v1/doe-analysis/', include('stickforstats.doe_analysis.api.urls')),
    path('api/v1/pca-analysis/', include('stickforstats.pca_analysis.urls')),
    # Enterprise modules
    # path('api/v1/gpu-engine/', include('stickforstats.gpu_statistical_engine.urls')),  # Temporarily disabled
    # path('api/v1/marketplace/', include('stickforstats.marketplace.urls')),  # Temporarily disabled
    # path('api/v1/collaboration/', include('stickforstats.collaboration.urls')),  # Temporarily disabled
    # path('api/v1/machine-learning/', include('stickforstats.machine_learning.urls')),  # Temporarily disabled while spacy installs
    path('api/v1/advanced-statistics/', include('stickforstats.advanced_statistics.urls')),
    # path('api/v1/automated-reporting/', include('stickforstats.automated_reporting.urls')),  # Temporarily disabled
    # path('api/v1/enterprise-security/', include('stickforstats.enterprise_security.urls')),  # Temporarily disabled
    # path('api/v1/data-visualization/', include('stickforstats.data_visualization.urls')),  # Temporarily disabled
    
    # Workflow automation
    path('api/v1/workflows/', include('stickforstats.workflow_automation.urls')),  # Re-enabled after fixing model conflict
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)