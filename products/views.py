
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.forms.utils import ErrorList
from .models import Product, ProductImage, Favorite, Comment
from .forms import ProductForm
from django import forms
from django.utils import timezone
from datetime import timedelta
import json
from django.http import JsonResponse
from django.http import HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
import logging


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

    def dispatch(self, request, *args, **kwargs):
        # 商品が購入済みか確認
        product = self.get_object()
        if product.status == 'sold_out':
            return HttpResponseForbidden("この商品は購入されているため編集できません。")
        return super().dispatch(request, *args, **kwargs)

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


# class ProductListView(ListView):
#     model = Product
#     template_name = 'products/product_list.html'
#     context_object_name = 'products'
#     paginate_by = 10  # ページネーション


# class ProductDetailView(DetailView):
#     model = Product
#     template_name = 'products/product_detail.html'
#     context_object_name = 'product'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         if self.request.user.is_authenticated:
#             context['is_favorited'] = Favorite.objects.filter(
#                 user=self.request.user, product=self.object
#             ).exists()
#         else:
#             context['is_favorited'] = False
#         return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()  # 現在表示されている商品を取得
        self.object = product
        print(f"Product in context: {product}")  # デバッグログ

        # 商品が売り切れの場合はコメントフォームを表示しない
        if product.status == "sold_out":
            context['comments_disabled'] = True
        else:
            context['comments_disabled'] = False

        # 親コメントを取得
        comments = product.comments.filter(reply_to=None)
        print("Comments in context: ", comments)

        # コメントフォームを取得
        if self.request.user.is_authenticated:
            form = CommentForm()
            context['form'] = form

        # お気に入り判定
        if self.request.user.is_authenticated:
            is_favorited = product.favorited_by.filter(user=self.request.user).exists()  # 修正: idではなくuserで検索
        else:
            is_favorited = False

        # 出品日時の計算
        created_at = product.created_at
        now = timezone.now()
        time_diff = now - created_at

        # 1分未満の場合は「たった今出品されました」
        if time_diff < timedelta(minutes=1):
            time_display = "たった今出品されました"

        # 1分以上60分未満の場合は「~分前に出品されました」
        elif time_diff < timedelta(hours=1):
            minutes_ago = int(time_diff.total_seconds() // 60)
            time_display = f"{minutes_ago}分前に出品されました"

        # 1時間以上24時間未満の場合は「~時間前に出品されました」
        elif time_diff < timedelta(days=1):
            hours_ago = int(time_diff.total_seconds() // 3600)
            time_display = f"{hours_ago}時間前に出品されました"

        # それ以上の場合は「~日前に出品されました」
        else:
            days_ago = time_diff.days
            time_display = f"{days_ago}日前に出品されました"

        context['comments'] = comments
        context['is_favorited'] = is_favorited 
        context['time_display'] = time_display
        context['comments_disabled'] = context.get('comments_disabled', False)

        return context


    def post(self, request, *args, **kwargs):
        # 商品詳細ページに対するPOSTリクエスト（コメント投稿）
        product = self.get_object()
        self.object = product
        print(f"Product object: {product}")  # デバッグログ
        form = CommentForm(request.POST)

        if form.is_valid():
            # コメントを一時的に保存
            comment = form.save(commit=False)
            # コメントがどの商品のものか指定
            comment.product = product
            # 現在のユーザーをコメントの作成者として保存
            comment.user = request.user  

            # リプライがあれば、リプライ先のコメントを指定
            # リプライ先のコメントIDを数値に変換して設定
            reply_to = form.cleaned_data.get('reply_to')

            print(f"リプライ先のコメントID: {reply_to}")  # ログを追加

            if reply_to:
                if isinstance(reply_to, Comment):
                    # reply_toがすでにCommentオブジェクトの場合、そのまま使用
                    comment.reply_to = reply_to
                else:
                    try:
                        # reply_toをIDで取得
                        comment.reply_to = Comment.objects.get(id=int(reply_to))  # ここでIDを使ってCommentオブジェクトを取得
                    except ValueError:
                        print(f"Invalid reply_to value: {reply_to}")
                    except Comment.DoesNotExist:
                        print(f"Comment with id {reply_to} does not exist.")
            
            # コメントを保存
            comment.save()

            # コメント投稿後、同じ商品ページにリダイレクト
            return redirect('products:product_detail', pk=product.pk)

        # フォームが無効な場合、再度商品詳細ページを表示
        print(f"Form errors: {form.errors}") 
        return self.render_to_response(self.get_context_data(form=form))


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/product_delete.html'
    success_url = reverse_lazy('products:product_list')

    def dispatch(self, request, *args, **kwargs):
        # 商品が購入済みか確認
        product = self.get_object()
        if product.status == 'sold_out':
            return HttpResponseForbidden("この商品は購入されているため削除できません。")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # ログイン中のユーザーが出品者の商品だけを取得
        return super().get_queryset().filter(seller=self.request.user)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'reply_to']  # reply_toフィールドを追加

    # reply_toフィールドをフォームに追加（リプライ元のコメント）
    reply_to = forms.ModelChoiceField(
        queryset=Comment.objects.all(),
        required=False,  # リプライでない場合は不要
        widget=forms.HiddenInput(),  # フォーム上では表示しない
    )




@login_required
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # 出品者自身や売り切れた商品をお気に入りに追加できないように制御
    if product.seller == request.user:
        return HttpResponseForbidden("自身の商品はお気に入りに追加できません。")
    if product.status == 'sold_out':
        return HttpResponseForbidden("売り切れた商品はお気に入りに追加できません。")

    # お気に入り追加・解除
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
