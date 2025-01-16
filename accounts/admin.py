
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import Follow


CustomUser = get_user_model()

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # ユーザー編集画面で表示するフィールドを設定
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('age', 'address', 'icon')}),
    )

    # ユーザーリスト画面で表示するフィールドを設定
    list_display = ('username', 'email', 'age', 'icon')

admin.site.register(Follow)