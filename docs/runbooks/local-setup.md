# ローカル環境構築手順書（Runbook）

このドキュメントは、`project-atlas-api` のローカル開発環境を構築するための詳細な手順書です。  
README の「セットアップ手順」の詳細版として利用します。

---

## 前提条件

- OS: macOS / Linux（Windows の場合は WSL2 推奨）
- Python: 3.12 以上
- PostgreSQL: 15 以上
- Git がインストール済みであること

---

## 1. リポジトリのクローン

```bash
git clone https://github.com/example/project-atlas-api.git
cd project-atlas-api
```

---

## 2. Python 仮想環境の作成・有効化

### 2-1. 仮想環境の作成

```bash
python -m venv venv
```

### 2-2. 仮想環境の有効化

macOS / Linux:

```bash
source venv/bin/activate
```

---

## 3. 依存パッケージのインストール

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install --upgrade python-multipart starlette
```

---

## 4. データベースの作成

### 4-1. PostgreSQL の起動確認

PostgreSQL が起動していない場合は起動してください（Homebrew 例）:

```bash
brew services start postgresql@15
```

### 4-2. データベース `atlas` の作成

```bash
createdb atlas
```

既に存在する場合はエラーになるが、その場合はそのまま次のステップに進んで問題ありません。

---

## 5. 環境変数の設定

アプリケーションが接続する DB の接続情報を環境変数 `DATABASE_URL` に設定します。

macOS / Linux (bash/zsh):

```bash
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/atlas
```

※ ユーザー名やパスワードを変更している場合は、手元の設定に合わせて書き換えてください。

---

## 6. マイグレーションの実行

データベースにテーブルを作成するため、Alembic マイグレーションを実行します。

```bash
alembic upgrade head
```

---

## 7. アプリケーションの起動

FastAPI アプリケーションをローカルで起動します。

```bash
uvicorn main:app --reload
```

デフォルトは `http://127.0.0.1:8000` で起動。

---

## 8. 動作確認（Swagger UI）

ブラウザで以下の URL にアクセスし、API ドキュメントが表示されることを確認します。

- [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 9. テストの実行

最後にテストを実行し、ローカル環境が正しく構成されていることを確認します。

```bash
pytest tests/ -v
```

---

## 10. よくあるエラーと対処

### 10-1. `createdb: command not found`

PostgreSQL のコマンドラインツールが PATH に通っていない可能性があります。

- Homebrew インストールの場合の例:

```bash
export PATH="/usr/local/opt/postgresql@15/bin:$PATH"
```

### 10-2. DB 接続エラー（`DATABASE_URL` 関連）

- PostgreSQL が起動しているか確認する
- `DATABASE_URL` のユーザー名 / パスワード / ポート / DB 名が実際の設定と一致しているか確認する
- `atlas` データベースが作成済みか `psql -l` などで確認する

---

## 11. まとめ

- README にはこの Runbook へのリンクを記載し、「詳細手順は Runbook を参照」と案内します。
- 新メンバーは、まず README で全体像を把握し、詰まった場合や細かい確認が必要な場合にこの Runbook を参照します。

