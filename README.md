
## ブランチ命名規則

### feature/app_name
各アプリごとの開発

### feature/settings_update
プロジェクトのsettings.pyや他の設定に関する更新

### feature/template_update
テンプレートの修正

### feature/documentation_update
README.md,ドキュメントなどの更新

### feature/config_update
config関連の更新
.env .gitgnoreの修正

### feature/deployment_setup
デプロイ関連の設定ファイルの修正

### feature/requirements_update
requirements.txtや依存パッケージに関する更新

## add,commit,push,mergeの流れ
1, git add
2, git commit -m
3, git checkout -b feature/documentation_update
4, git push origin feature/documentation_update
5, git checkout develop
6, git merge feature/documentation_update