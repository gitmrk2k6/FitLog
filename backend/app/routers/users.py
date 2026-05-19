from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.follow import FollowStateOut, ProfileOut, UserBrief
from app.services.follow_service import (
    AlreadyFollowingError,
    CannotFollowSelfError,
    FollowService,
    NotFollowingError,
    UserNotFoundError,
)

router = APIRouter(prefix="/users", tags=["users"])


def _handle(exc: Exception) -> HTTPException:
    if isinstance(exc, UserNotFoundError):
        return HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, CannotFollowSelfError):
        return HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        )
    if isinstance(exc, AlreadyFollowingError):
        return HTTPException(status.HTTP_409_CONFLICT, detail=str(exc))
    if isinstance(exc, NotFollowingError):
        return HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))
    raise exc


@router.get("/search", response_model=list[UserBrief])
def search_users(
    q: str = Query(min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return FollowService(db).search(current_user.id, q)


@router.get("/{user_id}", response_model=ProfileOut)
def get_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return FollowService(db).profile(current_user.id, user_id)
    except UserNotFoundError as exc:
        raise _handle(exc) from exc


@router.get("/{user_id}/following", response_model=list[UserBrief])
def list_following(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return FollowService(db).list_following(current_user.id, user_id)
    except UserNotFoundError as exc:
        raise _handle(exc) from exc


@router.get("/{user_id}/followers", response_model=list[UserBrief])
def list_followers(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return FollowService(db).list_followers(current_user.id, user_id)
    except UserNotFoundError as exc:
        raise _handle(exc) from exc


@router.post(
    "/{user_id}/follow",
    response_model=FollowStateOut,
    status_code=status.HTTP_201_CREATED,
)
def follow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return FollowService(db).follow(current_user.id, user_id)
    except (
        UserNotFoundError,
        CannotFollowSelfError,
        AlreadyFollowingError,
    ) as exc:
        raise _handle(exc) from exc


@router.delete(
    "/{user_id}/follow", status_code=status.HTTP_204_NO_CONTENT
)
def unfollow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        FollowService(db).unfollow(current_user.id, user_id)
    except (UserNotFoundError, NotFollowingError) as exc:
        raise _handle(exc) from exc
