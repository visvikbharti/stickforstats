import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from confidence_intervals.api.routing import websocket_urlpatterns as ci_websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stickforstats.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            ci_websocket_urlpatterns
            # Add other app WebSocket routing here
        )
    ),
})