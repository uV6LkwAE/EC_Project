
from django.urls import path
from django.contrib.auth.views import LogoutView # LogoutViewのみ標準を使用
from .views import SignupView, CustomLoginView, CustomLogoutView, MypageView, MypageEditView, ProfileView, AccountDeleteView, toggle_follow, follow_list
from .import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),  # カスタムログインビューを追加
    path('logout/', CustomLogoutView.as_view(), name='logout'), 
    path('profile/', MypageView.as_view(), name='profile'),
    path('profile/edit/', MypageEditView.as_view(), name='profile_edit'),
    path('profile/delete/', AccountDeleteView.as_view(), name='account_delete'),
    path('profile/<int:user_id>/', ProfileView.as_view(), name='user_profile'), 
    path('purchased-items/', views.purchased_items, name='purchased_items'),
    path('sold-items/', views.sold_items, name='sold_items'),
    path('trading-items/', views.trading_items, name='trading_items'),
    path('follow-list/', views.follow_list, name='follow_list'),
    path('toggle-follow/', views.toggle_follow, name='toggle_follow'),
    path('delete-icon/', views.delete_icon, name='delete_icon'),
    path('upload-icon/', views.upload_icon, name='upload_icon'),
]
