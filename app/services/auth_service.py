from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class AuthService:

    def __init__(self):
        self.user_repository = UserRepository()

    def register(self, db: Session, user: UserCreate):

        existing_user = self.user_repository.get_by_email(db, user.email)

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already exists"
            )

        hashed_password = hash_password(user.password)

        user.password = hashed_password

        return self.user_repository.create(db, user)

    def login(self, db: Session, email: str, password: str):

        db_user = self.user_repository.get_by_email(db, email)

        if not db_user:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        if not verify_password(password, db_user.password):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        access_token = create_access_token(
            data={"sub": db_user.email}
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }