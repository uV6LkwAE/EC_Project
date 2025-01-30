
from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('initiate/<int:product_id>/', views.initiate_transaction, name='initiate_transaction'),
    path('detail/<int:transaction_id>/', views.transaction_detail, name='transaction_detail'),
    path('update/<int:transaction_id>/', views.update_transaction_status, name='update_transaction_status'),
    path('rating/<int:transaction_id>/', views.submit_transaction_rating, name='submit_transaction_rating'),
    # チャット取得用エンドポイント
    path('chat/<int:transaction_id>/', views.transaction_detail, name='chat_detail'),
]
