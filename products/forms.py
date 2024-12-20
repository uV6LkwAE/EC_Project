
from django import forms
from .models import Product, ProductImage, Comment

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'category', 'condition']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 空の選択肢を削除
        self.fields['category'].choices = Product.CATEGORY_CHOICES

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'order']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'reply_to']  # reply_toをフォームに追加

    reply_to = forms.ModelChoiceField(
        queryset=Comment.objects.all(),
        required=False,  # リプライでない場合は不要
        widget=forms.HiddenInput(),  # フォーム上では表示しない
    )