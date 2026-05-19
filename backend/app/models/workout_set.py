from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, CheckConstraint, ForeignKey, Index, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, CreatedAtMixin


class WorkoutSet(Base, CreatedAtMixin):
    __tablename__ = "workout_sets"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    workout_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("workouts.id", ondelete="CASCADE"), nullable=False
    )
    # 種目は参照中なら削除させない（RESTRICT）
    exercise_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("exercises.id", ondelete="RESTRICT"), nullable=False
    )
    set_no: Mapped[int] = mapped_column(Integer, nullable=False)
    weight_kg: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    reps: Mapped[int] = mapped_column(Integer, nullable=False)
    is_pr: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")

    __table_args__ = (
        CheckConstraint("weight_kg >= 0", name="weight_non_negative"),
        CheckConstraint("reps >= 1", name="reps_positive"),
        CheckConstraint("set_no >= 1", name="set_no_positive"),
        Index("idx_sets_workout", "workout_id"),
        Index("idx_sets_user_exercise", "exercise_id"),
    )
