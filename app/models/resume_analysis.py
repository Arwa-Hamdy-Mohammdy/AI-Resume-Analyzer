from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.database import Base


class ResumeAnalysis(Base):
    __tablename__ = "resume_analysis"

    id = Column(Integer, primary_key=True, index=True)

    resume_id = Column(Integer, ForeignKey("resumes.id"))

    summary = Column(Text)

    skills = Column(Text)

    technical_skills = Column(Text, nullable=True)

    soft_skills = Column(Text, nullable=True)

    education = Column(Text)

    experience = Column(Text)

    strengths = Column(Text, nullable=True)

    weaknesses = Column(Text, nullable=True)

    overall_score = Column(Integer, nullable=True, default=70)

    resume = relationship(
        "Resume",
        back_populates="analysis"
    )