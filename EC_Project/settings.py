"""
Django settings for EC_Project project.

Generated by 'django-admin startproject' using Django 5.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-$u6uq2w+fuud3a0j2(b*5--e4jvn)w13_x$$m%m!nt*%y*-nta'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # allauth関連
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'accounts',
    'products',
    'search',
]

# サイトIDの設定（必須）
SITE_ID = 1

# 認証バックエンドの設定
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Djangoの標準認証
    'allauth.account.auth_backends.AuthenticationBackend',  # allauthの認証
]

# カスタムユーザーモデルの設定
AUTH_USER_MODEL = 'accounts.CustomUser'

# メールアドレスの確認を必須にするかどうか
ACCOUNT_EMAIL_VERIFICATION = "mandatory"  # メール確認を必須に
ACCOUNT_EMAIL_REQUIRED = True  # メールアドレスを必須項目に
LOGIN_REDIRECT_URL = 'accounts:profile'  # ログイン後にリダイレクトするURL
LOGOUT_REDIRECT_URL = 'accounts:login'  # ログアウト後のリダイレクト先


# メディアファイルの設定
MEDIA_URL = '/media/'  # URLで画像にアクセスする際のパス
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # 画像を保存するディレクトリ


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # allauth関連のミドルウェアを追加
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'EC_Project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'EC_Project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ec_project_db',           # 使用するデータベース名
        'USER': 'ec_user',      # PostgreSQLのユーザー名
        'PASSWORD': 'ec_user',       # PostgreSQLのパスワード
        'HOST': 'localhost',               # ホスト名（ローカルで実行する場合は 'localhost'）
        'PORT': '5432',                    # PostgreSQLのデフォルトポート
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",  # 'static'ディレクトリを指定
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
