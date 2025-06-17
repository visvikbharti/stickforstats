"""
Minimal URL configuration for the StickForStats project.
"""

from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

# Simple view for testing
def index(request):
    return HttpResponse("<h1>StickForStats Migration Project</h1><p>The server is running in minimal mode.</p>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
]