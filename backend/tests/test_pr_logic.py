from datetime import date
from decimal import Decimal

from app.core.pr import (
    METRIC_BEST_1RM,
    METRIC_BEST_VOLUME,
    METRIC_MAX_WEIGHT,
    SetRow,
    compute_pr,
    diff_metrics,
    epley_1rm,
)


def _row(set_id, wid, on, w, reps, ex=1):
    return SetRow(
        set_id=set_id,
        exercise_id=ex,
        workout_id=wid,
        performed_on=date.fromisoformat(on),
        weight_kg=Decimal(str(w)),
        reps=reps,
    )


def test_epley_matches_frontend_formula():
    # 75 × (1 + 6/30) = 90.0
    assert epley_1rm(Decimal("75"), 6) == Decimal("90.0")
    # 60 × (1 + 10/30) = 80.0
    assert epley_1rm(Decimal("60"), 10) == Decimal("80.0")


def test_compute_pr_none_when_empty():
    assert compute_pr([]) is None


def test_max_weight_tie_breaks_on_higher_reps():
    rows = [
        _row(1, 1, "2026-05-01", 100, 3),
        _row(2, 2, "2026-05-02", 100, 5),  # 同kg・高レップ → こちらが①
    ]
    m = compute_pr(rows)
    assert m.max_weight_kg == Decimal("100")
    assert m.max_weight_reps == 5
    assert m.max_weight_set_id == 2


def test_best_volume_is_per_workout_sum():
    rows = [
        _row(1, 1, "2026-05-01", 60, 10),  # workout1: 600
        _row(2, 1, "2026-05-01", 60, 10),  # workout1 合計 1200
        _row(3, 2, "2026-05-02", 100, 5),  # workout2: 500
    ]
    m = compute_pr(rows)
    assert m.best_volume == Decimal("1200")
    assert m.best_volume_workout_id == 1


def test_diff_first_record_is_all_metrics():
    after = compute_pr([_row(1, 1, "2026-05-01", 60, 10)])
    assert set(diff_metrics(None, after)) == {
        METRIC_MAX_WEIGHT,
        METRIC_BEST_VOLUME,
        METRIC_BEST_1RM,
    }


def test_diff_detects_only_changed_metric():
    before = compute_pr([_row(1, 1, "2026-05-01", 60, 10)])
    # 重量だけ上げ、ボリューム/1RMは下げる構成
    after = compute_pr(
        [_row(1, 1, "2026-05-01", 60, 10), _row(2, 2, "2026-05-02", 80, 1)]
    )
    updated = diff_metrics(before, after)
    assert METRIC_MAX_WEIGHT in updated
    assert METRIC_BEST_VOLUME not in updated


def test_diff_empty_when_no_improvement():
    before = compute_pr([_row(1, 1, "2026-05-01", 100, 10)])
    after = compute_pr(
        [_row(1, 1, "2026-05-01", 100, 10), _row(2, 2, "2026-05-02", 50, 5)]
    )
    assert diff_metrics(before, after) == []
