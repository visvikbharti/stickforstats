"""
ASGI config for stickforstats project.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os
import logging
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stickforstats.settings')

# Initialize Django ASGI application early
django_asgi_app = get_asgi_application()

# Import the routing module
from stickforstats.routing import application as routing_application

# Initialize the WebSocket connection manager
logger = logging.getLogger(__name__)
try:
    from stickforstats.rag_system.services.websocket_manager import connection_manager
    import asyncio
    
    # Define a function to start the background tasks for the connection manager
    async def on_startup():
        logger.info("Starting WebSocket connection manager background tasks")
        await connection_manager.start_background_tasks()
    
    # Schedule the startup tasks to run when the ASGI application starts
    # This will only execute once when the ASGI application starts
    asyncio.create_task(on_startup())
    logger.info("Initialized WebSocket connection manager")
except (ImportError, Exception) as e:
    logger.warning(f"Failed to initialize WebSocket connection manager: {str(e)}")

# Configure the ASGI application
application = ProtocolTypeRouter({
    # Django's ASGI application for traditional HTTP requests
    "http": django_asgi_app,
    
    # WebSocket handler (from routing module)
    "websocket": routing_application.protocol_type_handlers["websocket"],
})