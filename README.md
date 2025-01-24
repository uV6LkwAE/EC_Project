
# EC_Project

フリマサイトの一連の流れをDjangoを使用して作成しました。
諸事情により、実際に決済できる機能は実装されていません。

## 使用技術

- **フロントエンド**: HTML, CSS, JavaScript, Bootstrap, Splide  
- **バックエンド**: Python（Django）  
- **データベース**: PostgreSQL  
- **その他**: VSCode, WSL, Git

## 主な機能

- **ユーザー認証**
  - ユーザー登録、ログイン、ログアウト

- **商品管理**
  - 商品の出品、編集、削除
  - 商品の一覧表示、詳細表示

- **購入**
  - 商品の購入、取引のステータス更新
  - 購入後のレビュー

- **検索・フィルタ**
  - 商品名やカテゴリによる検索
  - 価格や条件によるフィルタリング

- **お気に入り機能**
  - 商品のお気に入り登録・解除

## セットアップ手順

1. **リポジトリをクローン**
   ```bash
   git clone https://github.com/username/EC_Project.git
   cd EC_Project
   ```

2. **仮想環境作成と依存パッケージのインストール**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements-dev.txt
   ```

3. **PostgreSQLでデータベースとロールを作成**
   ```sql
   CREATE DATABASE ec_project_db;
   CREATE USER ec_user WITH PASSWORD 'ec_user';
   GRANT ALL PRIVILEGES ON DATABASE ec_project_db TO ec_user;
   ```

4. **.envファイルを作成**  
   プロジェクトのルートディレクトリに`.env`ファイルを作成してください。

   任意のターミナルで以下のコマンドを実行して`SECRET_KEY`を生成します。
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

   `.env`ファイルの例:
   ```
   SECRET_KEY=生成されたセキュリティキー
   DEBUG=True
   DATABASE_URL=postgres://ec_user:your_password@localhost:5432/ec_project_db
   ALLOWED_HOSTS=[]
   ```

5. **設定ファイルの読み込み**
   ```bash
   export DJANGO_SETTINGS_MODULE=EC_Project.settings.development
   ```

6. **データベースのマイグレーション**
   ```bash
   python3 manage.py makemigrations
   python3 manage.py migrate
   ```

7. **スーパーユーザーを作成**
   ```bash
   python3 manage.py createsuperuser
   ```

8. **サーバーの起動**
   ```bash
   python3 manage.py runserver
   ```
