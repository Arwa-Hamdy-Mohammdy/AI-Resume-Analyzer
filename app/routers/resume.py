from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from app.schemas.resume_analysis import ResumeAnalysisResponse
from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.resume import ResumeResponse
from app.services.resume_service import ResumeService
from app.core.dependencies import get_current_user

router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"]
)

resume_service = ResumeService()


@router.post("/upload", response_model=ResumeResponse)
def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return resume_service.upload_resume(
        db=db,
        file=file,
        current_user=current_user
    )

@router.get(
    "/{resume_id}/analysis",
    response_model=ResumeAnalysisResponse
)
def get_resume_analysis(
    resume_id: int,
    db: Session = Depends(get_db),
):
    return resume_service.get_analysis(
        db,
        resume_id
    )