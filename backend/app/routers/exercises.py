from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.exercise import ExerciseCreate, ExerciseOut
from app.services.exercise_service import DuplicateExerciseError, ExerciseService

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get(
    "",
    response_model=list[ExerciseOut],
    summary="種目一覧取得（共通 + 自作）",
    description="共通種目と、ログインユーザーが作成したカスタム種目の一覧を返します。",
    responses={
        401: {"description": "未認証"},
    },
)
def list_exercises(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ExerciseService(db).list_for_user(current_user.id)


@router.post(
    "",
    response_model=ExerciseOut,
    status_code=status.HTTP_201_CREATED,
    summary="カスタム種目を作成",
    description="ログインユーザー専用のカスタム種目を新規作成します。同名の種目が既に存在する場合は 409 を返します。",
    responses={
        401: {"description": "未認証"},
        409: {"description": "同名の種目が既に存在する"},
    },
)
def create_exercise(
    payload: ExerciseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return ExerciseService(db).create_custom(
            user_id=current_user.id,
            name=payload.name,
            category=payload.category,
        )
    except DuplicateExerciseError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc
