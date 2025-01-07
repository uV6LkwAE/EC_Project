
from django import forms
from .models import TransactionRating

class TransactionRatingForm(forms.ModelForm):
    class Meta:
        model = TransactionRating
        fields = ['rating', 'comment']

    # 「良かった」「残念だった」の選択肢をラジオボタンで表示
    RATING_CHOICES = [
        ('good', '良かった'),
        ('bad', '残念だった'),
    ]

    rating = forms.ChoiceField(choices=RATING_CHOICES, widget=forms.RadioSelect, label="評価")
    comment = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'コメントを入力してください', 'rows': 4}), required=False, label="コメント")
