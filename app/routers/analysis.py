from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.resume_analysis import ResumeAnalysisResponse
from app.services.analysis_service import AnalysisService

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"]
)

analysis_service = AnalysisService()


@router.get("/latest", response_model=ResumeAnalysisResponse)
def get_latest_analysis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return analysis_service.get_latest_analysis(db, current_user.id)


@router.get("/{resume_id}", response_model=ResumeAnalysisResponse)
def get_resume_analysis(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return analysis_service.get_analysis_by_resume_id(db, resume_id)


@router.post("/{resume_id}/reanalyze", response_model=ResumeAnalysisResponse)
def reanalyze_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return analysis_service.reanalyze_resume(db, resume_id)
