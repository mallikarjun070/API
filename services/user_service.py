from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.user import User, UserCreate, UserUpdate, UserPasswordChange
from utils.security import get_password_hash, verify_password


class UserService:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email.lower().strip()).first()

    @classmethod
    def register(cls, db: Session, user_in: UserCreate) -> User:
        existing = cls.get_by_email(db, user_in.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists"
            )
        
        hashed_pwd = get_password_hash(user_in.password)
        db_user = User(
            email=user_in.email.lower().strip(),
            full_name=user_in.full_name.strip(),
            hashed_password=hashed_pwd,
            is_active=True
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @classmethod
    def authenticate(cls, db: Session, email: str, password: str) -> Optional[User]:
        user = cls.get_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @classmethod
    def update_profile(cls, db: Session, user: User, user_update: UserUpdate) -> User:
        if user_update.full_name is not None:
            user.full_name = user_update.full_name.strip()
        if user_update.email is not None and user_update.email != user.email:
            existing = cls.get_by_email(db, user_update.email)
            if existing and existing.id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email is already in use by another account"
                )
            user.email = user_update.email.lower().strip()
        
        db.commit()
        db.refresh(user)
        return user

    @classmethod
    def change_password(cls, db: Session, user: User, pwd_change: UserPasswordChange) -> bool:
        if not verify_password(pwd_change.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password"
            )
        
        user.hashed_password = get_password_hash(pwd_change.new_password)
        db.commit()
        return True
