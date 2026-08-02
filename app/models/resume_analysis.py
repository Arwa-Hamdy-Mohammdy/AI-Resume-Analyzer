from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.database import Base


class ResumeAnalysis(Base):
    __tablename__ = "resume_analysis"

    id = Column(Integer, primary_key=True, index=True)

    resume_id = Column(Integer, ForeignKey("resumes.id"))

    summary = Column(Text)

    skills = Column(Text)

    education = Column(Text)

    experience = Column(Text)

    resume = relationship(
        "Resume",
        back_populates="analysis"
    )