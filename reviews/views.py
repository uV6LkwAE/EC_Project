
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import Review
from transactions.models import Transaction

@login_required
def add_review(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)

    if transaction.status != "received":
        # 受け取り完了でなければ評価を許可しない
        return redirect('transactions:transaction_detail', transaction_id=transaction.id)

    if request.method == "POST":
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        # レビューの作成
        Review.objects.create(
            transaction=transaction,
            reviewer=request.user,
            reviewee=transaction.seller if transaction.buyer == request.user else transaction.buyer,
            rating=rating,
            comment=comment
        )

        return redirect('transactions:transaction_detail', transaction_id=transaction.id)

    return render(request, 'reviews/add_review.html', {'transaction': transaction})
