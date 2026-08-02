from pydantic import BaseModel


class JobCreate(BaseModel):
    title: str
    company: str
    location: str
    description: str
    required_skills: str
    experience_level: str


class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    location: str
    description: str
    required_skills: str
    experience_level: str

    model_config = {
        "from_attributes": True
    }

class JobUpdate(BaseModel):
    title: str
    company: str
    location: str
    description: str
    required_skills: str
    experience_level: str    