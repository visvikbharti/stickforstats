"""
Core URL configuration for the StickForStats project.
This enables just the basic URLs.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

# Simple view for testing
def index(request):
    return HttpResponse("<h1>StickForStats Migration Project</h1><p>The server is running with core functionality.</p>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),

    # Core API
    # path('api/v1/core/', include('stickforstats.core.api.urls')),

    # Confidence Intervals API
    path('api/v1/confidence-intervals/', include('stickforstats.confidence_intervals.api.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)