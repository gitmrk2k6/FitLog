from datetime import date
from decimal import Decimal

from sqlalchemy import BigInteger, CheckConstraint, Date, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, CreatedAtMixin


class Goal(Base, CreatedAtMixin):
    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    period_type: Mapped[str] = mapped_column(String(10), nullable=False)
    metric: Mapped[str] = mapped_column(String(10), nullable=False)
    target_value: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    start_on: Mapped[date] = mapped_column(Date, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "period_type", name="uq_goals_user_period"),
        CheckConstraint("target_value > 0", name="target_value_positive"),
        CheckConstraint(
            "period_type IN ('weekly', 'monthly')", name="period_type_valid"
        ),
        CheckConstraint(
            "metric IN ('sessions', 'volume')", name="metric_valid"
        ),
    )
