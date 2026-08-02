from sqlalchemy.orm import Session

from app.models.job import Job
from app.schemas.job import JobCreate


class JobRepository:

    def create(self, db: Session, job: JobCreate):
        db_job = Job(
            title=job.title,
            company=job.company,
            location=job.location,
            description=job.description,
            required_skills=job.required_skills,
            experience_level=job.experience_level
        )

        db.add(db_job)
        db.commit()
        db.refresh(db_job)

        return db_job

    def get_all(self, db: Session):
        return db.query(Job).all()

    def get_by_id(self, db: Session, job_id: int):
        return db.query(Job).filter(Job.id == job_id).first()

    def delete(self, db: Session, job: Job):
        db.delete(job)
        db.commit()


    def update(self, db: Session, db_job: Job, job):
        db_job.title = job.title
        db_job.company = job.company
        db_job.location = job.location
        db_job.description = job.description
        db_job.required_skills = job.required_skills
        db_job.experience_level = job.experience_level

        db.commit()
        db.refresh(db_job)

        return db_job    