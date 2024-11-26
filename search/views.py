
from django.shortcuts import render
from products.models import Product
from .forms import ProductSearchForm

def product_search(request):
    form = ProductSearchForm(request.GET or None)
    products = Product.objects.all()

    if form.is_valid():
        filters = {
            'price__gte': form.cleaned_data.get('min_price'),
            'price__lte': form.cleaned_data.get('max_price'),
            'condition': form.cleaned_data.get('condition') or None,
            'status': form.cleaned_data.get('status') or None,
            'category': form.cleaned_data.get('category') or None,
        }
        # 動的フィルタリング
        for field, value in filters.items():
            if value:
                products = products.filter(**{field: value})

        # その他のフィルタリング
        if form.cleaned_data.get('title'):
            products = products.filter(title__icontains=form.cleaned_data['title'])
        if form.cleaned_data.get('include_keywords'):
            products = products.filter(description__icontains=form.cleaned_data['include_keywords'])
        if form.cleaned_data.get('exclude_keywords'):
            products = products.exclude(description__icontains=form.cleaned_data['exclude_keywords'])
        if form.cleaned_data.get('user'):
            products = products.filter(seller__username__icontains=form.cleaned_data['user'])
        if form.cleaned_data.get('exclude_user'):
            products = products.exclude(seller__username__icontains=form.cleaned_data['exclude_user'])

        # デバッグ用にクエリを出力
        # print(products.query)

    else:
        print(form.errors)

    return render(request, 'search/search_results.html', {'form': form, 'products': products})
