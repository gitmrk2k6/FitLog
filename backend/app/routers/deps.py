from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core import messages
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=messages.NOT_AUTHENTICATED,
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exc
    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_exc
    user = UserRepository(db).get_by_id(user_id)
    if user is None:
        raise credentials_exc
    return user
