
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import CreateView, TemplateView, UpdateView, DeleteView
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin  # ユーザーがログインしているか判定
from django.contrib.auth.views import LoginView, LogoutView  # Django標準のログインビューをインポート
from .forms import SignupForm, CustomLoginForm, ProfileEditForm  # カスタムログインフォームをインポート
from .models import CustomUser

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
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 現在のユーザー情報をコンテキストに追加
        context['user'] = self.request.user
        return context

# プロフィール編集ビュー
class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = ProfileEditForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        # 現在のログイン中のユーザーを返す
        return self.request.user


# アカウント削除ビュー
class AccountDeleteView(LoginRequiredMixin, DeleteView):
    model = CustomUser
    template_name = 'accounts/account_delete.html'
    success_url = reverse_lazy('accounts:signup')  # 削除後はサインアップページにリダイレクト

    def get_object(self, queryset=None):
        # 現在のログイン中のユーザーを返す
        return self.request.user