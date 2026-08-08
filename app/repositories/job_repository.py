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

    def search(
        self,
        db: Session,
        q: str = None,
        location: str = None,
        experience_level: str = None,
        company: str = None
    ):
        query = db.query(Job)

        if q:
            pattern = f"%{q.strip()}%"
            query = query.filter(
                (Job.title.ilike(pattern)) |
                (Job.description.ilike(pattern)) |
                (Job.required_skills.ilike(pattern)) |
                (Job.company.ilike(pattern))
            )

        if location:
            query = query.filter(Job.location.ilike(f"%{location.strip()}%"))

        if experience_level:
            query = query.filter(Job.experience_level.ilike(f"%{experience_level.strip()}%"))

        if company:
            query = query.filter(Job.company.ilike(f"%{company.strip()}%"))

        return query.all()