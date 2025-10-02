"""
ASGI config for event_manager project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import event_manager.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "event_manager.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": event_manager.routing.application,
})
