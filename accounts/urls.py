
from django.urls import path
from django.contrib.auth.views import LogoutView # LogoutViewのみ標準を使用
from .views import SignupView, CustomLoginView, CustomLogoutView, ProfileView, ProfileEditView, AccountDeleteView
from .import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),  # カスタムログインビューを追加
    path('logout/', CustomLogoutView.as_view(), name='logout'), 
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('profile/delete/', AccountDeleteView.as_view(), name='account_delete'),
    path('purchased-items/', views.purchased_items, name='purchased_items'),
    path('sold-items/', views.sold_items, name='sold_items'),
    path('trading-items/', views.trading_items, name='trading_items'),
]
