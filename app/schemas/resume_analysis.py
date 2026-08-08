from typing import Optional
from pydantic import BaseModel


class ResumeAnalysisResponse(BaseModel):
    id: Optional[int] = None
    resume_id: Optional[int] = None
    summary: Optional[str] = ""
    skills: Optional[str] = ""
    technical_skills: Optional[str] = ""
    soft_skills: Optional[str] = ""
    education: Optional[str] = ""
    experience: Optional[str] = ""
    strengths: Optional[str] = ""
    weaknesses: Optional[str] = ""
    overall_score: Optional[int] = 70

    model_config = {
        "from_attributes": True
    }