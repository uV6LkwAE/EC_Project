
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import Transaction, TransactionRating, Message
from .forms import TransactionRatingForm
from products.models import Product, ProductImage
from accounts.models import Follow
from django.urls import reverse 
# from django.contrib import messages

@login_required
def initiate_transaction(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    first_image = ProductImage.objects.filter(product=product).order_by('order').first()
    profile_user = product.seller


    # フォロー状態を判定
    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(
            follower=request.user, followed=profile_user
        ).exists()

    # テンプレート側で"不正な操作です"とすべて表示
    # 出品者自身による購入を禁止
    if request.user == product.seller:
        return render(request, 'transactions/confirm.html', {
            'product': product,
            'is_post_blocked': True,
        })

    # すでに取引レコードが存在する場合をブロック（statusに関係なくブロック）
    if Transaction.objects.filter(product=product).exists():
        return render(request, 'transactions/confirm.html', {
            'product': product,
            'is_post_blocked': True,
        })

    # 商品が売り切れの場合も同様に
    if product.status == 'sold_out':
        if request.method == "POST":
            return render(request, 'transactions/confirm.html', {'product': product, 'is_post_blocked': True})
        else:
            return render(request, 'transactions/confirm.html', {'product': product, 'is_post_blocked': True})

    if request.method == "POST":
        shipping_address = request.POST.get('shipping_address')

        # 新しい取引を作成
        transaction = Transaction.objects.create(
            buyer=request.user,
            seller=product.seller,
            product=product,
            shipping_address=shipping_address,
            status='order_confirmed'
        )

        # 商品のステータスを「売り切れ」に更新
        product.status = 'sold_out'
        product.save()

        return redirect('transactions:transaction_detail', transaction_id=transaction.id)

    return render(request, 'transactions/confirm.html', {
        'product': product,
        'first_image': first_image,
        'is_following': is_following,
    })

@login_required
def update_transaction_status(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)

    if request.method == "POST":
        new_status = request.POST.get('status')

        # ステータス更新ロジック
        if new_status == 'order_confirmed' and request.user == transaction.buyer and transaction.status == 'pending':
        # 購入者が注文確定を行う場合
            transaction.status = 'order_confirmed'
            transaction.save()
            # messages.add_message(request, messages.INFO, 'ステータスが注文確定に変更されました。ページをリロードしてください。')
        elif new_status == 'shipped' and request.user == transaction.seller and transaction.status == 'order_confirmed':
        # 販売者が発送を行う場合
            transaction.status = 'shipped'
            transaction.save()
            # messages.add_message(request, messages.INFO, 'ステータスが発送済みに変更されました。ページをリロードしてください。')
        elif new_status == 'received' and request.user == transaction.buyer and transaction.status == 'shipped':
        # 購入者が受け取りを完了する場合
            transaction.status = 'received'
            transaction.save()
            # messages.add_message(request, messages.INFO, 'ステータスが受け取り完了に変更されました。ページをリロードしてください。')

        # 更新が成功した場合、メッセージを追加
        # messages.success(request, 'ステータスが更新されました。ページをリロードします。')
        
        # 出品者と購入者両方が評価を行った後に、取引完了に変更
        seller_rating = TransactionRating.objects.filter(transaction=transaction, rated_user=transaction.seller).exists()
        buyer_rating = TransactionRating.objects.filter(transaction=transaction, rated_user=transaction.buyer).exists()

        if seller_rating and buyer_rating:
            transaction.status = 'completed'
            transaction.save()

    return redirect('transactions:transaction_detail', transaction_id=transaction.id)

@login_required
def transaction_detail(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    messages = Message.objects.filter(transaction=transaction).order_by("timestamp")

    # 出品者または購入者の評価がまだ投稿されていないか確認
    seller_rating_exists = TransactionRating.objects.filter(transaction=transaction, rated_user=transaction.seller).exists()
    buyer_rating_exists = TransactionRating.objects.filter(transaction=transaction, rated_user=transaction.buyer).exists()

    # ログイン中のユーザーが評価を投稿したか
    user_is_buyer = request.user == transaction.buyer
    user_is_seller = request.user == transaction.seller
    user_rating_exists = TransactionRating.objects.filter(transaction=transaction, rater=request.user).exists()

    # デバッグ用メッセージ
    debug_message = f"ログインユーザー: {request.user.username} は、"
    if user_is_buyer:
        debug_message += "購入者です。"
    elif user_is_seller:
        debug_message += "出品者です。"
    else:
        debug_message += "購入者でも出品者でもありません。"

    # 購入者または出品者でない場合、GETリクエストをブロックして商品詳細ページへリダイレクト
    if request.user != transaction.buyer and request.user != transaction.seller:
        return render(request, 'transactions/detail.html', {
            'is_get_blocked': True,
            'transaction': transaction,
            'product_id': transaction.product.id,
            'product': transaction.product,
        })

    # ステータスに応じてパーセンテージを設定
    if transaction.status == 'order_confirmed':
        progress_percentage = 0  # 注文確定は0%
    elif transaction.status == 'pending':
        progress_percentage = 20  # 未発送は20%
    elif transaction.status == 'shipped':
        progress_percentage = 40  # 発送済みは40%
    elif transaction.status == 'received':
        progress_percentage = 60  # 受け取り完了は60%
    elif transaction.status == 'completed':  # 取引完了を100%に変更
        progress_percentage = 100  # 完了は100%
    else:
        progress_percentage = 0  # デフォルト値


    # 評価フォーム処理
    if request.method == 'POST':
        form = TransactionRatingForm(request.POST)
        if form.is_valid():
            # 評価の保存
            form.instance.transaction = transaction
            form.instance.rater = request.user
            form.instance.rated_user = transaction.seller if request.user == transaction.buyer else transaction.buyer
            form.save()

            # 評価後に取引完了に変更するロジック
            seller_rating = TransactionRating.objects.filter(transaction=transaction, rated_user=transaction.seller).exists()
            buyer_rating = TransactionRating.objects.filter(transaction=transaction, rated_user=transaction.buyer).exists()

            if seller_rating and buyer_rating:
                transaction.status = 'completed'
                transaction.save()

            return redirect('transactions:transaction_detail', transaction_id=transaction.id)
    else:
        form = TransactionRatingForm()
    
    # 関連するproductを取得
    product = transaction.product
    first_image = ProductImage.objects.filter(product=product).order_by('order').first()
        
    return render(request, 'transactions/detail.html', {
        'transaction': transaction,
        'progress_percentage': progress_percentage,
        'form': form,
        'user_rating_exists': user_rating_exists,
        'seller_rating_exists': seller_rating_exists,
        'buyer_rating_exists': buyer_rating_exists,
        'user_is_buyer': user_is_buyer,
        'user_is_seller': user_is_seller,
        # 'alert_message': alert_message, 
        'debug_message': debug_message,
        'first_image': first_image,
        'messages': messages,
    })

@login_required
def submit_transaction_rating(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)

    # 出品者または購入者の評価がまだ投稿されていないか確認
    seller_rating_exists = TransactionRating.objects.filter(transaction=transaction, rated_user=transaction.seller).exists()
    buyer_rating_exists = TransactionRating.objects.filter(transaction=transaction, rated_user=transaction.buyer).exists()

    # ログイン中のユーザーが評価を投稿したか
    user_is_buyer = request.user == transaction.buyer
    user_is_seller = request.user == transaction.seller
    user_rating_exists = TransactionRating.objects.filter(transaction=transaction, rater=request.user).exists()

    # 取引が受け取り完了かつ、評価がまだ投稿されていない場合にのみ処理を行う
    if transaction.status == 'received':
        # すでに評価が投稿されているか確認
        existing_rating = TransactionRating.objects.filter(transaction=transaction)
        
        # 出品者から購入者への評価が存在するか
        seller_to_buyer_rating = existing_rating.filter(rated_user=transaction.buyer, rater=transaction.seller).exists()
        
        # 購入者から出品者への評価が存在するか
        buyer_to_seller_rating = existing_rating.filter(rated_user=transaction.seller, rater=transaction.buyer).exists()

        # 両方の評価が存在しない場合のみ投稿を許可
        if seller_to_buyer_rating and buyer_to_seller_rating:
            error_message = "評価はすでに両者から投稿されています。"
            return render(request, 'transactions/detail.html', {
                'transaction': transaction,
                'error_message': error_message,
                'user_rating_exists': user_rating_exists,
                'seller_rating_exists': seller_rating_exists,
                'buyer_rating_exists': buyer_rating_exists,
                'user_is_buyer': user_is_buyer,
                'user_is_seller': user_is_seller,
            })

        # 評価を送信したユーザーが出品者か購入者であることを確認
        if request.user != transaction.buyer and request.user != transaction.seller:
            return redirect('products:product_list')  # 出品者でも購入者でもない場合はリダイレクト

        if request.method == 'POST':
            form = TransactionRatingForm(request.POST)
            if form.is_valid():
                rating = form.save(commit=False)
                rating.transaction = transaction
                rating.rater = request.user
                # 出品者が購入者を評価する場合と購入者が出品者を評価する場合
                if request.user == transaction.buyer:
                    rating.rated_user = transaction.seller
                else:
                    rating.rated_user = transaction.buyer
                rating.save()

                # 両者が評価した場合、取引を「取引完了」に更新
                seller_rating = TransactionRating.objects.filter(transaction=transaction, rated_user=transaction.seller).exists()
                buyer_rating = TransactionRating.objects.filter(transaction=transaction, rated_user=transaction.buyer).exists()

                if seller_rating and buyer_rating:
                    transaction.status = 'completed'
                    transaction.save()

                # 成功メッセージを設定
                return render(request, 'transactions/detail.html', {
                    'transaction': transaction,
                    'success_message': "評価が正常に送信されました。",
                    'user_rating_exists': user_rating_exists,
                    'seller_rating_exists': seller_rating_exists,
                    'buyer_rating_exists': buyer_rating_exists,
                    'user_is_buyer': user_is_buyer,
                    'user_is_seller': user_is_seller,
                })
            
            else:
                # フォームが無効の場合、エラーメッセージを渡す
                error_message = "評価の投稿に失敗しました。再度試してください。"
                return render(request, 'transactions/detail.html', {
                    'transaction': transaction,
                    'error_message': error_message,
                    'user_rating_exists': user_rating_exists,
                    'seller_rating_exists': seller_rating_exists,
                    'buyer_rating_exists': buyer_rating_exists,
                    'user_is_buyer': user_is_buyer,
                    'user_is_seller': user_is_seller,
                })

        else:
            form = TransactionRatingForm()
        
        return render(request, 'transactions/rating_form.html', {'form': form, 'transaction': transaction})

    return redirect('transactions:transaction_detail', transaction_id=transaction.id)

