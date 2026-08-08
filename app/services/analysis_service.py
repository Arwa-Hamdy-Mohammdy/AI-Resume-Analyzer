import json
import re
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.agents.resume_agent import ResumeAgent
from app.models.resume_analysis import ResumeAnalysis
from app.repositories.resume_analysis_repository import ResumeAnalysisRepository
from app.repositories.resume_repository import ResumeRepository


class AnalysisService:

    def __init__(self):
        self.analysis_repository = ResumeAnalysisRepository()
        self.resume_repository = ResumeRepository()
        self.resume_agent = ResumeAgent()

    def get_analysis_by_resume_id(self, db: Session, resume_id: int) -> ResumeAnalysis:
        analysis = self.analysis_repository.get_by_resume_id(db, resume_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Resume analysis not found")
        return analysis

    def get_latest_analysis(self, db: Session, user_id: int) -> ResumeAnalysis:
        latest_resume = self.resume_repository.get_latest_by_user(db, user_id)
        if not latest_resume:
            raise HTTPException(status_code=404, detail="No resume uploaded yet.")

        analysis = self.analysis_repository.get_by_resume_id(db, latest_resume.id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found for latest resume.")
        return analysis

    def reanalyze_resume(self, db: Session, resume_id: int) -> ResumeAnalysis:
        resume = self.resume_repository.get_by_id(db, resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")

        raw_analysis = self.resume_agent.analyze_resume(resume.extracted_text)
        
        # Clean response
        raw_analysis = raw_analysis.strip().replace("```json", "").replace("```", "")
        match = re.search(r"\{.*\}", raw_analysis, re.DOTALL)
        if not match:
            raise HTTPException(status_code=500, detail="AI did not return valid JSON.")
        
        try:
            analysis_json = json.loads(match.group())
        except Exception:
            raise HTTPException(status_code=500, detail="Invalid AI JSON output.")

        tech_skills = analysis_json.get("technical_skills", [])
        soft_sk = analysis_json.get("soft_skills", [])
        combined_skills = analysis_json.get("skills", [])
        if not combined_skills:
            combined_skills = list(set(tech_skills + soft_sk))

        score_val = analysis_json.get("overall_score", 75)
        try:
            score_val = int(score_val)
        except (ValueError, TypeError):
            score_val = 75

        existing = self.analysis_repository.get_by_resume_id(db, resume_id)
        if existing:
            existing.summary = analysis_json.get("summary", "")
            existing.skills = json.dumps(combined_skills)
            existing.technical_skills = json.dumps(tech_skills)
            existing.soft_skills = json.dumps(soft_sk)
            existing.education = json.dumps(analysis_json.get("education", []))
            existing.experience = json.dumps(analysis_json.get("experience", []))
            existing.strengths = json.dumps(analysis_json.get("strengths", []))
            existing.weaknesses = json.dumps(analysis_json.get("weaknesses", []))
            existing.overall_score = score_val
            db.commit()
            db.refresh(existing)
            return existing

        new_analysis = ResumeAnalysis(
            resume_id=resume.id,
            summary=analysis_json.get("summary", ""),
            skills=json.dumps(combined_skills),
            technical_skills=json.dumps(tech_skills),
            soft_skills=json.dumps(soft_sk),
            education=json.dumps(analysis_json.get("education", [])),
            experience=json.dumps(analysis_json.get("experience", [])),
            strengths=json.dumps(analysis_json.get("strengths", [])),
            weaknesses=json.dumps(analysis_json.get("weaknesses", [])),
            overall_score=score_val
        )
        return self.analysis_repository.create(db, new_analysis)
