# Project Atlas API

チーム・ユーザー管理API。

## 前提条件

- Python 3.12+
- PostgreSQL 15+

## セットアップ

### 1. リポジトリのクローン

```
git clone https://github.com/s-hayashi123/project-atlas-api.git
cd project-atlas-api
```

### 2. 仮想環境の作成・有効化

```
python -m venv venv
source venv/bin/activate # macOS/Linux
```

### 3. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 4. データベースの作成

```
createdb atlas
```

### 5. 環境変数の設定

```
export DATABASE_URL=postgersql://postgres:postfres@localhost:5432/atlas
```

### 6. マイグレーションの実行

```
alembic upgrade head
```

## サーバー起動

```bash
uvicorn main:app --reload
```

APIドキュメント: [http://localhost:8000/docs](http://localhost:8000/docs)

## テスト

```
pytest tests/ -v
```

詳細な手順は [Runbook](docs/runbooks/local-setup.md)を参照してください