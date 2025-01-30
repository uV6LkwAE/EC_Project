"""
ASGI config for EC_Project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# 環境変数の設定（デフォルトは開発環境）
os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.getenv('DJANGO_SETTINGS_MODULE', 'EC_Project.settings.development'))

# Django の初期化（重要）
django.setup()

# Djangoアプリをロード
django_asgi_app = get_asgi_application()

# Djangoのアプリケーションがロードされた後に `transactions.routing` をインポート
import transactions.routing

# ASGIルーティング設定
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(transactions.routing.websocket_urlpatterns)
    ),
})
