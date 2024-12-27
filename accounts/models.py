
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

# カスタムユーザーモデルの定義
class CustomUser(AbstractUser):
    age = models.IntegerField(blank=True, null=True, help_text='任意です。年齢を入力してください。')
    address = models.CharField(max_length=255, blank=True, null=True, help_text='任意です。住所を入力してください。')
    icon = models.ImageField(upload_to='user_icons/', blank=True, null=True, help_text='任意です。アイコン画像をアップロードしてください。')

    # CreateSuperUserする際に必要なフィールドを指定
    REQUIRED_FIELDS = ['email', 'age']

    # ImageFieldに対してファイルサイズの制約を追加
    # 30MB以下のファイルサイズでiconが保存されることを確認
    def clean(self):
        super().clean()
        if self.icon:
            if self.icon.size > 3 * 1024 * 1024:  # 3MB以下のサイズ制約
                raise ValidationError("アイコン画像のサイズは3MB以下にしてください。")

    def __str__(self):
        return self.username