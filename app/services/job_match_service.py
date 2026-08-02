import json
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.agents.job_match_agent import JobMatchAgent
from app.models.job_match import JobMatch
from app.repositories.job_match_repository import JobMatchRepository
from app.repositories.job_repository import JobRepository
from app.repositories.resume_repository import ResumeRepository
from app.models.user import User

class JobMatchService:

    def __init__(self):
        self.resume_repository = ResumeRepository()
        self.job_repository = JobRepository()
        self.job_match_repository = JobMatchRepository()
        self.job_match_agent = JobMatchAgent()

    def match(
        self,
        db: Session,
        resume_id: int,
        job_id: int,
        current_user: User
    ):

        resume = self.resume_repository.get_by_id(
            db,
            resume_id
        )

        if not resume:
            raise HTTPException(
                status_code=404,
                detail="Resume not found"
            )
        if resume.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You are not allowed to access this resume."
         )
        job = self.job_repository.get_by_id(
            db,
            job_id
        )

        if not job:
            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )

        ai_response = self.job_match_agent.match(
            resume.extracted_text,
            job.description
        )

        print("=" * 50)
        print("JOB MATCH")
        print("=" * 50)
        print(ai_response)
        print("=" * 50)

        result = json.loads(ai_response)

        job_match = JobMatch(
            resume_id=resume.id,
            job_id=job.id,
            match_score=result.get("match_score", 0),
            missing_skills=json.dumps(
                result.get("missing_skills", [])
            ),
            strengths=json.dumps(
                result.get("strengths", [])
            ),
            recommendations=json.dumps(
                result.get("recommendations", [])
            )
        )

        return self.job_match_repository.create(
            db,
            job_match
        )