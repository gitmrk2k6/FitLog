from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.workout import WorkoutDetail
from app.services.workout_service import (
    NotWorkoutOwnerError,
    PhotoEmptyError,
    PhotoTooLargeError,
    PhotoTypeError,
    WorkoutNotFoundError,
    WorkoutService,
)
from app.storage.factory import get_storage

router = APIRouter(prefix="/workouts/{workout_id}/photo", tags=["photos"])


def _handle(exc: Exception) -> HTTPException:
    if isinstance(exc, WorkoutNotFoundError):
        return HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, NotWorkoutOwnerError):
        return HTTPException(status.HTTP_403_FORBIDDEN, detail=str(exc))
    if isinstance(
        exc, (PhotoTypeError, PhotoTooLargeError, PhotoEmptyError)
    ):
        return HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        )
    raise exc


@router.put(
    "",
    response_model=WorkoutDetail,
    summary="ワークアウットに写真をアップロード",
    description="JPEG / PNG / GIF のいずれか、最大5MB のファイルをワークアウットに紐づけます。既存写真がある場合は上書きされます（F-10）。",
    responses={
        401: {"description": "未認証"},
        403: {"description": "他ユーザーのワークアウットへの操作"},
        404: {"description": "ワークアウットが見つからない"},
        422: {"description": "ファイル形式が不正またはサイズ超過（5MB 以上）"},
    },
)
async def upload_photo(
    workout_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    storage=Depends(get_storage),
):
    data = await file.read()
    try:
        return WorkoutService(db).set_photo(
            current_user.id,
            workout_id,
            data=data,
            content_type=file.content_type or "",
            storage=storage,
        )
    except (
        WorkoutNotFoundError,
        NotWorkoutOwnerError,
        PhotoTypeError,
        PhotoTooLargeError,
        PhotoEmptyError,
    ) as exc:
        raise _handle(exc) from exc


@router.delete(
    "",
    response_model=WorkoutDetail,
    summary="ワークアウットの写真を削除",
    description="ワークアウットに紐づく写真を削除します。ストレージ上のファイルも合わせて削除されます（F-10）。",
    responses={
        401: {"description": "未認証"},
        403: {"description": "他ユーザーのワークアウットへの操作"},
        404: {"description": "ワークアウットが見つからない"},
    },
)
def delete_photo(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return WorkoutService(db).clear_photo(current_user.id, workout_id)
    except (WorkoutNotFoundError, NotWorkoutOwnerError) as exc:
        raise _handle(exc) from exc
