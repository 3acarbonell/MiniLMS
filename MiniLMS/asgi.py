"""
ASGI config for MiniLMS project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""
import os
import django

from django.core.asgi import get_asgi_application

from core.templates.core.dashboard.board.board import BoardConsumer
from core.templates.core.course.chat.chat import ChatConsumer
from django.urls import re_path
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MiniLMS.settings')
django.setup()
django_asgi_app = get_asgi_application()


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                re_path('ws/chat/', ChatConsumer.as_asgi()),
                re_path('ws/board/', BoardConsumer.as_asgi())
            ])
        )
    )
})
