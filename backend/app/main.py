from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging
from app.middleware.request_logging import RequestLoggingMiddleware
from app.routers import (
    advices,
    auth,
    cheers,
    dashboard,
    exercises,
    feed,
    goals,
    photos,
    users,
    workouts,
)

setup_logging()
settings = get_settings()
_logger = get_logger("fitlog.app")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    _logger.info("fitlog api started", extra={"env": settings.env, "log_level": settings.log_level})
    yield


app = FastAPI(
    lifespan=lifespan,
    title="FitLog API",
    version="0.1.0",
    description="""
FitLog は筋トレ・運動記録サービスの REST API です。

## 認証
保護エンドポイントは Bearer トークン（JWT）を要求します。
`/auth/login` で取得したトークンを `Authorization: Bearer <token>` ヘッダに付与してください。

## 共通エラーレスポンス
| ステータス | 意味 |
|---|---|
| 401 | 未認証（トークン不正・期限切れ） |
| 403 | 権限なし（他ユーザーのリソースへのアクセス等） |
| 404 | リソースが見つからない |
| 409 | 重複登録（メール・ユーザー名等） |
| 422 | バリデーションエラー |
""",
    openapi_tags=[
        {"name": "auth",      "description": "ユーザー登録・ログイン・ログアウト・プロフィール取得（F-01）"},
        {"name": "exercises", "description": "種目マスタの一覧取得・カスタム種目作成"},
        {"name": "workouts",  "description": "ワークアウト記録の作成・一覧・詳細・編集・削除（F-02/F-03）"},
        {"name": "photos",    "description": "ワークアウト写真のアップロード・削除（F-10）"},
        {"name": "cheers",    "description": "ナイストレ（いいね）の付与・解除（F-04）"},
        {"name": "advices",   "description": "アドバイスコメントの投稿・一覧・削除（F-05）"},
        {"name": "users",     "description": "ユーザー検索・プロフィール・フォロー操作（F-06）"},
        {"name": "feed",      "description": "フォロー中ユーザーのワークアウト一覧（F-06）"},
        {"name": "goals",     "description": "目標の設定・一覧・削除・達成率推移（F-07）"},
        {"name": "dashboard", "description": "自己ベスト・達成率・ストリーク・ヒートマップ（F-07/F-08/F-09）"},
        {"name": "health",    "description": "サーバー稼働確認"},
    ],
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,      prefix="/api")
app.include_router(exercises.router,  prefix="/api")
app.include_router(workouts.router,   prefix="/api")
app.include_router(photos.router,     prefix="/api")
app.include_router(cheers.router,     prefix="/api")
app.include_router(advices.router,    prefix="/api")
app.include_router(users.router,      prefix="/api")
app.include_router(feed.router,       prefix="/api")
app.include_router(goals.router,      prefix="/api")
app.include_router(dashboard.router,  prefix="/api")


@app.get("/health", tags=["health"], include_in_schema=False)
def health_internal() -> dict[str, str]:
    """ECS / ALB ヘルスチェック専用（CloudFront 非公開）"""
    return {"status": "ok"}


@app.get("/api/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
