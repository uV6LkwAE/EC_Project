
from django.db import models
from accounts.models import CustomUser
from products.models import Product

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', '未発送'),
        ('shipped', '発送済み'),
        ('received', '受け取り完了'),
    ]

    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='transactions_as_buyer')
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='transactions_as_seller')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    shipping_address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.title} - {self.get_status_display()}"
