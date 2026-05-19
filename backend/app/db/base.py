"""Alembic autogenerate 用に Base.metadata へ全モデルを集約する。

このモジュールを import すれば 9 テーブルすべてが metadata に登録される。
"""

from app.db.base_class import Base  # noqa: F401
from app.models.advice import Advice  # noqa: F401
from app.models.cheer import Cheer  # noqa: F401
from app.models.exercise import Exercise  # noqa: F401
from app.models.follow import Follow  # noqa: F401
from app.models.goal import Goal  # noqa: F401
from app.models.personal_record import PersonalRecord  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.workout import Workout  # noqa: F401
from app.models.workout_set import WorkoutSet  # noqa: F401
