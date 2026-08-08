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


class JobRecommendationResponse(BaseModel):
    job_id: int
    title: str
    company: str
    location: str
    experience_level: str
    description: str
    required_skills: str
    match_score: int
    matched_skills: list[str]
    missing_skills: list[str]
    resume_id: int