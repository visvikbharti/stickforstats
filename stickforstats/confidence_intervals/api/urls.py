from django.urls import path
from ..views import (
    CalculateConfidenceIntervalView,
    BootstrapConfidenceIntervalView,
    MultipleConfidenceIntervalsView,
    ConfidenceIntervalVisualizationView
)

app_name = 'confidence_intervals_api'

urlpatterns = [
    # Main CI calculation endpoint
    path('calculate/', CalculateConfidenceIntervalView.as_view(), name='calculate'),
    
    # Bootstrap CI endpoint
    path('bootstrap/', BootstrapConfidenceIntervalView.as_view(), name='bootstrap'),
    
    # Multiple CIs with adjustment
    path('multiple/', MultipleConfidenceIntervalsView.as_view(), name='multiple'),
    
    # Custom visualization endpoint
    path('visualize/', ConfidenceIntervalVisualizationView.as_view(), name='visualize'),
]