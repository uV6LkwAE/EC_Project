
from django.contrib import admin
from .models import Product, ProductImage

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'price', 'category', 'status', 'created_at')  # 管理画面で表示するフィールド
    list_filter = ('category', 'status', 'condition')  # フィルタリングオプション
    search_fields = ('title', 'description')  # 検索ボックスの対象となるフィールド
    ordering = ('-created_at',)  # デフォルトの並び順を設定

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image', 'order')  # 管理画面で表示するフィールド
    list_filter = ('product',)  # フィルタリングオプション（必要に応じて）
    search_fields = ('product__title',)  # 検索ボックスで商品名で検索可能
    ordering = ('product', 'order')  # デフォルトの並び順を設定
