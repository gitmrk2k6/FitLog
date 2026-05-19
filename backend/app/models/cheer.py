from sqlalchemy import BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, CreatedAtMixin


class Cheer(Base, CreatedAtMixin):
    __tablename__ = "cheers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    workout_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("workouts.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("workout_id", "user_id", name="uq_cheers_workout_user"),
    )
