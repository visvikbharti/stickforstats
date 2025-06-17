from django.urls import path, include

urlpatterns = [
    path('api/', include('stickforstats.rag_system.api.urls')),
]