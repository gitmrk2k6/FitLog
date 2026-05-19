from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.dashboard import PersonalRecordOut
from app.services.personal_record_service import PersonalRecordService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/personal-records", response_model=list[PersonalRecordOut])
def personal_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = PersonalRecordService(db).list_for_user(current_user.id)
    return [
        PersonalRecordOut(
            exercise_id=pr.exercise_id,
            exercise_name=name,
            max_weight_kg=pr.max_weight_kg,
            max_weight_reps=pr.max_weight_reps,
            max_weight_on=pr.max_weight_on,
            best_volume=pr.best_volume,
            best_volume_on=pr.best_volume_on,
            best_est_1rm=pr.best_est_1rm,
            best_1rm_weight_kg=pr.best_1rm_weight_kg,
            best_1rm_reps=pr.best_1rm_reps,
            best_1rm_on=pr.best_1rm_on,
        )
        for pr, name in rows
    ]
