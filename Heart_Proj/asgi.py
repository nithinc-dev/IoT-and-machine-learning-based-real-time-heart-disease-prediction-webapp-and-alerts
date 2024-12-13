import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import heartApp.routing  # Make sure 'heartApp' is the correct app name where your routing is defined

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Heart_Proj.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # For regular HTTP requests
    "websocket": AuthMiddlewareStack(  # For WebSocket connections
        URLRouter(
            heartApp.routing.websocket_urlpatterns  # Your WebSocket URL routing from the 'heartApp'
        )
    ),
})
