import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import JSONField  # Using Django's built-in JSONField

User = get_user_model()

# Import models from mainapp for backward compatibility
# This allows other modules to continue importing from stickforstats.core.models
from stickforstats.mainapp.models.analysis import AnalysisSession, AnalysisResult, Dataset, Visualization

# Simplified model just to get the server running
class Analysis(models.Model):
    """
    Base model for all analyses performed in the system.
    Stores metadata and references to data, parameters, and results.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    analysis_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    parameters = JSONField(default=dict)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.analysis_type})"