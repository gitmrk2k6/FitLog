from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.pr import (
    METRIC_BEST_1RM,
    METRIC_MAX_WEIGHT,
    compute_pr,
    diff_metrics,
)
from app.repositories.personal_record_repository import (
    PersonalRecordRepository,
)


@dataclass
class PrUpdate:
    exercise_id: int
    metrics: list[str]


class PersonalRecordService:
    def __init__(self, db: Session) -> None:
        self.repo = PersonalRecordRepository(db)

    def apply_for_workout(
        self, user_id: int, workout_id: int
    ) -> list[PrUpdate]:
        """保存された記録に対しPR判定し、is_pr付与・PR更新・更新指標を返す。"""
        brief = self.repo.workout_set_brief(workout_id)
        current_ids = {sid for sid, _, _ in brief}
        # この記録で扱った種目（重量0は対象外）
        exercise_ids = sorted(
            {ex for _, ex, w in brief if w > 0}
        )
        updates: list[PrUpdate] = []
        for ex_id in exercise_ids:
            before = compute_pr(
                self.repo.user_set_rows(
                    user_id, ex_id, exclude_workout_id=workout_id
                )
            )
            after = compute_pr(self.repo.user_set_rows(user_id, ex_id))
            if after is None:
                continue
            updated = diff_metrics(before, after)
            self.repo.upsert(user_id, ex_id, after)
            if not updated:
                continue
            # 達成セット（①③のみ is_pr。②はセット単位でないため指標で表現）
            pr_set_ids: set[int] = set()
            if METRIC_MAX_WEIGHT in updated:
                pr_set_ids.add(after.max_weight_set_id)
            if METRIC_BEST_1RM in updated:
                pr_set_ids.add(after.best_1rm_set_id)
            self.repo.mark_sets_pr(
                [sid for sid in pr_set_ids if sid in current_ids]
            )
            updates.append(PrUpdate(exercise_id=ex_id, metrics=updated))
        return updates

    def recompute_exercises(
        self, user_id: int, exercise_ids: list[int]
    ) -> None:
        """編集/削除後、影響種目のPRを全履歴から再計算（整合維持）。"""
        for ex_id in exercise_ids:
            rows = self.repo.user_set_rows(user_id, ex_id)
            metrics = compute_pr(rows)
            if metrics is None:
                # 該当セットが消えた種目は personal_records も削除
                self.repo.delete_for(user_id, ex_id)
            else:
                self.repo.upsert(user_id, ex_id, metrics)

    def list_for_user(self, user_id: int):
        return self.repo.list_for_user(user_id)
