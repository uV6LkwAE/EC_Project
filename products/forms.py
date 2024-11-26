
from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'title',
            'description',
            'price',
            'image',
            'category',
            'condition',
        ]

# forms.pyからsellerを削除
