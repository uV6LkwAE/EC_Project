
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import CreateView, TemplateView, UpdateView, DeleteView
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin  # ユーザーがログインしているか判定
from django.contrib.auth.views import LoginView, LogoutView  # Django標準のログインビューをインポート
from .forms import SignupForm, CustomLoginForm, ProfileEditForm  # カスタムログインフォームをインポート
from .models import CustomUser

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from transactions.models import Transaction
from products.models import Product


# サインアップビュー
class SignupView(CreateView):
    model = CustomUser  # CustomUserモデルを使用
    form_class = SignupForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('products:product_list')

    def form_valid(self, form):
        # フォームを保存して新規ユーザーを作成
        user = form.save()

        # ユーザーを認証してログイン
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)

        # 明示的にリダイレクト
        return redirect(self.success_url)

# カスタムログインビュー
class CustomLoginView(LoginView):
    form_class = CustomLoginForm  # CustomLoginFormを使用
    template_name = 'accounts/login.html'  # ログインテンプレートを指定

# ユーザーid or メールアドレス and パスワードでログインできるように

# ログアウトビュー

class CustomLogoutView(LoginRequiredMixin, LogoutView):
    template_name = "accounts/login.html"
    success_url = reverse_lazy('accounts:login')


# プロフィールビュー
class MypageView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/my_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 現在のユーザー情報をコンテキストに追加
        context['user'] = self.request.user
        return context

# プロフィール編集ビュー
class MypageEditView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = ProfileEditForm
    template_name = 'accounts/my_profile_edit.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        # 現在のログイン中のユーザーを返す
        return self.request.user

# 他のユーザーのプロフィールビュー
class ProfileView(TemplateView):
    template_name = 'accounts/user_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # ユーザー情報を取得
        user_id = kwargs.get('user_id')
        user = get_object_or_404(CustomUser, pk=user_id)
        context['user'] = user
        
        # 出品中の商品をフィルタリング
        products = Product.objects.filter(seller=user)
        
        # 検索クエリが存在する場合
        search_query = self.request.GET.get('q', '')
        if search_query:
            products = products.filter(title__icontains=search_query)  # 商品タイトルに検索ワードが含まれている商品を取得

        context['products'] = products
        
        return context

# アカウント削除ビュー
class AccountDeleteView(LoginRequiredMixin, DeleteView):
    model = CustomUser
    template_name = 'accounts/account_delete.html'
    success_url = reverse_lazy('accounts:signup')  # 削除後はサインアップページにリダイレクト

    def get_object(self, queryset=None):
        # 現在のログイン中のユーザーを返す
        return self.request.user

# 購入した商品ビュー
# 'received', '受け取り完了'した商品
@login_required
def purchased_items(request):
    status_filter = request.GET.get('status')  # クエリパラメータで状態を取得
    transactions = Transaction.objects.filter(buyer=request.user).select_related('product')
    
    if status_filter:
        transactions = Transaction.objects.filter(buyer=request.user).filter(status=status_filter)
    
    data = [
        {
            'id': t.id,
            'title': t.product.title,
            'price': float(t.product.price),
            'status': t.status,
        }
        for t in transactions
    ]
    return JsonResponse({'purchased_items': data})

# 出品した商品ビュー
@login_required
def sold_items(request):
    products = Product.objects.filter(seller=request.user)
    data = [
        {
            'id': p.id,
            'title': p.title,
            'price': float(p.price),
            'status': p.status,
        }
        for p in products
    ]
    return JsonResponse({'sold_items': data})

# 取引中の商品ビュー
@login_required
def trading_items(request):
    # 未発送または発送済みの取引をフィルタリング
    trading_transactions = Transaction.objects.filter(
        status__in=['order_confirmed', 'pending', 'shipped']
    ).select_related('product')
    
    # 必要なデータを抽出
    data = [
        {
            'id': transaction.id,
            'title': transaction.product.title,
            'price': transaction.product.price,
            'status': transaction.get_status_display(),
        }
        for transaction in trading_transactions
    ]
    
    # JsonResponseで返す
    return JsonResponse({'trading_items': data})
