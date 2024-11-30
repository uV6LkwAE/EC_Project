
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.decorators import method_decorator
import json
from .models import Product, ProductImage, Favorite
from .forms import ProductForm
from django.core.exceptions import ValidationError


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_create.html'  # テンプレート名を修正

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.seller = self.request.user
        self.object.save()

        # 画像順序データを取得して保存
        order_data = self.request.POST.get('order_data')
        if order_data:
            for item in json.loads(order_data):
                ProductImage.objects.create(
                    product=self.object,
                    image=self.request.FILES.getlist('images')[int(item['index'])],
                    order=item['order']
                )
        return super().form_valid(form)
    
    def get_success_url(self):
        if self.object:
            return reverse('products:product_detail', kwargs={'pk': self.object.pk})
        return reverse('products:product_list')  # フォールバックとして商品一覧にリダイレクト


class ProductEditView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_edit.html'

    def form_valid(self, form):
        self.object = form.save()

        # 画像順序データを取得
        order_data = self.request.POST.get('order_data')
        if order_data:
            order_data = json.loads(order_data)
            # 既存画像の順序を更新
            for item in order_data:
                if 'id' in item:  # 既存画像
                    image = ProductImage.objects.filter(product=self.object, id=item['id']).first()
                    if image:
                        image.order = item['order']
                        image.save()

            # 新規画像を保存
            new_files = self.request.FILES.getlist('images')
            for item in order_data:
                if 'index' in item:  # 新規画像
                    index = int(item['index'])
                    if index < len(new_files):  # ファイルが存在する場合のみ処理
                        ProductImage.objects.create(
                            product=self.object,
                            image=new_files[index],
                            order=item['order']
                        )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('products:product_detail', kwargs={'pk': self.object.pk})


class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 10


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
        queryset = super().get_queryset()
        return queryset.filter(seller=self.request.user)


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
