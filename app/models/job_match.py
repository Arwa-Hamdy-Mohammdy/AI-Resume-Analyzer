from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.database import Base


class JobMatch(Base):
    __tablename__ = "job_matches"

    id = Column(Integer, primary_key=True, index=True)

    resume_id = Column(
        Integer,
        ForeignKey("resumes.id"),
        nullable=False
    )

    job_id = Column(
        Integer,
        ForeignKey("jobs.id"),
        nullable=False
    )

    match_score = Column(Integer)

    missing_skills = Column(Text)

    strengths = Column(Text)

    recommendations = Column(Text)

    resume = relationship(
        "Resume",
        back_populates="matches"
    )

    job = relationship(
        "Job",
        back_populates="matches"
    )