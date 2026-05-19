# FitLog バックエンド

FastAPI + SQLAlchemy + PostgreSQL。本 Increment では基盤 + 全9テーブルのスキーマ + F-01 認証を実装。

## セットアップ

```bash
# 1. PostgreSQL（リポジトリルートで）
cd ..
docker compose up -d

# 2. Python 環境
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env        # 必要なら SECRET_KEY を変更

# 3. マイグレーション（全9テーブル作成）
alembic upgrade head

# 4. 起動（ポート8000）
uvicorn app.main:app --reload --port 8000
# Swagger: http://localhost:8000/docs
```

## テスト

```bash
pytest        # F-01 認証テスト（pytest_test DB は自動作成）
```

## 実装済みエンドポイント（F-01）

| メソッド | パス | 説明 |
| --- | --- | --- |
| POST | `/auth/register` | ユーザー登録（201） |
| POST | `/auth/login` | ログイン、JWT 発行 |
| POST | `/auth/logout` | クライアント側でトークン破棄 |
| GET | `/auth/me` | 認証ユーザー情報（要 Bearer） |
| GET | `/health` | ヘルスチェック |

F-02〜F-10 は機能ごとに別 issue/PR で段階的に追加する。
