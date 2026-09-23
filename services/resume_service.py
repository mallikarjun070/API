from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.resume import Resume, ResumeCreate, ResumeUpdate


class ResumeService:
    @staticmethod
    def get_by_id(db: Session, resume_id: int, user_id: int) -> Optional[Resume]:
        return db.query(Resume).filter(
            Resume.id == resume_id,
            Resume.user_id == user_id
        ).first()

    @staticmethod
    def list_by_user(db: Session, user_id: int) -> List[Resume]:
        return db.query(Resume).filter(Resume.user_id == user_id).order_by(Resume.updated_at.desc()).all()

    @classmethod
    def create(cls, db: Session, user_id: int, resume_in: ResumeCreate) -> Resume:
        resume_data = resume_in.model_dump()
        
        # Convert sub-models to dictionaries for JSON column storage
        db_resume = Resume(
            user_id=user_id,
            title=resume_data.get("title", "Untitled Resume"),
            target_role=resume_data.get("target_role"),
            template_id=resume_data.get("template_id", "modern"),
            personal_info=resume_data.get("personal_info") or {},
            summary=resume_data.get("summary") or "",
            experiences=resume_data.get("experiences") or [],
            educations=resume_data.get("educations") or [],
            skills=resume_data.get("skills") or [],
            projects=resume_data.get("projects") or [],
            certifications=resume_data.get("certifications") or [],
            custom_sections=resume_data.get("custom_sections") or []
        )
        db.add(db_resume)
        db.commit()
        db.refresh(db_resume)
        return db_resume

    @classmethod
    def update(cls, db: Session, resume_id: int, user_id: int, resume_in: ResumeUpdate) -> Resume:
        resume = cls.get_by_id(db, resume_id, user_id)
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )

        update_data = resume_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(resume, field, value)

        db.commit()
        db.refresh(resume)
        return resume

    @classmethod
    def delete(cls, db: Session, resume_id: int, user_id: int) -> bool:
        resume = cls.get_by_id(db, resume_id, user_id)
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        db.delete(resume)
        db.commit()
        return True

    @classmethod
    def save_ats_feedback(
        cls,
        db: Session,
        resume_id: int,
        user_id: int,
        score: float,
        feedback: Dict[str, Any]
    ) -> Resume:
        resume = cls.get_by_id(db, resume_id, user_id)
        if resume:
            resume.ats_score = score
            resume.ats_feedback = feedback
            db.commit()
            db.refresh(resume)
        return resume
