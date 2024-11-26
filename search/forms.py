
from django import forms
from products.models import Product

class ProductSearchForm(forms.Form):
    min_price = forms.IntegerField(required=False, label='最低価格')
    max_price = forms.IntegerField(required=False, label='最高価格')
    condition = forms.ChoiceField(
        choices=[('', '---------')] + list(Product.CONDITION_CHOICES),
        required=False,
        label='状態'
    )
    status = forms.ChoiceField(
        choices=[('', '---------')] + list(Product.STATUS_CHOICES),
        required=False,
        label='ステータス'
    )
    category = forms.ChoiceField(
        choices=[('', '---------')] + list(Product.CATEGORY_CHOICES),
        required=False,
        label='カテゴリー'
    )
    title = forms.CharField(required=False, label='タイトル', max_length=100)
    include_keywords = forms.CharField(required=False, label='キーワード（必ず含む）', max_length=100)
    exclude_keywords = forms.CharField(required=False, label='キーワード（含まない）', max_length=100)
    user = forms.CharField(required=False, label='ユーザー名', max_length=100)
    exclude_user = forms.CharField(required=False, label='特定のユーザーを非表示', max_length=100)

    def __init__(self, *args, **kwargs):
        super(ProductSearchForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.initial = ''
