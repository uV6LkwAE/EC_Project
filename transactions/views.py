
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
            status='order_confirmed'
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
        if new_status == 'order_confirmed' and request.user == transaction.buyer and transaction.status == 'pending':
        # 購入者が注文確定を行う場合
            transaction.status = 'order_confirmed'
            transaction.save()
        elif new_status == 'shipped' and request.user == transaction.seller and transaction.status == 'order_confirmed':
        # 販売者が発送を行う場合
            transaction.status = 'shipped'
            transaction.save()
        elif new_status == 'received' and request.user == transaction.buyer and transaction.status == 'shipped':
        # 購入者が受け取りを完了する場合
            transaction.status = 'received'
            transaction.save()


    return redirect('transactions:transaction_detail', transaction_id=transaction.id)

@login_required
def transaction_detail(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    return render(request, 'transactions/detail.html', {'transaction': transaction})
