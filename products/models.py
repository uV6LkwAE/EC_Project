
from django.db import models
from accounts.models import CustomUser

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
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='products', verbose_name='出品者') # 出品者が削除された場合、すべての商品レコードも削除
    image = models.ImageField(upload_to='product_images/', verbose_name='商品画像')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name='カテゴリー')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new', verbose_name='状態')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日') # 更新されるたびにフィールドに現在の日時を自動的に設定

    def __str__(self):
        return self.title

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 3 * 1024 * 1024:
                raise ValidationError('画像のアップロードサイズは3MB以下にしてください。')
        return image

        