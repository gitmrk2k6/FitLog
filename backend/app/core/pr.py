"""自己ベスト(PR)判定の純粋ロジック（F-09）。

DB に依存しない計算のみ。フロント frontend/src/lib/stats.ts と
同じ式・同じ優先順位に揃える（画面と数値を一致させるため）。
"""

from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal


@dataclass(frozen=True)
class SetRow:
    """PR 計算の入力（重量0は呼び出し側で除外済みの前提）。"""

    set_id: int
    exercise_id: int
    workout_id: int
    performed_on: date
    weight_kg: Decimal
    reps: int


def epley_1rm(weight_kg: Decimal, reps: int) -> Decimal:
    """推定1RM = weight × (1 + reps/30)。stats.ts と同じく小数1桁に丸め。"""
    raw = weight_kg * (Decimal(1) + Decimal(reps) / Decimal(30))
    return (raw * 10).quantize(Decimal(1), rounding=ROUND_HALF_UP) / 10


@dataclass
class PrMetrics:
    # ① 最大重量
    max_weight_kg: Decimal
    max_weight_reps: int
    max_weight_set_id: int
    max_weight_on: date
    # ② ベストボリューム（1記録での種目Σ(重量×回数)）
    best_volume: Decimal
    best_volume_workout_id: int
    best_volume_on: date
    # ③ 推定1RMベスト
    best_est_1rm: Decimal
    best_1rm_weight_kg: Decimal
    best_1rm_reps: int
    best_1rm_set_id: int
    best_1rm_on: date


def compute_pr(rows: list[SetRow]) -> PrMetrics | None:
    """1種目分のセット群から3指標を算出。対象セットが無ければ None。"""
    if not rows:
        return None

    # ① 最大重量: 重量が大きい方。同重量なら回数が多い方を優先（stats.ts と同じ）
    best_w = rows[0]
    for r in rows[1:]:
        if r.weight_kg > best_w.weight_kg or (
            r.weight_kg == best_w.weight_kg and r.reps > best_w.reps
        ):
            best_w = r

    # ② ベストボリューム: 記録(workout)単位で Σ(重量×回数) を集計し最大
    vol_by_workout: dict[int, tuple[Decimal, date]] = {}
    for r in rows:
        cur, _ = vol_by_workout.get(r.workout_id, (Decimal(0), r.performed_on))
        vol_by_workout[r.workout_id] = (
            cur + r.weight_kg * r.reps,
            r.performed_on,
        )
    best_vol_wid, (best_vol, best_vol_on) = max(
        vol_by_workout.items(), key=lambda kv: kv[1][0]
    )

    # ③ 推定1RM: Epley が最大のセット
    best_rm = rows[0]
    best_rm_val = epley_1rm(rows[0].weight_kg, rows[0].reps)
    for r in rows[1:]:
        val = epley_1rm(r.weight_kg, r.reps)
        if val > best_rm_val:
            best_rm, best_rm_val = r, val

    return PrMetrics(
        max_weight_kg=best_w.weight_kg,
        max_weight_reps=best_w.reps,
        max_weight_set_id=best_w.set_id,
        max_weight_on=best_w.performed_on,
        best_volume=best_vol,
        best_volume_workout_id=best_vol_wid,
        best_volume_on=best_vol_on,
        best_est_1rm=best_rm_val,
        best_1rm_weight_kg=best_rm.weight_kg,
        best_1rm_reps=best_rm.reps,
        best_1rm_set_id=best_rm.set_id,
        best_1rm_on=best_rm.performed_on,
    )


# pr_updates で返す指標名
METRIC_MAX_WEIGHT = "max_weight"
METRIC_BEST_VOLUME = "best_volume"
METRIC_BEST_1RM = "best_est_1rm"


def diff_metrics(before: PrMetrics | None, after: PrMetrics) -> list[str]:
    """before（今回を除く過去最高）に対し after で更新された指標名。"""
    if before is None:
        # 初回はその種目の全指標が新規ベスト
        return [METRIC_MAX_WEIGHT, METRIC_BEST_VOLUME, METRIC_BEST_1RM]
    updated: list[str] = []
    if after.max_weight_kg > before.max_weight_kg or (
        after.max_weight_kg == before.max_weight_kg
        and after.max_weight_reps > before.max_weight_reps
    ):
        updated.append(METRIC_MAX_WEIGHT)
    if after.best_volume > before.best_volume:
        updated.append(METRIC_BEST_VOLUME)
    if after.best_est_1rm > before.best_est_1rm:
        updated.append(METRIC_BEST_1RM)
    return updated
