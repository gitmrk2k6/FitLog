# FitLog バックエンド

FastAPI + SQLAlchemy + PostgreSQL。F-01〜F-10 の全機能を実装済み。

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
pytest        # 全テスト実行（pytest_test DB は自動作成）
```

## 実装済みエンドポイント

| メソッド | パス | 機能 |
| --- | --- | --- |
| POST | `/auth/register` | ユーザー登録（F-01） |
| POST | `/auth/login` | ログイン・JWT発行（F-01） |
| POST | `/auth/logout` | ログアウト（クライアント側トークン破棄）（F-01） |
| GET | `/auth/me` | 認証ユーザー情報取得（F-01） |
| GET | `/exercises` | 種目一覧取得 |
| POST | `/exercises` | カスタム種目作成 |
| POST | `/workouts` | ワークアウット記録作成（F-02, F-09） |
| GET | `/workouts` | 自分の記録一覧（F-03） |
| GET | `/workouts/{id}` | 記録詳細（F-03） |
| PATCH | `/workouts/{id}` | 記録更新（F-02） |
| DELETE | `/workouts/{id}` | 記録削除（F-02） |
| PUT | `/workouts/{id}/photo` | 写真アップロード・S3保存（F-10） |
| DELETE | `/workouts/{id}/photo` | 写真削除（F-10） |
| POST | `/workouts/{id}/cheers` | ナイストレ付与（F-04） |
| DELETE | `/workouts/{id}/cheers` | ナイストレ解除（F-04） |
| GET | `/workouts/{id}/advices` | アドバイス一覧（F-05） |
| POST | `/workouts/{id}/advices` | アドバイス投稿（F-05） |
| DELETE | `/advices/{id}` | アドバイス削除（F-05） |
| GET | `/users/search` | ユーザー検索（F-06） |
| GET | `/users/{id}` | プロフィール取得（F-06） |
| GET | `/users/{id}/following` | フォロー中一覧（F-06） |
| GET | `/users/{id}/followers` | フォロワー一覧（F-06） |
| POST | `/users/{id}/follow` | フォロー（F-06） |
| DELETE | `/users/{id}/follow` | アンフォロー（F-06） |
| GET | `/feed` | フォロー中フィード（F-06） |
| GET | `/goals` | 目標一覧（F-07） |
| PUT | `/goals` | 目標設定・更新（upsert）（F-07） |
| DELETE | `/goals/{period_type}` | 目標削除（F-07） |
| GET | `/goals/{period_type}/trend` | 達成率推移（F-07） |
| GET | `/dashboard/personal-records` | 種目別自己ベスト（F-09） |
| GET | `/dashboard/achievements` | 現在期間の達成率（F-07） |
| GET | `/dashboard/streak` | 連続記録日数（F-08） |
| GET | `/dashboard/heatmap` | 日別ボリューム（F-08） |
| GET | `/health` | ヘルスチェック |
