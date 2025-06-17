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
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    
    # Core API
    path('api/v1/core/', include('stickforstats.core.api.urls')),
    
    # MainApp API (core statistical services)
    path('api/v1/mainapp/', include('stickforstats.mainapp.api.urls')),
    
    # Confidence Intervals Module
    path('api/v1/confidence-intervals/', include('stickforstats.confidence_intervals.api.urls')),
    
    # Additional modules will be added as we migrate them
    # path('api/v1/probability-distributions/', include('stickforstats.probability_distributions.api.urls')),
    # path('api/v1/sqc-analysis/', include('stickforstats.sqc_analysis.api.urls')),
    # path('api/v1/doe-analysis/', include('stickforstats.doe_analysis.api.urls')),
    # path('api/v1/pca-analysis/', include('stickforstats.pca_analysis.api.urls')),
    # path('api/v1/rag/', include('stickforstats.rag_system.api.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)