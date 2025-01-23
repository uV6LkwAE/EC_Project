
# from django.views.generic import ListView
# from django.db.models import Q
# from products.models import Product
# from .forms import ProductSearchForm
# from django.core.paginator import Paginator
# from urllib.parse import unquote
# from django.utils.http import urlencode

# class ProductListSearchView(ListView):
#     model = Product
#     template_name = 'products/product_list.html'
#     context_object_name = 'products'
#     paginate_by = 10  # 1ページあたりの表示商品数

#     def get_queryset(self):
#         """
#         商品一覧、簡易検索、詳細検索を統合したクエリセットを取得
#         """
#         print("Original Request GET parameters:", self.request.GET)
        
#         # 空白を取り除いたクエリパラメータを使用
#         cleaned_get = self.request.GET.copy()  # コピーして操作する
#         cleaned_get = {key.strip(): value for key, value in cleaned_get.items()}  # 空白を取り除く

#         # デバッグ用：クリーンされたGETパラメータを表示
#         print("Cleaned Request GET parameters:", cleaned_get)

#         queryset = Product.objects.all()
#         query = cleaned_get.get('q')  # 簡易検索用クエリ
#         form = ProductSearchForm(cleaned_get)  # 詳細検索フォーム

#         # 簡易検索の処理
#         if query:
#             queryset = queryset.filter(
#                 Q(title__icontains=query) | Q(description__icontains=query)
#             )

#         # 詳細検索の処理
#         if form.is_valid():
#             filters = {
#                 'price__gte': form.cleaned_data.get('min_price'),
#                 'price__lte': form.cleaned_data.get('max_price'),
#                 'condition': form.cleaned_data.get('condition') or None,
#                 'status': form.cleaned_data.get('status') or None,
#                 'category': form.cleaned_data.get('category') or None,
#             }

#             for field, value in filters.items():
#                 if value:
#                     queryset = queryset.filter(**{field: value})

#             if form.cleaned_data.get('title'):
#                 queryset = queryset.filter(title__icontains=form.cleaned_data['title'])
#             if form.cleaned_data.get('include_keywords'):
#                 queryset = queryset.filter(description__icontains=form.cleaned_data['include_keywords'])
#             if form.cleaned_data.get('exclude_keywords'):
#                 queryset = queryset.exclude(description__icontains=form.cleaned_data['exclude_keywords'])
#             if form.cleaned_data.get('user'):
#                 queryset = queryset.filter(seller__username__icontains=form.cleaned_data['user'])
#             if form.cleaned_data.get('exclude_user'):
#                 queryset = queryset.exclude(seller__username__icontains=form.cleaned_data['exclude_user'])

#         return queryset

#     def get_context_data(self, **kwargs):
#         """
#         コンテキストに検索フォームを追加
#         """
#         context = super().get_context_data(**kwargs)

#         cleaned_get = self.request.GET.copy()  # クエリパラメータのコピー

#         # 空のパラメータがあればそのまま保持しつつ、空白を削除
#         for key, value in cleaned_get.items():
#             if not value:  # 空の値の場合はそのまま
#                 cleaned_get[key] = ''
#             else:
#                 cleaned_get[key] = value.strip()  # 空白を削除

#         # パラメータ間の不要な空白を削除したURLを生成
#         encoded_params = urlencode(cleaned_get, doseq=True)
#         context['encoded_query_params'] = encoded_params

#         # 他のコンテキストデータ
#         context['search_form'] = ProductSearchForm(cleaned_get or None)
#         context['query_params'] = cleaned_get  # クリーンされたパラメータをテンプレートに渡す

#         return context


from django.views.generic import ListView
from django.db.models import Q
from products.models import Product
from .forms import ProductSearchForm
from django.core.paginator import Paginator
from urllib.parse import unquote
from django.utils.http import urlencode

# class ProductListSearchView(ListView):
#     model = Product
#     template_name = 'products/product_list.html'
#     context_object_name = 'products'
#     paginate_by = 10  # 1ページあたりの表示商品数

#     def get_queryset(self):
#         """
#         商品一覧、簡易検索、詳細検索を統合したクエリセットを取得
#         """
#         print("Request.GET before cleaning:", self.request.GET)

#         # 空白を取り除いたクエリパラメータを使用
#         cleaned_get = self.request.GET.copy()  # コピーして操作する
#         cleaned_get = {key.strip(): value[0].strip() if isinstance(value, list) else value.strip() 
#                for key, value in self.request.GET.items()}

#         # 'page'がcleaned_getに含まれているかを確認
#         if 'page' in cleaned_get:
#             print("Page parameter found:", cleaned_get['page'])
        
