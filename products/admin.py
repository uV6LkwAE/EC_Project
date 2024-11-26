
from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'price', 'category', 'status', 'created_at')  # 管理画面で表示するフィールド
    list_filter = ('category', 'status', 'condition')  # フィルタリングオプション
    search_fields = ('title', 'description')  # 検索ボックスの対象となるフィールド
    ordering = ('-created_at',)  # デフォルトの並び順を設定
