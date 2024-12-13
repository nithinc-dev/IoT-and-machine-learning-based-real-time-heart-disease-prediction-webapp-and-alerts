import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import heartApp.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Heart_Proj.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            heartApp.routing.websocket_urlpatterns
        )
    ),
})