from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.job_match import JobMatchCreate, JobMatchResponse
from app.services.job_match_service import JobMatchService
from app.core.security import get_current_user

router = APIRouter(
    prefix="/matching",
    tags=["Job Matching"]
)
job_match_service = JobMatchService()
@router.post(
    "/",
    response_model=JobMatchResponse
)
def match_resume(
    request: JobMatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return job_match_service.match(
        db=db,
        resume_id=request.resume_id,
        job_id=request.job_id,
        current_user=current_user
    )