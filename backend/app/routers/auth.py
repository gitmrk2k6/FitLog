from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserOut,
)
from app.services.auth_service import (
    AuthService,
    DuplicateEmailError,
    DuplicateUsernameError,
    InvalidCredentialsError,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="新規ユーザー登録",
    description="ユーザー名・メールアドレス・パスワードで新規アカウントを作成します。パスワードは8文字以上で英字と数字を含む必要があります。",
    responses={
        409: {"description": "メールアドレスまたはユーザー名が既に使用済み"},
        422: {"description": "バリデーションエラー（パスワード強度不足など）"},
    },
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> User:
    service = AuthService(db)
    try:
        return service.register(
            username=payload.username,
            email=payload.email,
            password=payload.password,
        )
    except (DuplicateEmailError, DuplicateUsernameError) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="ログイン（JWTトークン取得）",
    description="メールアドレスとパスワードで認証し、JWT アクセストークンを返します。以降のリクエストは `Authorization: Bearer <token>` ヘッダを付与してください。",
    responses={
        401: {"description": "メールアドレスまたはパスワードが無効"},
    },
)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    service = AuthService(db)
    try:
        user = service.authenticate(
            email=payload.email, password=payload.password
        )
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)
        ) from exc
    return TokenResponse(access_token=service.issue_token(user))


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="ログアウト",
    description="JWT はステートレスのため、クライアント側でトークンを破棄します。サーバー側での処理はありません。",
)
def logout() -> dict[str, str]:
    return {"status": "success"}


@router.get(
    "/me",
    response_model=UserOut,
    summary="ログイン中ユーザーの情報取得",
    description="Bearer トークンに紐づくログイン中ユーザーの情報を返します。",
    responses={
        401: {"description": "未認証（トークン不正または期限切れ）"},
    },
)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
