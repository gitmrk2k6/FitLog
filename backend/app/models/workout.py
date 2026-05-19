from datetime import date

from sqlalchemy import BigInteger, Date, ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, TimestampMixin


class Workout(Base, TimestampMixin):
    __tablename__ = "workouts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    performed_on: Mapped[date] = mapped_column(Date, nullable=False)
    memo: Mapped[str | None] = mapped_column(String(280), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    __table_args__ = (
        Index(
            "idx_workouts_user_date",
            "user_id",
            text("performed_on DESC"),
        ),
    )
