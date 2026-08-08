from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.services.rag_service import RAGService

router = APIRouter(
    prefix="/rag",
    tags=["RAG & AI Optimizer"]
)

rag_service = RAGService()


class RAGRequest(BaseModel):
    resume_id: int
    job_id: int


@router.post("/optimize-bullets")
def optimize_bullets(
    request: RAGRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return rag_service.optimize_bullets(
        db=db,
        resume_id=request.resume_id,
        job_id=request.job_id,
        current_user=current_user
    )


@router.post("/skill-roadmap")
def skill_roadmap(
    request: RAGRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return rag_service.generate_roadmap(
        db=db,
        resume_id=request.resume_id,
        job_id=request.job_id,
        current_user=current_user
    )
