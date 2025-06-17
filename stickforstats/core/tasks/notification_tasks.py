"""
Notification tasks for StickForStats application.
"""

import logging

logger = logging.getLogger(__name__)

def send_notification(user_id, title, message, notification_type="info", related_object_type=None, related_object_id=None):
    """
    Send a notification to a user.
    
    This is a placeholder implementation. In a real application, this would be a Celery task
    that sends notifications via email, push notifications, or in-app notifications.
    
    Args:
        user_id (str): The ID of the user to notify
        title (str): The title of the notification
        message (str): The message content
        notification_type (str): The type of notification (info, success, warning, error)
        related_object_type (str, optional): The type of related object
        related_object_id (str, optional): The ID of the related object
    """
    logger.info(
        f"NOTIFICATION to user {user_id}: [{notification_type.upper()}] {title} - {message}"
    )
    
    if related_object_type and related_object_id:
        logger.info(
            f"Related to: {related_object_type} (ID: {related_object_id})"
        )
    
    # In a real implementation, this would:
    # 1. Create a notification in the database
    # 2. Send via appropriate channels (email, push, etc.)
    # 3. Return a notification ID or success status
    
    return {
        'status': 'sent',
        'user_id': user_id,
        'title': title,
        'message': message,
        'type': notification_type
    }

# Make delay a no-op method for compatibility with Celery-style task calls
send_notification.delay = send_notification