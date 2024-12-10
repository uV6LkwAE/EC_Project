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