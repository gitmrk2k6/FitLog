from datetime import date
from decimal import Decimal

from sqlalchemy import BigInteger, Date, ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, TimestampMixin


class PersonalRecord(Base, TimestampMixin):
    """種目別の自己ベスト（F-09）。3指標を分けて保持する。"""

    __tablename__ = "personal_records"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    exercise_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False
    )

    # ① 最大重量
    max_weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    max_weight_reps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_weight_set_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("workout_sets.id", ondelete="SET NULL"), nullable=True
    )
    max_weight_on: Mapped[date | None] = mapped_column(Date, nullable=True)

    # ② ベストボリューム（1記録での種目Σ(重量×回数×全セット)）
    best_volume: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    best_volume_workout_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("workouts.id", ondelete="SET NULL"), nullable=True
    )
    best_volume_on: Mapped[date | None] = mapped_column(Date, nullable=True)

    # ③ 推定1RMベスト
    best_est_1rm: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    best_1rm_weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    best_1rm_reps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    best_1rm_set_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("workout_sets.id", ondelete="SET NULL"), nullable=True
    )
    best_1rm_on: Mapped[date | None] = mapped_column(Date, nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "exercise_id", name="uq_pr_user_exercise"),
    )
