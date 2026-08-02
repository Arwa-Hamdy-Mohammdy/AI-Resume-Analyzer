from sqlalchemy.orm import Session

from app.models.job_match import JobMatch


class JobMatchRepository:

    def create(
        self,
        db: Session,
        job_match: JobMatch
    ):
        db.add(job_match)
        db.commit()
        db.refresh(job_match)

        return job_match

    def get_by_resume_and_job(
        self,
        db: Session,
        resume_id: int,
        job_id: int
    ):

        return (
            db.query(JobMatch)
            .filter(
                JobMatch.resume_id == resume_id,
                JobMatch.job_id == job_id
            )
            .first()
        )

    def get_by_id(
        self,
        db: Session,
        match_id: int
    ):

        return (
            db.query(JobMatch)
            .filter(JobMatch.id == match_id)
            .first()
        )