
import os
import shutil
import json
import re

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.agents.resume_agent import ResumeAgent
from app.models.resume import Resume
from app.models.resume_analysis import ResumeAnalysis
from app.models.user import User
from app.repositories.resume_analysis_repository import ResumeAnalysisRepository
from app.repositories.resume_repository import ResumeRepository
from app.utils.resume_parser import extract_text


class ResumeService:

    def __init__(self):
        self.resume_repository = ResumeRepository()
        self.analysis_repository = ResumeAnalysisRepository()
        self.resume_agent = ResumeAgent()

    def upload_resume(
        self,
        db: Session,
        file: UploadFile,
        current_user: User
    ):

        # Save file
        upload_dir = f"uploads/user_{current_user.id}"
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract text
        extracted_text = extract_text(file_path)

        # AI Analysis
        analysis = self.resume_agent.analyze_resume(extracted_text)

        print("=" * 50)
        print("AI ANALYSIS")
        print("=" * 50)
        print(analysis)
        print("=" * 50)

        # Save Resume
        resume = Resume(
            file_name=file.filename,
            file_path=file_path,
            extracted_text=extracted_text,
            user_id=current_user.id
        )

        resume = self.resume_repository.create(db, resume)

        # -----------------------------
        # Clean AI Response
        # -----------------------------

        analysis = analysis.strip()

        analysis = analysis.replace("```json", "")
        analysis = analysis.replace("```", "")

        match = re.search(r"\{.*\}", analysis, re.DOTALL)

        if not match:
            print("=" * 50)
            print("AI DID NOT RETURN JSON")
            print("=" * 50)
            print(analysis)

            raise HTTPException(
                status_code=500,
                detail="AI did not return valid JSON."
            )

        json_text = match.group()

        print("=" * 50)
        print("JSON ONLY")
        print("=" * 50)
        print(json_text)
        print("=" * 50)

        try:
            analysis_json = json.loads(json_text)

        except Exception as e:

            print("=" * 50)
            print("INVALID JSON")
            print("=" * 50)
            print(e)
            print(json_text)

            raise HTTPException(
                status_code=500,
                detail="Invalid AI JSON."
            )

        # Save Analysis
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

        resume_analysis = ResumeAnalysis(
            resume_id=resume.id,
            summary=analysis_json.get("summary", ""),
            skills=json.dumps(combined_skills),
            technical_skills=json.dumps(tech_skills),
            soft_skills=json.dumps(soft_sk),
            education=json.dumps(
                analysis_json.get("education", [])
            ),
            experience=json.dumps(
                analysis_json.get("experience", [])
            ),
            strengths=json.dumps(analysis_json.get("strengths", [])),
            weaknesses=json.dumps(analysis_json.get("weaknesses", [])),
            overall_score=score_val
        )

        self.analysis_repository.create(
            db,
            resume_analysis
        )

        return resume

    def get_analysis(
        self,
        db: Session,
        resume_id: int
    ):

        analysis = self.analysis_repository.get_by_resume_id(
            db,
            resume_id
        )

        if not analysis:
            raise HTTPException(
                status_code=404,
                detail="Analysis not found"
            )

        return analysis

    def get_latest_analysis(
        self,
        db: Session,
        user_id: int
    ):
        latest_resume = self.resume_repository.get_latest_by_user(db, user_id)

        if not latest_resume:
            raise HTTPException(
                status_code=404,
                detail="No resumes uploaded yet."
            )

        analysis = self.analysis_repository.get_by_resume_id(
            db,
            latest_resume.id
        )

        if not analysis:
            raise HTTPException(
                status_code=404,
                detail="Analysis not found for latest resume."
            )

        return analysis

    def update_skills(
        self,
        db: Session,
        resume_id: int,
        technical_skills: list[str],
        soft_skills: list[str],
        current_user: User
    ):
        resume = self.resume_repository.get_by_id(db, resume_id)
        if not resume or resume.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Resume not found or access denied.")

        analysis = self.analysis_repository.get_by_resume_id(db, resume_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found.")

        combined = list(dict.fromkeys(technical_skills + soft_skills))
        analysis.technical_skills = json.dumps(technical_skills)
        analysis.soft_skills = json.dumps(soft_skills)
        analysis.skills = json.dumps(combined)

        db.commit()
        db.refresh(analysis)
        return analysis