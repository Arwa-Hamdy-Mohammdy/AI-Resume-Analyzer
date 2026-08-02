from sqlalchemy.orm import Session

from app.models.resume_analysis import ResumeAnalysis


class ResumeAnalysisRepository:

    def create(
        self,
        db: Session,
        analysis: ResumeAnalysis
    ):
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        return analysis

    def get_by_resume_id(
        self,
        db: Session,
        resume_id: int
    ):
        return (
            db.query(ResumeAnalysis)
            .filter(ResumeAnalysis.resume_id == resume_id)
            .first()
        )