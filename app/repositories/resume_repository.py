from sqlalchemy.orm import Session

from app.models.resume import Resume


class ResumeRepository:

    def create(self, db: Session, resume: Resume):

        db.add(resume)

        db.commit()

        db.refresh(resume)

        return resume

    def get_by_user(self, db: Session, user_id: int):

        return db.query(Resume).filter(
            Resume.user_id == user_id
        ).all()