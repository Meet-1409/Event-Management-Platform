from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from communications.consumers import AdvancedChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/advanced-chat/(?P<room_id>\w+)/$', AdvancedChatConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    # 'http': get_asgi_application(),  # Already handled in asgi.py
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
}) 