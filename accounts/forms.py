
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

# サインアップフォーム
class SignupForm(UserCreationForm):
    nickname = forms.CharField(max_length=150, required=True, help_text='必須です。ニックネームを入力してください。')
    age = forms.IntegerField(required=False, help_text='任意です。年齢を入力してください。')
    address = forms.CharField(max_length=255, required=False, help_text='任意です。住所を入力してください。')
    icon = forms.ImageField(required=False, help_text='任意です。アイコン画像をアップロードしてください。')

    class Meta:
        model = CustomUser  # CustomUserモデルを使用
        fields = ('username', 'nickname', 'email', 'password1', 'password2', 'age', 'address', 'icon')

    # formの段階でオブジェクトが保存される前に3MB以下の制約をバリデーションに追加
    def clean_icon(self):
        icon = self.cleaned_data.get('icon')
        if icon:
            if icon.size > 3 * 1024 * 1024:  # 3MB以下のサイズ制約
                raise ValidationError("アイコン画像のサイズは3MB以下にしてください。")
        return icon

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.nickname = self.cleaned_data['nickname']
        user.age = self.cleaned_data['age']
        user.address = self.cleaned_data['address']
        user.icon = self.cleaned_data.get('icon')
        if commit:
            user.save()
        return user

# カスタムログインフォーム
class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150, required=True, help_text='ユーザー名を入力してください。')
    password = forms.CharField(widget=forms.PasswordInput, required=True, help_text='パスワードを入力してください。')

    class Meta:
        model = CustomUser  # CustomUserモデルを使用
        fields = ('username', 'password')

# プロフィール編集フォーム
class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'age', 'address', 'icon')  # 編集可能なフィールド