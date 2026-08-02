from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.schemas.job import JobCreate, JobUpdate
from app.repositories.job_repository import JobRepository
from app.schemas.job import JobCreate


class JobService:

    def __init__(self):
        self.job_repository = JobRepository()

    def create(self, db: Session, job: JobCreate):
        return self.job_repository.create(db, job)

    def get_all(self, db: Session):
        return self.job_repository.get_all(db)

    def get_by_id(self, db: Session, job_id: int):
        job = self.job_repository.get_by_id(db, job_id)

        if not job:
            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )

        return job

    def delete(self, db: Session, job_id: int):
        job = self.job_repository.get_by_id(db, job_id)

        if not job:
            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )

        self.job_repository.delete(db, job)

        return {
            "message": "Job deleted successfully"
        }
    
    def update(self, db: Session, job_id: int, job: JobUpdate):

        db_job = self.job_repository.get_by_id(db, job_id)

        if not db_job:
            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )

        return self.job_repository.update(db, db_job, job)