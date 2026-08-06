import json

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.agents.job_match_agent import JobMatchAgent
from app.models.job_match import JobMatch
from app.models.user import User
from app.repositories.job_match_repository import JobMatchRepository
from app.repositories.job_repository import JobRepository
from app.repositories.resume_repository import ResumeRepository
from app.utils.matching import calculate_match_score


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

        # Get Resume
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

        # Get Job
        job = self.job_repository.get_by_id(
            db,
            job_id
        )

        if not job:
            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )

        # AI Matching
        ai_response = self.job_match_agent.match(
            resume.extracted_text,
            job.description
        )

        print("=" * 50)
        print("JOB MATCH")
        print("=" * 50)
        print(ai_response)
        print("=" * 50)

        # Extract JSON only
        start = ai_response.find("{")
        end = ai_response.rfind("}") + 1

        json_text = ai_response[start:end]

        result = json.loads(json_text)

        # Resume Skills
        resume_skills = []

        if resume.analysis:
            resume_skills = json.loads(
                resume.analysis.skills
            )

        # Job Skills
        job_skills = [
            skill.strip()
            for skill in job.required_skills.split(",")
        ]

        # Calculate Match Score
        calc_score = calculate_match_score(
            resume_skills,
            job_skills
        )

        strengths = result.get("strengths", [])
        missing = result.get("missing_skills", [])
        total_ai_skills = len(strengths) + len(missing)
        ai_ratio_score = int((len(strengths) / total_ai_skills) * 100) if total_ai_skills > 0 else 0

        ai_score = result.get("match_score")
        if isinstance(ai_score, (int, float)) and ai_score > 0:
            score = int(ai_score)
        else:
            score = max(ai_ratio_score, calc_score)

        # Save Match
        job_match = JobMatch(
            resume_id=resume.id,
            job_id=job.id,
            match_score=score,
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