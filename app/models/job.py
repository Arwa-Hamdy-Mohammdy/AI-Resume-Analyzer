from sqlalchemy import Column, Integer, String, Text

from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200), nullable=False)

    company = Column(String(200), nullable=False)

    location = Column(String(200), nullable=False)

    description = Column(Text, nullable=False)

    required_skills = Column(Text, nullable=False)

    experience_level = Column(String(100), nullable=False)