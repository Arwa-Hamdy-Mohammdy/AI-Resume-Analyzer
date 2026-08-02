from pydantic import BaseModel


class JobMatchCreate(BaseModel):
    resume_id: int
    job_id: int


class JobMatchResponse(BaseModel):
    id: int
    resume_id: int
    job_id: int
    match_score: int
    missing_skills: str
    strengths: str
    recommendations: str

    model_config = {
        "from_attributes": True
    }