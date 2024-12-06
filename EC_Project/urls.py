"""
URL configuration for EC_Project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('products/', include('products.urls', namespace='products')),  # ここを確認
    path('search/', include('search.urls', namespace='search')),
    path('transactions/', include('transactions.urls')),
    # path('accounts/', include('allauth.urls')),  # allauthのURL
]

# メディアファイルのURL設定
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # if settings.DEBUG:: 開発環境でのみメディアファイルの配信を有効にするための設定です。
    # 本番環境では、Webサーバー（例：NGINX）でメディアファイルを配信するように設定する必要があります。