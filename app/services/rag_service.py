import json
import re
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.agents.rag_agent import RAGAgent
from app.models.user import User
from app.rag.retriever import Retriever
from app.repositories.job_match_repository import JobMatchRepository
from app.repositories.job_repository import JobRepository
from app.repositories.resume_repository import ResumeRepository


class RAGService:
    def __init__(self):
        self.retriever = Retriever()
        self.rag_agent = RAGAgent()
        self.resume_repository = ResumeRepository()
        self.job_repository = JobRepository()
        self.job_match_repository = JobMatchRepository()

    def optimize_bullets(self, db: Session, resume_id: int, job_id: int, current_user: User):
        resume = self.resume_repository.get_by_id(db, resume_id)
        if not resume or resume.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Resume not found")

        job = self.job_repository.get_by_id(db, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job position not found")

        # Fetch missing skills if match exists
        missing_skills = []
        job_match = self.job_match_repository.get_by_resume_and_job(db, resume_id, job_id) if hasattr(self.job_match_repository, 'get_by_resume_and_job') else None
        if job_match:
            try:
                missing_skills = json.loads(job_match.missing_skills)
            except Exception:
                missing_skills = []

        query = f"{job.title} {job.required_skills} {' '.join(missing_skills)} bullet points ATS rules"
        rag_context = self.retriever.retrieve_context(query, top_k=3)

        raw_response = self.rag_agent.optimize_bullets(
            resume_text=resume.extracted_text or "",
            job_title=job.title,
            job_description=job.description,
            missing_skills=missing_skills,
            rag_context=rag_context
        )

        return self._clean_and_parse_json(raw_response)

    def generate_roadmap(self, db: Session, resume_id: int, job_id: int, current_user: User):
        resume = self.resume_repository.get_by_id(db, resume_id)
        if not resume or resume.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Resume not found")

        job = self.job_repository.get_by_id(db, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job position not found")

        missing_skills = []
        job_match = self.job_match_repository.get_by_resume_and_job(db, resume_id, job_id) if hasattr(self.job_match_repository, 'get_by_resume_and_job') else None
        if job_match:
            try:
                missing_skills = json.loads(job_match.missing_skills)
            except Exception:
                missing_skills = []

        if not missing_skills and job.required_skills:
            missing_skills = [s.strip() for s in job.required_skills.split(",") if s.strip()]

        query = f"roadmap learning course {' '.join(missing_skills)}"
        rag_context = self.retriever.retrieve_context(query, top_k=3)

        raw_response = self.rag_agent.generate_roadmap(
            missing_skills=missing_skills,
            rag_context=rag_context
        )

        return self._clean_and_parse_json(raw_response)

    def _clean_and_parse_json(self, response_str: str) -> dict:
        cleaned = response_str.strip()
        cleaned = cleaned.replace("```json", "").replace("```", "")
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start != -1 and end != -1:
            json_text = cleaned[start:end]
            try:
                return json.loads(json_text)
            except Exception as e:
                print(f"[RAGService] JSON parse error: {e}")
        return {"raw_output": response_str}
