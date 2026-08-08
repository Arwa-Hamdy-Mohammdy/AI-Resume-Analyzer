from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.job_match import JobMatchCreate, JobMatchResponse, JobRecommendationResponse
from app.services.job_match_service import JobMatchService

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


@router.get(
    "/recommendations",
    response_model=list[JobRecommendationResponse]
)
def get_job_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return job_match_service.get_recommendations(
        db=db,
        current_user=current_user
    )


@router.get(
    "/history"
)
def get_match_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return job_match_service.get_history(
        db=db,
        current_user=current_user
    )
