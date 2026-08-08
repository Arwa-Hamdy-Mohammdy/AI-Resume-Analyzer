from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.database import get_db
from app.schemas.job import JobCreate, JobResponse
from app.services.job_service import JobService
from app.schemas.job import JobCreate, JobResponse, JobUpdate

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)

job_service = JobService()


@router.post("/", response_model=JobResponse)
def create_job(
    job: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return job_service.create(db, job)


@router.get("/", response_model=list[JobResponse])
def get_jobs(db: Session = Depends(get_db)):
    return job_service.get_all(db)


@router.get("/search", response_model=list[JobResponse])
def search_jobs(
    q: str = None,
    location: str = None,
    experience_level: str = None,
    company: str = None,
    db: Session = Depends(get_db)
):
    return job_service.search_jobs(
        db=db,
        q=q,
        location=location,
        experience_level=experience_level,
        company=company
    )


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    return job_service.get_by_id(db, job_id)


@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return job_service.delete(db, job_id)

@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return job_service.update(db, job_id, job)