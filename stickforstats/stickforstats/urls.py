from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include other app URLs
    path('api/confidence-intervals/', include('confidence_intervals.api.urls')),
    # RAG system URLs
    path('rag/', include('rag_system.urls')),
    # Add other app URLs as needed
]