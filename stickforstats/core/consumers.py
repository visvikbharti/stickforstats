"""
WebSocket consumers for core application functionality.

This module provides WebSocket consumers for real-time updates and notifications.
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for user notifications."""
    
    async def connect(self):
        """Handle WebSocket connection."""
        # Get user from scope (requires AuthMiddlewareStack)
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            # Reject connection if user is not authenticated
            await self.close()
            return
        
        # Create group name for this user's notifications
        self.notification_group_name = f"notifications_{self.user.id}"
        
        # Join group
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        # Accept connection
        await self.accept()
        
        # Send any pending notifications
        await self.send_pending_notifications()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave group
        if hasattr(self, 'notification_group_name'):
            await self.channel_layer.group_discard(
                self.notification_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle received messages from WebSocket."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'mark_read':
                # Mark notification as read
                notification_id = data.get('notification_id')
                if notification_id:
                    await self.mark_notification_read(notification_id)
                    
            elif message_type == 'request_notifications':
                # Client requests notifications
                await self.send_pending_notifications()
                
        except json.JSONDecodeError:
            logger.error(f"Received invalid JSON: {text_data}")
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
    
    @database_sync_to_async
    def get_pending_notifications(self):
        """Get pending notifications for the user."""
        from stickforstats.core.models import Notification
        try:
            # Get unread notifications
            notifications = Notification.objects.filter(
                user=self.user,
                read=False
            ).order_by('-created_at')[:10]
            
            return [
                {
                    'id': str(notif.id),
                    'title': notif.title,
                    'message': notif.message,
                    'notification_type': notif.notification_type,
                    'related_object_type': notif.related_object_type,
                    'related_object_id': notif.related_object_id,
                    'created_at': notif.created_at.isoformat()
                }
                for notif in notifications
            ]
        except Exception as e:
            logger.error(f"Error getting notifications: {str(e)}")
            return []
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark a notification as read."""
        from stickforstats.core.models import Notification
        try:
            notification = Notification.objects.get(id=notification_id, user=self.user)
            notification.read = True
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False
        except Exception as e:
            logger.error(f"Error marking notification read: {str(e)}")
            return False
    
    async def send_pending_notifications(self):
        """Send pending notifications to the client."""
        notifications = await self.get_pending_notifications()
        
        await self.send(text_data=json.dumps({
            'type': 'notifications',
            'notifications': notifications
        }))
    
    async def notification(self, event):
        """Handle notification event from channel layer."""
        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))


class AnalysisProgressConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for analysis progress updates."""
    
    async def connect(self):
        """Handle WebSocket connection."""
        # Get user from scope (requires AuthMiddlewareStack)
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            # Reject connection if user is not authenticated
            await self.close()
            return
        
        # Create group name for this user's analysis updates
        self.analysis_group_name = f"analysis_{self.user.id}"
        
        # Join group
        await self.channel_layer.group_add(
            self.analysis_group_name,
            self.channel_name
        )
        
        # Accept connection
        await self.accept()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave group
        if hasattr(self, 'analysis_group_name'):
            await self.channel_layer.group_discard(
                self.analysis_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle received messages from WebSocket."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'request_status':
                # Client requests status update for a specific analysis
                session_id = data.get('session_id')
                if session_id:
                    await self.send_analysis_status(session_id)
        except json.JSONDecodeError:
            logger.error(f"Received invalid JSON: {text_data}")
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
    
    @database_sync_to_async
    def get_analysis_status(self, session_id):
        """Get status of a specific analysis session."""
        from stickforstats.core.models import AnalysisSession
        try:
            session = AnalysisSession.objects.get(id=session_id, user=self.user)
            return {
                'session_id': str(session.id),
                'status': session.status,
                'progress': 100 if session.status == 'completed' else 
                            0 if session.status == 'failed' else 50,
                'name': session.name,
                'updated_at': session.updated_at.isoformat()
            }
        except AnalysisSession.DoesNotExist:
            return {'error': 'Analysis session not found'}
        except Exception as e:
            logger.error(f"Error getting analysis status: {str(e)}")
            return {'error': str(e)}
    
    async def send_analysis_status(self, session_id):
        """Send analysis status to the client."""
        status = await self.get_analysis_status(session_id)
        
        await self.send(text_data=json.dumps({
            'type': 'analysis_status',
            'data': status
        }))
    
    async def progress_update(self, event):
        """Handle progress update event from channel layer."""
        # Send progress update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'progress_update',
            'data': event['data']
        }))
    
    async def analysis_complete(self, event):
        """Handle analysis complete event from channel layer."""
        # Send completion notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'analysis_complete',
            'data': event['data']
        }))