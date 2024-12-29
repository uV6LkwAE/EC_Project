
# from django.shortcuts import render
# from products.models import Product
# from .forms import ProductSearchForm

# def product_search(request):
#     form = ProductSearchForm(request.GET or None)
#     products = Product.objects.all()

#     if form.is_valid():
#         filters = {
#             'price__gte': form.cleaned_data.get('min_price'),
#             'price__lte': form.cleaned_data.get('max_price'),
#             'condition': form.cleaned_data.get('condition') or None,
#             'status': form.cleaned_data.get('status') or None,
#             'category': form.cleaned_data.get('category') or None,
#         }
#         # 動的フィルタリング
#         for field, value in filters.items():
#             if value:
#                 products = products.filter(**{field: value})

#         # その他のフィルタリング
#         if form.cleaned_data.get('title'):
#             products = products.filter(title__icontains=form.cleaned_data['title'])
#         if form.cleaned_data.get('include_keywords'):
#             products = products.filter(description__icontains=form.cleaned_data['include_keywords'])
#         if form.cleaned_data.get('exclude_keywords'):
#             products = products.exclude(description__icontains=form.cleaned_data['exclude_keywords'])
#         if form.cleaned_data.get('user'):
#             products = products.filter(seller__username__icontains=form.cleaned_data['user'])
#         if form.cleaned_data.get('exclude_user'):
#             products = products.exclude(seller__username__icontains=form.cleaned_data['exclude_user'])

#         # デバッグ用にクエリを出力
#         # print(products.query)

#     else:
#         print(form.errors)

#     return render(request, 'search/search_results.html', {'form': form, 'products': products})

from django.views.generic import ListView
from django.db.models import Q
from products.models import Product
from .forms import ProductSearchForm

class ProductListSearchView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 10  # ページネーション

    def get_queryset(self):
        """
        商品一覧、簡易検索、詳細検索を統合したクエリセットを取得
        """
        queryset = Product.objects.all()
        query = self.request.GET.get('q')  # 簡易検索用クエリ
        form = ProductSearchForm(self.request.GET)  # 詳細検索フォーム

        # 簡易検索の処理
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )

        # 詳細検索の処理
        if form.is_valid():
            filters = {
                'price__gte': form.cleaned_data.get('min_price'),
                'price__lte': form.cleaned_data.get('max_price'),
                'condition': form.cleaned_data.get('condition') or None,
                'status': form.cleaned_data.get('status') or None,
                'category': form.cleaned_data.get('category') or None,
            }

            print("Applied filters:", filters)

            for field, value in filters.items():
                if value:
                    queryset = queryset.filter(**{field: value})

            if form.cleaned_data.get('title'):
                queryset = queryset.filter(title__icontains=form.cleaned_data['title'])
            if form.cleaned_data.get('include_keywords'):
                queryset = queryset.filter(description__icontains=form.cleaned_data['include_keywords'])
            if form.cleaned_data.get('exclude_keywords'):
                queryset = queryset.exclude(description__icontains=form.cleaned_data['exclude_keywords'])
            if form.cleaned_data.get('user'):
                queryset = queryset.filter(seller__username__icontains=form.cleaned_data['user'])
            if form.cleaned_data.get('exclude_user'):
                queryset = queryset.exclude(seller__username__icontains=form.cleaned_data['exclude_user'])

        print("Final queryset:", queryset)
        return queryset

    def get_context_data(self, **kwargs):
        """
        コンテキストに検索フォームを追加
        """
        context = super().get_context_data(**kwargs)
        context['search_form'] = ProductSearchForm(self.request.GET or None)
        return context
