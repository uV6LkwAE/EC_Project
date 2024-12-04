
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.forms.utils import ErrorList
from .models import Product, ProductImage, Favorite
from .forms import ProductForm
import json

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_create.html'  # テンプレート名を修正

    def form_valid(self, form):
        # 新しい画像を取得
        new_images = self.request.FILES.getlist('images')

        # 制約チェック
        error_messages = []

        # 1. 枚数チェック
        if len(new_images) > 10:  # 上限10枚
            error_messages.append(f"画像は合計10枚までアップロード可能です（現在{len(new_images)}枚アップロードしようとしています）。")

        # 2. 各画像のサイズチェック
        for image in new_images:
            if image.size > 10 * 1024 * 1024:  # 10MB制限
                error_messages.append(f"画像「{image.name}」のサイズが10MBを超えています。")

        # エラーがあればテンプレートに表示
        if error_messages:
            for message in error_messages:
                form.add_error(None, message)  # フォームにエラーメッセージを追加
            return self.form_invalid(form)

        # 商品の基本情報を保存
        self.object = form.save(commit=False)
        self.object.seller = self.request.user
        self.object.save()

        # 画像を保存
        for image in new_images:
            ProductImage.objects.create(
                product=self.object,
                image=image,
                order=self.object.images.count()  # 順序を指定
            )

        return super().form_valid(form)

    def get_success_url(self):
        if self.object:
            return reverse('products:product_detail', kwargs={'pk': self.object.pk})
        return reverse('products:product_list')  # フォールバックとして商品一覧にリダイレクト
    
    # No.008 デバッグ
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)

        
    #     print("フォームのクラス:", self.form_class.__name__)
    #     print("Category Choices:", self.form_class.base_fields['category'].choices)
    #     print("Condition Choices:", self.form_class.base_fields['condition'].choices)

    #     return context

class ProductEditView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_edit.html'

    def form_valid(self, form):
        self.object = form.save()

        # 既存画像の枚数を取得
        existing_image_count = self.object.images.count()

        # 新しい画像を取得
        new_images = self.request.FILES.getlist('images')

        # 制約チェック
        total_images = existing_image_count + len(new_images)
        error_messages = []

        # 1. 合計枚数チェック
        if total_images > 10:  # 上限10枚
            excess_count = total_images - 10
            error_messages.append(f"画像は合計10枚までアップロード可能です（現在{existing_image_count}枚、新規{len(new_images)}枚、{excess_count}枚超過）。")

        # 2. 各画像のサイズチェック
        for image in new_images:
            if image.size > 10 * 1024 * 1024:  # 10MB制限
                error_messages.append(f"画像「{image.name}」のサイズが10MBを超えています。")

        # エラーがあればテンプレートに表示
        if error_messages:
            for message in error_messages:
                form.add_error(None, message)  # フォームにエラーメッセージを追加
            return self.form_invalid(form)

        # 新しい画像を保存
        for image in new_images:
            ProductImage.objects.create(
                product=self.object,
                image=image,
                order=self.object.images.count()  # 最後に追加
            )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('products:product_detail', kwargs={'pk': self.object.pk})


class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 10  # ページネーション


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['is_favorited'] = Favorite.objects.filter(
                user=self.request.user, product=self.object
            ).exists()
        else:
            context['is_favorited'] = False
        return context


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/product_delete.html'
    success_url = reverse_lazy('products:product_list')

    def get_queryset(self):
        return super().get_queryset().filter(seller=self.request.user)


@login_required
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)

    if not created:
        favorite.delete()

    return redirect('products:product_detail', pk=product.id)


@login_required
def favorite_list(request):
    favorites = Favorite.objects.filter(user=request.user)
    products = [favorite.product for favorite in favorites]
    return render(request, 'products/favorite_list.html', {'products': products})
