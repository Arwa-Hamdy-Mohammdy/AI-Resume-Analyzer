from fastapi import FastAPI
from app.models.job import Job
from app.database import Base, engine
from app.models.user import User
from app.routers.auth import router as auth_router
from app.routers.jobs import router as jobs_router
from app.routers.resume import router as resume_router
from app.models.resume import Resume
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Resume Analyzer",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(jobs_router)
app.include_router(resume_router)

@app.get("/")
def home():
    return {
        "message": "Welcome to AI Resume Analyzer API"
    }