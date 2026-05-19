from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, CreatedAtMixin


class Follow(Base, CreatedAtMixin):
    __tablename__ = "follows"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    follower_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    following_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("follower_id", "following_id", name="uq_follows_pair"),
        CheckConstraint("follower_id <> following_id", name="no_self_follow"),
        Index("idx_follows_follower", "follower_id"),
        Index("idx_follows_following", "following_id"),
    )