#         # デバッグ用：クリーンされたGETパラメータを表示
#         print("Request.GET after cleaning:", cleaned_get)

#         queryset = Product.objects.all()
#         query = cleaned_get.get('q')  # 簡易検索用クエリ
#         form = ProductSearchForm(cleaned_get)  # 詳細検索フォーム

#         # 簡易検索の処理
#         if query:
#             queryset = queryset.filter(
#                 Q(title__icontains=query) | Q(description__icontains=query)
#             )

#         # 詳細検索の処理
#         if form.is_valid():
#             filters = {
#                 'price__gte': form.cleaned_data.get('min_price'),
#                 'price__lte': form.cleaned_data.get('max_price'),
#                 'condition': form.cleaned_data.get('condition') or None,
#                 'status': form.cleaned_data.get('status') or None,
#                 'category': form.cleaned_data.get('category') or None,
#             }

#             for field, value in filters.items():
#                 if value:
#                     queryset = queryset.filter(**{field: value})

#             if form.cleaned_data.get('title'):
#                 queryset = queryset.filter(title__icontains=form.cleaned_data['title'])
#             if form.cleaned_data.get('include_keywords'):
#                 queryset = queryset.filter(description__icontains=form.cleaned_data['include_keywords'])
#             if form.cleaned_data.get('exclude_keywords'):
#                 queryset = queryset.exclude(description__icontains=form.cleaned_data['exclude_keywords'])
#             if form.cleaned_data.get('user'):
#                 queryset = queryset.filter(seller__username__icontains=form.cleaned_data['user'])
#             if form.cleaned_data.get('exclude_user'):
#                 queryset = queryset.exclude(seller__username__icontains=form.cleaned_data['exclude_user'])

#         return queryset

#     def get_context_data(self, **kwargs):
#         """
#         コンテキストに検索フォームを追加
#         """
#         context = super().get_context_data(**kwargs)

#         cleaned_get = self.request.GET.copy()  # クエリパラメータのコピー

#         # 空白を削除
#         for key, value in cleaned_get.items():
#             if isinstance(value, list):
#                 cleaned_get[key] = [v.strip() for v in value if v.strip()]
#             else:
#                 cleaned_get[key] = value.strip() if value.strip() else ''  # 空白を削除

#         # パラメータ間の不要な空白を削除したURLを生成
#         encoded_params = urlencode(cleaned_get, doseq=True)
#         context['encoded_query_params'] = encoded_params

#         # 他のコンテキストデータ
#         context['search_form'] = ProductSearchForm(cleaned_get or None)
#         context['query_params'] = cleaned_get  # クリーンされたパラメータをテンプレートに渡す
#         context['encoded_query_params'] = urlencode(cleaned_get, doseq=True)

#         return context


# class ProductListSearchView(ListView):
#     model = Product
#     template_name = 'products/product_list.html'
#     context_object_name = 'products'
#     paginate_by = 10  # 1ページあたりの表示商品数

#     def get_queryset(self):
#         """
#         商品一覧、簡易検索、詳細検索を統合したクエリセットを取得
#         """
#         # リクエストパラメータを取得
#         cleaned_get = self.request.GET.copy()  # コピーして操作する
        
#         # 空白を削除（キーと値両方）
#         cleaned_get = {key.strip(): value[0].strip() if isinstance(value, list) else value.strip() 
#                        for key, value in cleaned_get.items()}

#         # デバッグ：空白削除後のクエリパラメータを出力
#         print("Cleaned GET parameters:", cleaned_get)

#         # 並び替えの条件を取得（クエリパラメータから）
#         sort_by = self.request.GET.get('sort_by', 'created_at')  # デフォルトは'created_at'で並び替え
#         sort_order = self.request.GET.get('sort_order', 'desc')  # デフォルトは降順

#         # 並び替え条件を選択
#         if sort_by == 'title':
#             sort_by = 'title'
#         elif sort_by == 'price':
#             sort_by = 'price'
#         elif sort_by == 'created_at':  # 新しい順または古い順
#             sort_by = 'created_at'

#         # 昇順/降順
#         if sort_order == 'asc':
#             sort_by = sort_by
#         elif sort_order == 'desc':
#             sort_by = f'-{sort_by}'


#         queryset = Product.objects.all()
#         query = cleaned_get.get('q')  # 簡易検索用クエリ
#         form = ProductSearchForm(cleaned_get)  # 詳細検索フォーム

#         # 簡易検索の処理
#         if query:
#             queryset = queryset.filter(
#                 Q(title__icontains=query) | Q(description__icontains=query)
#             )

