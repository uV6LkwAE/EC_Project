
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .models import Product, Favorite
from .forms import ProductForm

# 商品出品ビュー
class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/create_product.html'
    # 出品商品にリダイレクトしたい
    success_url = reverse_lazy('products:product_detail')

    def form_valid(self, form):
        # 出品者として現在のログインユーザーを設定
        form.instance.seller = self.request.user
        # ステータスを「販売中」に設定
        form.instance.status = 'available'
        return super().form_valid(form)
    
    def form_invalid(self, form):
        print(form.errors)  # フォームエラーメッセージを表示
        return super().form_invalid(form)


    def get_success_url(self):
        # 商品詳細ページにリダイレクトするためのURLを生成
        return reverse_lazy('products:product_detail', kwargs={'pk': self.object.pk})

# 商品一覧ビュー
class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'  # 使用するテンプレートファイルの指定
    context_object_name = 'products'  # テンプレートで使うコンテキスト名
    paginate_by = 10  # 必要に応じてページネーションを設定

# 商品詳細ビュー
class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ユーザーがログインしている場合にお気に入りの状態を追加
        if self.request.user.is_authenticated:
            context['is_favorited'] = Favorite.objects.filter(
                user=self.request.user, product=self.object
            ).exists()
        else:
            context['is_favorited'] = False
        return context

# 商品編集ビュー
class ProductEditView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_edit.html'

    def get_queryset(self):
        # ログインしているユーザーが出品した商品だけを編集できるようにする
        queryset = super().get_queryset()
        return queryset.filter(seller=self.request.user)

    def get_success_url(self):
        # 商品詳細ページにリダイレクトするためのURLを生成
        return reverse('products:product_detail', kwargs={'pk': self.object.pk})


# 商品削除ビュー
class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/product_delete.html'
    success_url = reverse_lazy('products:product_list')  # 削除後にリダイレクトするURL

    def get_queryset(self):
        # ログインしているユーザーが出品した商品だけを削除できるようにする
        queryset = super().get_queryset()
        return queryset.filter(seller=self.request.user)

# "@login_required" ユーザーがログインしていない場合、ログインページにリダイレクト

@login_required
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)

    if not created:
        # すでにお気に入りの場合は削除
        favorite.delete()

    return redirect('products:product_detail', pk=product.id)

@login_required
def favorite_list(request):
    # ログイン中のユーザーのお気に入り商品を取得
    favorites = Favorite.objects.filter(user=request.user)
    print(f"Favorites for user {request.user}: {favorites}")  # デバッグ用
    products = [favorite.product for favorite in favorites]
    print(f"Products for user {request.user}: {products}")  # デバッグ用
    
    return render(request, 'products/favorite_list.html', {'products': products})
