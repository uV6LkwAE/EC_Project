
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import Transaction
from products.models import Product

@login_required
def initiate_transaction(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        shipping_address = request.POST.get('shipping_address')

        # 新しい取引を作成
        transaction = Transaction.objects.create(
            buyer=request.user,
            seller=product.seller,
            product=product,
            shipping_address=shipping_address,
            status='pending'
        )

        # 商品のステータスを「売り切れ」に更新
        product.status = 'sold_out'
        product.save()

        return redirect('transactions:transaction_detail', transaction_id=transaction.id)

    return render(request, 'transactions/confirm.html', {'product': product})

@login_required
def update_transaction_status(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)

    if request.method == "POST":
        new_status = request.POST.get('status')

        # ステータス更新ロジック
        if new_status == 'shipped' and request.user == transaction.seller and transaction.status == 'pending':
            transaction.status = 'shipped'
            transaction.save()
        elif new_status == 'received' and request.user == transaction.buyer and transaction.status == 'shipped':
            transaction.status = 'received'
            transaction.save()

    return redirect('transactions:transaction_detail', transaction_id=transaction.id)

@login_required
def transaction_detail(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    
    # ステータスに応じた進行具合を計算
    if transaction.status == 'order_confirmed':
        progress_percentage = 0  # 注文確定は0%
    elif transaction.status == 'pending':
        progress_percentage = 25  # 未発送は25%
    elif transaction.status == 'shipped':
        progress_percentage = 75  # 発送済みは75%
    elif transaction.status == 'received':
        progress_percentage = 100  # 受け取り完了は100%
    else:
        progress_percentage = 0  # デフォルト値

    return render(request, 'transactions/detail.html', {
        'transaction': transaction,
        'progress_percentage': progress_percentage,
    })
