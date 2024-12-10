from .base import *
import environ

# 環境変数の読み込み
env = environ.Env()
env_file = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_file):  # 開発環境用に.envを読み込む
    env.read_env(env_file)
else:
    print("NO")

DEBUG = True
ALLOWED_HOSTS = ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

SECRET_KEY = env('SECRET_KEY')

# データベース設定（環境変数で管理）
DATABASES = {
    'default': env.db(),  # 環境変数 DATABASE_URL を使用
}
