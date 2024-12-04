
from django.urls import path
from .views import ProductCreateView, ProductEditView, ProductListView, ProductDetailView, ProductDeleteView, toggle_favorite, favorite_list, delete_images

app_name = 'products'

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('create/', ProductCreateView.as_view(), name='product_create'), 
    path('<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('<int:pk>/edit/', ProductEditView.as_view(), name='product_edit'),
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    path('image/<int:image_id>/delete/', delete_images, name='delete_images'),
    path('<int:product_id>/toggle_favorite/', toggle_favorite, name='toggle_favorite'),
    path('favorites/', favorite_list, name='favorite_list'),
]
