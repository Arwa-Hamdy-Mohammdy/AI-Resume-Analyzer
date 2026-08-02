from pydantic import BaseModel


class ResumeAnalysisResponse(BaseModel):
    summary: str
    skills: str
    education: str
    experience: str

    model_config = {
        "from_attributes": True
    }