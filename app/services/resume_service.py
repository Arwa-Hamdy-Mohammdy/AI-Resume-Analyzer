import os
import shutil

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.models.user import User
from app.repositories.resume_repository import ResumeRepository


class ResumeService:

    def __init__(self):
        self.resume_repository = ResumeRepository()

    def upload_resume(
        self,
        db: Session,
        file: UploadFile,
        current_user: User
    ):

        upload_dir = f"uploads/user_{current_user.id}"
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        resume = Resume(
            file_name=file.filename,
            file_path=file_path,
            extracted_text=None,
            user_id=current_user.id
        )

        return self.resume_repository.create(db, resume)