
from django.db import models
from accounts.models import CustomUser
from products.models import Product

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('order_confirmed', '注文確定'),
        ('pending', '未発送'),
        ('shipped', '発送済み'),
        ('received', '受け取り完了'),
        ('completed', '取引完了'),
    ]
    
    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='transactions_as_buyer')
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='transactions_as_seller')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    shipping_address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 評価を関連付け
    ratings = models.ManyToManyField('TransactionRating', related_name='transactions', blank=True)

    def __str__(self):
        return f"{self.product.title} - {self.get_status_display()}"

    @property
    def average_rating(self):
        # 取引に対する評価（良かった, 残念だった）の計算
        ratings = self.rating.all()  # 評価に関連するすべてのレコードを取得
        if ratings.exists():
            good_count = ratings.filter(rating='good').count()  # 良かったの数
            bad_count = ratings.filter(rating='bad').count()    # 残念だったの数
            total = good_count + bad_count
            if total > 0:
                percentage = (good_count / total) * 100  # 百分率で計算
                return round(percentage, 2)  # 小数点以下2桁まで返す
        return 0  # 評価がない場合は0%


class TransactionRating(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="rating")
    rater = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="ratings")
    rated_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="received_ratings")
    rating = models.CharField(max_length=10, choices=[('good', '良かった'), ('bad', '残念だった')], default='good')
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_good(self):
        return self.rating == 'good'

    @property
    def is_bad(self):
        return self.rating == 'bad'


class TransactionStatusHistory(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=Transaction.STATUS_CHOICES)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Status: {self.status} at {self.changed_at}"