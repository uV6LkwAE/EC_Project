
from django.db import models
from django.conf import settings
from transactions.models import Transaction

class Review(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_reviews')
    reviewee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name="評価")  # 1～5の評価
    comment = models.TextField(blank=True, verbose_name="コメント")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('transaction', 'reviewer')  # 同一の取引で同じ人が複数回評価するのを防ぐ

    def __str__(self):
        return f"Review by {self.reviewer} for {self.reviewee} - Rating: {self.rating}"
