
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
from django.db.models import Q


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

# 取引中の商品
# ・ログイン中のユーザーであり、ステータスが('received', '受け取り完了')以外の場合
# ・取引の新しい順で並び替え

# 購入した商品
# ・ログイン中のユーザーであり、ステータスが('received', '受け取り完了')である
# ・取引の新しい順で並び替え

# 出品した商品
# ・ログイン中のユーザーが出品した商品である
# ・・取引の新しい順で並び替え


# 購入した商品ビュー
@login_required
def purchased_items(request):
    # クエリパラメータで状態を取得
    status_filter = request.GET.get('status')  

    # 購入した商品に対してフィルタリングを行う
    transactions = Transaction.objects.filter(buyer=request.user, status__in=['received', 'completed']) \
        .select_related('product') \
        .order_by('-created_at')  # 取引の新しい順で並べ替え

    if status_filter:
        transactions = transactions.filter(status=status_filter)  # 状態でさらに絞り込み

    # 購入した商品のデータを整形
    data = [
        {
            'id': t.id,
            'title': t.product.title,
            'price': float(t.product.price),
            'status': t.status,
            'buyer': t.buyer_id,
            'seller': t.seller_id,
            'created': t.created_at,
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
    # ログイン中のユーザーが購入者または販売者として取引に関わるものを取得
    transactions = Transaction.objects.filter(
        (Q(buyer=request.user) | Q(seller=request.user))  # 購入者または販売者が現在のユーザーである
    ).exclude(status__in=['received', '受け取り完了'])  # ステータスが 'received' または '受け取り完了' 以外

    # 取引を新しい順に並べ替え
    transactions = transactions.order_by('-id')  # idの降順で新しい取引を先に表示

    data = [
        {
            'id': t.id,
            'title': t.product.title,
            'price': float(t.product.price),
            'status': t.status,
            'buyer': t.buyer_id,
            'seller': t.seller_id,
            'created': t.created_at,
        }
        for t in transactions
    ]
    return JsonResponse({'trading_items': data})