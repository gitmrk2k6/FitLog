"""seed common exercises

Revision ID: 8a1f2c3d4e5b
Revises: 79bbea48ca69
Create Date: 2026-05-19

共通種目マスタ（created_by = NULL）を投入する。
フロントプロトタイプのモック種目と整合させる。
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "8a1f2c3d4e5b"
down_revision: str | None = "79bbea48ca69"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

COMMON_EXERCISES = [
    {"name": "ベンチプレス", "category": "chest"},
    {"name": "スクワット", "category": "legs"},
    {"name": "デッドリフト", "category": "back"},
    {"name": "懸垂", "category": "back"},
    {"name": "ランニング", "category": "cardio"},
]


def upgrade() -> None:
    exercises = sa.table(
        "exercises",
        sa.column("name", sa.String),
        sa.column("category", sa.String),
        sa.column("created_by", sa.BigInteger),
    )
    op.bulk_insert(
        exercises,
        [{**e, "created_by": None} for e in COMMON_EXERCISES],
    )


def downgrade() -> None:
    names = tuple(e["name"] for e in COMMON_EXERCISES)
    op.execute(
        sa.text(
            "DELETE FROM exercises "
            "WHERE created_by IS NULL AND name IN :names"
        ).bindparams(sa.bindparam("names", expanding=True, value=list(names)))
    )
