"""
Celery configuration for StickForStats.

This module configures Celery for asynchronous task processing,
particularly for computationally intensive statistical operations.
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stickforstats.settings')

# Create the Celery application
app = Celery('stickforstats')

# Configure Celery using Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

# Define periodic tasks
app.conf.beat_schedule = {
    'cleanup-expired-sessions': {
        'task': 'stickforstats.core.tasks.cleanup_expired_sessions',
        'schedule': crontab(hour=2, minute=0),  # Run at 2:00 AM every day
    },
    'cleanup-temporary-files': {
        'task': 'stickforstats.core.tasks.cleanup_temporary_files',
        'schedule': crontab(hour=3, minute=0),  # Run at 3:00 AM every day
    },
    'update-rag-system-index': {
        'task': 'stickforstats.rag_system.tasks.update_vector_index',
        'schedule': crontab(hour=4, minute=0),  # Run at 4:00 AM every day
    },
}