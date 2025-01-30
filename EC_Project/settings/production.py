from .base import *
import environ

# 環境変数の読み込み
env = environ.Env()
env.read_env(os.path.join(BASE_DIR, '.env'))

DEBUG = False
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

SECRET_KEY = env('SECRET_KEY')
# デバッグ用
if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set in the environment")


DATABASES = {
    'default': env.db(),
}
# デバッグ用
if not DATABASES['default']:
    raise ValueError("DATABASE_URL is not set in the environment")


# 本番環境の Redis 設定（EC2 上の Redis を使用）
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("YOUR_EC2_IP", 6379)],  # EC2のグローバルIP or プライベートIP
        },
    },
}