
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.forms.utils import ErrorList
from .models import Product, ProductImage, Favorite
from .forms import ProductForm
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging

# class ProductCreateView(LoginRequiredMixin, CreateView):
#     model = Product
#     form_class = ProductForm
#     template_name = 'products/product_create.html'

#     def form_valid(self, form):
#         # 商品の基本情報を保存
#         self.object = form.save(commit=False)
#         self.object.seller = self.request.user
#         self.object.save()

#         # 新しい画像を取得
#         new_images = self.request.FILES.getlist('images')

#         # 削除対象の画像を取得
#         deleted_images = self.request.POST.get('deleted_images', '[]')
#         try:
#             deleted_images = json.loads(deleted_images)
#             logger.debug(f"Received deleted images data: {deleted_images}")
#         except json.JSONDecodeError:
#             deleted_images = []
#             logger.error(f"Invalid deleted images data: {deleted_images}")

#         # 並び順データを取得
#         order_data = self.request.POST.get('order_data', '[]')
#         try:
#             order_data = json.loads(order_data)
#             logger.debug(f"Received order data: {order_data}")
#         except json.JSONDecodeError:
#             order_data = []
#             logger.error(f"Invalid order data: {order_data}")

#         # 制約チェック
#         error_messages = []

#         # 1. 削除後の合計枚数チェック
#         remaining_images = [img for idx, img in enumerate(new_images) if idx not in deleted_images]
#         if len(remaining_images) > 10:  # 上限10枚
#             error_messages.append(
#                 f"画像は合計10枚までアップロード可能です（現在{len(remaining_images)}枚アップロードしようとしています）。"
#             )

#         # 2. 各画像のサイズチェック
#         for image in remaining_images:
#             if image.size > 10 * 1024 * 1024:  # 10MB制限
#                 error_messages.append(f"画像「{image.name}」のサイズが10MBを超えています。")

#         # エラーがあればテンプレートに表示
#         if error_messages:
#             for message in error_messages:
#                 form.add_error(None, message)  # フォームにエラーメッセージを追加
#             return self.form_invalid(form)

#         # 残った画像を保存
#         for image in remaining_images:
#             ProductImage.objects.create(
#                 product=self.object,
#                 image=image,
#                 order=self.object.images.count()  # 順序を指定
#             )

#         return super().form_valid(form)

#     def get_success_url(self):
#         if self.object:
#             return reverse('products:product_detail', kwargs={'pk': self.object.pk})
#         return reverse('products:product_list')  # フォールバックとして商品一覧にリダイレクト
    
#     # No.008 デバッグ
#     # def get_context_data(self, **kwargs):
#     #     context = super().get_context_data(**kwargs)

        
#     #     print("フォームのクラス:", self.form_class.__name__)
#     #     print("Category Choices:", self.form_class.base_fields['category'].choices)
#     #     print("Condition Choices:", self.form_class.base_fields['condition'].choices)

#     #     return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_create.html'

    def form_valid(self, form):
        # 商品の基本情報を保存
        self.object = form.save(commit=False)
        self.object.seller = self.request.user
        self.object.save()

        # 新しい画像を取得
        new_images = self.request.FILES.getlist('images')

        # 並び順データを取得
        order_data = self.request.POST.get('order_data', '[]')
        try:
            order_data = json.loads(order_data)
            logger.debug(f"Received order data: {order_data}")
        except json.JSONDecodeError:
            order_data = []
            logger.error(f"Invalid order data: {order_data}")

        # 制約チェック
        error_messages = []

        # 合計枚数チェック
        if len(new_images) > 10:  # 上限10枚
            error_messages.append(
                f"画像は合計10枚までアップロード可能です（現在{len(new_images)}枚選択されています）。"
            )

        # 各画像のサイズチェック
        for image in new_images:
            if image.size > 10 * 1024 * 1024:  # 10MB制限
                error_messages.append(f"画像「{image.name}」のサイズが10MBを超えています。")

        # エラーがあればテンプレートに表示
        if error_messages:
            for message in error_messages:
                form.add_error(None, message)  # フォームにエラーメッセージを追加
            return self.form_invalid(form)

        # 削除対象の画像の処理
        deleted_images = self.request.POST.get('deleted_images', '[]')
        try:
            deleted_images = json.loads(deleted_images)
            logger.debug(f"Received deleted images data: {deleted_images}")
        except json.JSONDecodeError:
            deleted_images = []
            logger.error(f"Invalid deleted images data: {deleted_images}")

        # 一時IDと実際のデータベースIDをマッピング
        temp_id_to_image = {}

        # 新規画像を保存し、一時IDを割り当てる
        for idx, image in enumerate(new_images):
            product_image = ProductImage.objects.create(
                product=self.object,
                image=image,
                order=idx  # 一時的な順序
            )
            temp_id_to_image[f"temp-{idx + 1}"] = product_image.id

        # 並び順を適用
        for item in order_data:
            temp_id = item.get('id')
            order = item.get('order')
            if temp_id and temp_id.startswith('temp-') and temp_id in temp_id_to_image:
                db_id = temp_id_to_image[temp_id]
                ProductImage.objects.filter(id=db_id, product=self.object).update(order=order)

        # 削除された画像を処理
        for temp_id in deleted_images:
            if temp_id.startswith('temp-') and temp_id in temp_id_to_image:
                db_id = temp_id_to_image[temp_id]
                ProductImage.objects.filter(id=db_id, product=self.object).delete()

        logger.debug(f"Mapped temp IDs to DB IDs: {temp_id_to_image}")

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
        # フォームの基本情報を保存
        self.object = form.save()

        # 並び替えデータの処理
        order_data = self.request.POST.get('order_data', '[]')
        try:
            order_data = json.loads(order_data)
            for item in order_data:
                image_id = item.get('id')
                order = item.get('order')
                if image_id is not None and order is not None:
                    ProductImage.objects.filter(id=image_id, product=self.object).update(order=order)
            logger.debug(f"Order data processed successfully: {order_data}")
        except json.JSONDecodeError:
            logger.error(f"Invalid order data: {order_data}")

        # 削除された画像の処理
        deleted_images = self.request.POST.get('deleted_images', '[]')
        try:
            deleted_images = json.loads(deleted_images)
            for image_id in deleted_images:
                ProductImage.objects.filter(id=image_id, product=self.object).delete()
            logger.debug(f"Deleted images processed successfully: {deleted_images}")
        except json.JSONDecodeError:
            logger.error(f"Invalid deleted images data: {deleted_images}")

        # 新しい画像の保存
        new_images = self.request.FILES.getlist('images')
        existing_image_count = self.object.images.count()
        total_images = existing_image_count + len(new_images)

        # 制約チェック
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
        logger.debug(f"New images uploaded successfully: {[image.name for image in new_images]}")

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


# 画像削除関連のバグが再発生する可能性があるため残しておく

# ログ設定
logger = logging.getLogger(__name__)

@csrf_exempt
def delete_images(request, image_id):
    logger.debug(f"Received request to delete image with ID: {image_id}")
    
    if request.method == 'POST':
        try:
            # 指定された画像を取得
            image = get_object_or_404(ProductImage, id=image_id)
            logger.debug(f"Found image: {image.image.url}")
            
            # 画像を削除
            image.delete()
            logger.debug(f"Successfully deleted image with ID: {image_id}")
            
            return JsonResponse({'success': True})
        except Exception as e:
            logger.error(f"Failed to delete image with ID {image_id}: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        logger.warning(f"Invalid request method: {request.method} for image ID: {image_id}")
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