#         # 詳細検索の処理
#         if form.is_valid():
#             filters = {
#                 'price__gte': form.cleaned_data.get('min_price'),
#                 'price__lte': form.cleaned_data.get('max_price'),
#                 'condition': form.cleaned_data.get('condition') or None,
#                 'status': form.cleaned_data.get('status') or None,
#                 'category': form.cleaned_data.get('category') or None,
#             }

#             for field, value in filters.items():
#                 if value:
#                     queryset = queryset.filter(**{field: value})

#             if form.cleaned_data.get('title'):
#                 queryset = queryset.filter(title__icontains=form.cleaned_data['title'])
#             if form.cleaned_data.get('include_keywords'):
#                 queryset = queryset.filter(description__icontains=form.cleaned_data['include_keywords'])
#             if form.cleaned_data.get('exclude_keywords'):
#                 queryset = queryset.exclude(description__icontains=form.cleaned_data['exclude_keywords'])
#             if form.cleaned_data.get('user'):
#                 queryset = queryset.filter(seller__username__icontains=form.cleaned_data['user'])
#             if form.cleaned_data.get('exclude_user'):
#                 queryset = queryset.exclude(seller__username__icontains=form.cleaned_data['exclude_user'])

#         return queryset

#     def get_context_data(self, **kwargs):
#         """
#         コンテキストに検索フォームを追加
#         """
#         context = super().get_context_data(**kwargs)

#         # クエリパラメータをコピー
#         cleaned_get = self.request.GET.copy()  

#         # 空白削除（キーと値両方）
#         cleaned_get = {key.strip(): value[0].strip() if isinstance(value, list) else value.strip() 
#                        for key, value in cleaned_get.items()}

#         # エンコードされたパラメータを生成
#         encoded_params = urlencode(cleaned_get, doseq=True)
#         context['encoded_query_params'] = encoded_params

#         # クリーンされたパラメータをテンプレートに渡す
#         context['query_params'] = cleaned_get  

#         return context


class ProductListSearchView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12 # 1ページあたりの表示商品数

    def get_queryset(self):
        """
        商品一覧、簡易検索、詳細検索を統合したクエリセットを取得
        """
        # リクエストパラメータを取得
        cleaned_get = self.request.GET.copy()  # コピーして操作する
        
        # 空白を削除（キーと値両方）
        cleaned_get = {key.strip(): value[0].strip() if isinstance(value, list) else value.strip() 
                       for key, value in cleaned_get.items()}

        # 並び替えの条件を取得（クエリパラメータから）
        sort_by = self.request.GET.get('sort_by', 'created_at')  # デフォルトは'created_at'で並び替え
        sort_order = self.request.GET.get('sort_order', 'desc')  # デフォルトは降順

        # 並び替え条件を選択
        if sort_by == 'title':
            sort_by = 'title'
        elif sort_by == 'price':
            sort_by = 'price'
        elif sort_by == 'created_at':  # 新しい順または古い順
            sort_by = 'created_at'

        # 昇順/降順
        if sort_order == 'asc':
            queryset = Product.objects.all().order_by(sort_by)
        elif sort_order == 'desc':
            queryset = Product.objects.all().order_by(f'-{sort_by}')  # 降順

        # 検索条件を適用
        queryset = self.apply_search_filters(queryset, cleaned_get)

        return queryset

    def apply_search_filters(self, queryset, cleaned_get):
        """
        商品の検索条件を適用する
        """
        query = cleaned_get.get('q')  # 簡易検索用クエリ
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )

        # 詳細検索の処理
        form = ProductSearchForm(cleaned_get)  # 詳細検索フォーム
        if form.is_valid():
            filters = {
                'price__gte': form.cleaned_data.get('min_price'),
                'price__lte': form.cleaned_data.get('max_price'),
                'condition': form.cleaned_data.get('condition') or None,
                'status': form.cleaned_data.get('status') or None,
                'category': form.cleaned_data.get('category') or None,
            }

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

        return queryset

    def get_context_data(self, **kwargs):
        """
        コンテキストに検索フォームを追加
        """
        context = super().get_context_data(**kwargs)

        queryset = self.get_queryset()

        # クエリパラメータをコピー
        cleaned_get = self.request.GET.copy()  

        # 空白削除（キーと値両方）
        cleaned_get = {key.strip(): value[0].strip() if isinstance(value, list) else value.strip() 
                       for key, value in cleaned_get.items()}

        # エンコードされたパラメータを生成
        encoded_params = urlencode(cleaned_get, doseq=True)
        context['encoded_query_params'] = encoded_params

        # クリーンされたパラメータをテンプレートに渡す
        context['query_params'] = cleaned_get  

        # オブジェクトの数をテンプレートに渡し、10個以下であるかの判定をテンプレートで行う
        context['object_count'] = queryset.count()
        
        return context
