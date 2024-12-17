
from django.db import models
from django.urls import reverse
from accounts.models import CustomUser
from django.conf import settings
from django.core.exceptions import ValidationError

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('electronics', '電子機器'),
        ('furniture', '家具'),
        ('clothing', '衣料品'),
    ]

    STATUS_CHOICES = [
        ('available', '販売中'),
        ('sold_out', '売り切れ'),
    ]

    CONDITION_CHOICES = [
        ('new', '新品'),
        ('unused', '未使用'),
        ('used', '中古'),
        ('refurbished', 'リファービッシュ品'),
    ]

    title = models.CharField(max_length=30, verbose_name='商品名')
    description = models.TextField(verbose_name='商品詳細')
    price = models.IntegerField(verbose_name='価格')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, verbose_name='販売状況', default='available')
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='products', verbose_name='出品者')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name='カテゴリー')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new', verbose_name='状態')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'pk': self.pk})

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE, verbose_name='商品')
    image = models.ImageField(upload_to='product_images/', verbose_name='商品画像')
    order = models.PositiveIntegerField(default=0, verbose_name='表示順')

    class Meta:
        ordering = ['order']
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'

    def clean(self):
        super().clean()
        if self.image.size > 10 * 1024 * 1024:  # 10MB以下のサイズ制限
            raise ValidationError('画像のアップロードサイズは10MB以下にしてください。')

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'

    def __str__(self):
        return f"{self.user.username} -> {self.product.title}"


class Comment(models.Model):
    product = models.ForeignKey(Product, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        return f"Comment by {self.user} on {self.product}"