from sqlalchemy.orm import Session

from app.core import messages
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository


class DuplicateEmailError(Exception):
    """email が既に登録済み。"""


class DuplicateUsernameError(Exception):
    """username が既に使用済み。"""


class InvalidCredentialsError(Exception):
    """email / password が一致しない。"""


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)

    def register(self, *, username: str, email: str, password: str) -> User:
        if self.users.get_by_email(email):
            raise DuplicateEmailError(messages.EMAIL_ALREADY_REGISTERED)
        if self.users.get_by_username(username):
            raise DuplicateUsernameError(messages.USERNAME_ALREADY_TAKEN)
        return self.users.create(
            username=username,
            email=email,
            password_digest=hash_password(password),
        )

    def authenticate(self, *, email: str, password: str) -> User:
        user = self.users.get_by_email(email)
        # ユーザー存在有無を漏らさないため失敗は単一メッセージに統一
        if user is None or not verify_password(password, user.password_digest):
            raise InvalidCredentialsError(messages.INVALID_CREDENTIALS)
        return user

    def issue_token(self, user: User) -> str:
        return create_access_token(user.id)
