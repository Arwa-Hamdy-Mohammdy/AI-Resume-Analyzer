import json

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.agents.job_match_agent import JobMatchAgent
from app.models.job_match import JobMatch
from app.models.user import User
from app.repositories.job_match_repository import JobMatchRepository
from app.repositories.job_repository import JobRepository
from app.repositories.resume_repository import ResumeRepository
from app.utils.matching import calculate_match_score, refine_match_results, is_skill_matched


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
            try:
                resume_skills = json.loads(
                    resume.analysis.skills
                )
            except Exception:
                resume_skills = []

        # Job Skills
        job_skills = [
            skill.strip()
            for skill in job.required_skills.split(",")
            if skill.strip()
        ]

        ai_strengths = result.get("strengths", [])
        ai_missing = result.get("missing_skills", [])

        # Cross-check and refine results to guarantee zero false missing skills!
        refined_strengths, refined_missing = refine_match_results(
            resume_skills=resume_skills,
            job_skills=job_skills,
            ai_missing=ai_missing,
            ai_strengths=ai_strengths,
            resume_text=resume.extracted_text or ""
        )

        # Calculate exact required skills match score
        calc_score = calculate_match_score(
            resume_skills,
            job_skills,
            resume.extracted_text or ""
        )

        # Count actual matched required skills vs total required skills
        matched_job_skills_count = sum(
            1 for js in job_skills if is_skill_matched(js, resume_skills, resume.extracted_text or "")
        )

        if job_skills:
            required_skills_score = int((matched_job_skills_count / len(job_skills)) * 100)
        else:
            required_skills_score = calc_score

        ai_score = result.get("match_score")
        if job_skills and matched_job_skills_count == 0:
            final_score = 0
        elif isinstance(ai_score, (int, float)) and ai_score > 0:
            # Weighted average between direct required skills match (70%) and AI evaluation (30%)
            final_score = int(0.7 * required_skills_score + 0.3 * ai_score)
        else:
            final_score = required_skills_score

        # Ensure score stays bounded [0, 100]
        final_score = max(0, min(100, final_score))

        # Check if match record already exists in DB
        existing_match = self.job_match_repository.get_by_resume_and_job(db, resume.id, job.id) if hasattr(self.job_match_repository, 'get_by_resume_and_job') else None

        if existing_match:
            existing_match.match_score = final_score
            existing_match.missing_skills = json.dumps(refined_missing)
            existing_match.strengths = json.dumps(refined_strengths)
            existing_match.recommendations = json.dumps(result.get("recommendations", []))
            db.commit()
            db.refresh(existing_match)
            return existing_match

        # Save Match
        job_match = JobMatch(
            resume_id=resume.id,
            job_id=job.id,
            match_score=final_score,
            missing_skills=json.dumps(refined_missing),
            strengths=json.dumps(refined_strengths),
            recommendations=json.dumps(
                result.get("recommendations", [])
            )
        )

        return self.job_match_repository.create(
            db,
            job_match
        )

    def get_recommendations(self, db: Session, current_user: User):
        latest_resume = self.resume_repository.get_latest_by_user(db, current_user.id)
        if not latest_resume:
            raise HTTPException(status_code=404, detail="No resume uploaded yet.")

        resume_skills = []
        if latest_resume.analysis:
            try:
                raw_skills = latest_resume.analysis.skills
                if raw_skills:
                    resume_skills = json.loads(raw_skills)
            except Exception:
                resume_skills = []

        resume_text = latest_resume.extracted_text or ""
        all_jobs = self.job_repository.get_all(db)
        recommendations = []

        for job in all_jobs:
            # Check if an existing match calculation is saved in DB for this resume & job
            saved_match = db.query(JobMatch).filter(
                JobMatch.resume_id == latest_resume.id,
                JobMatch.job_id == job.id
            ).first()

            if saved_match:
                try:
                    matched_skills = json.loads(saved_match.strengths)
                except Exception:
                    matched_skills = []
                try:
                    missing_skills = json.loads(saved_match.missing_skills)
                except Exception:
                    missing_skills = []
                
                score = saved_match.match_score
            else:
                job_skills = [s.strip() for s in job.required_skills.split(",") if s.strip()]
                matched_skills = []
                missing_skills = []

                for js in job_skills:
                    if is_skill_matched(js, resume_skills, resume_text):
                        matched_skills.append(js)
                    else:
                        missing_skills.append(js)

                score = calculate_match_score(resume_skills, job_skills, resume_text)

            recommendations.append({
                "job_id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "experience_level": job.experience_level,
                "description": job.description,
                "required_skills": job.required_skills,
                "match_score": score,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "resume_id": latest_resume.id
            })

        # Sort by highest match_score first
        recommendations.sort(key=lambda x: x["match_score"], reverse=True)
        return recommendations

    def get_history(self, db: Session, current_user: User):
        from app.models.resume import Resume
        user_resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
        resume_ids = [r.id for r in user_resumes]
        if not resume_ids:
            return []

        matches = db.query(JobMatch).filter(JobMatch.resume_id.in_(resume_ids)).all()
        history = []
        for m in matches:
            job = self.job_repository.get_by_id(db, m.job_id)
            if job:
                history.append({
                    "id": m.id,
                    "resume_id": m.resume_id,
                    "job_id": m.job_id,
                    "job_title": job.title,
                    "company": job.company,
                    "match_score": m.match_score,
                    "strengths": json.loads(m.strengths) if m.strengths else [],
                    "missing_skills": json.loads(m.missing_skills) if m.missing_skills else []
                })
        
        history.sort(key=lambda x: x["id"], reverse=True)
        return history


