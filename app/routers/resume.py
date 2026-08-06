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
    "/latest",
    response_model=ResumeResponse
)
def get_latest_resume(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    latest_resume = resume_service.resume_repository.get_latest_by_user(db, current_user.id)
    if not latest_resume:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="No resume uploaded yet.")
    return latest_resume

@router.get(
    "/latest/analysis",
    response_model=ResumeAnalysisResponse
)
def get_latest_resume_analysis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return resume_service.get_latest_analysis(
        db,
        current_user.id
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