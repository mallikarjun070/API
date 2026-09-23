from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from database.db import Base


# SQLAlchemy ORM Model
class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False, default="Untitled Resume")
    target_role = Column(String(255), nullable=True)
    template_id = Column(String(50), default="modern", nullable=False)
    
    # Structured resume data (stored as JSON)
    personal_info = Column(JSON, default=dict, nullable=False)
    summary = Column(Text, nullable=True)
    experiences = Column(JSON, default=list, nullable=False)
    educations = Column(JSON, default=list, nullable=False)
    skills = Column(JSON, default=list, nullable=False)
    projects = Column(JSON, default=list, nullable=False)
    certifications = Column(JSON, default=list, nullable=False)
    custom_sections = Column(JSON, default=list, nullable=False)
    
    # ATS Scoring Data
    ats_score = Column(Float, nullable=True)
    ats_feedback = Column(JSON, default=dict, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="resumes")


# Pydantic Schemas
class PersonalInfo(BaseModel):
    full_name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: Optional[str] = ""
    github: Optional[str] = ""
    portfolio: Optional[str] = ""
    job_title: Optional[str] = ""


class ExperienceItem(BaseModel):
    id: Optional[str] = None
    company: str
    position: str
    location: Optional[str] = ""
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""
    is_current: bool = False
    bullets: List[str] = []


class EducationItem(BaseModel):
    id: Optional[str] = None
    institution: str
    degree: str
    field_of_study: Optional[str] = ""
    start_date: Optional[str] = ""
    end_date: Optional[str] = ""
    grade: Optional[str] = ""
    details: Optional[str] = ""


class SkillItem(BaseModel):
    category: Optional[str] = "General"
    items: List[str] = []


class ProjectItem(BaseModel):
    id: Optional[str] = None
    title: str
    link: Optional[str] = ""
    tech_stack: Optional[str] = ""
    description: Optional[str] = ""
    bullets: List[str] = []


class CertificationItem(BaseModel):
    id: Optional[str] = None
    name: str
    issuer: str
    date: Optional[str] = ""
    url: Optional[str] = ""


class CustomSectionItem(BaseModel):
    id: Optional[str] = None
    title: str
    content: str


class ResumeBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    target_role: Optional[str] = None
    template_id: Optional[str] = "modern"
    personal_info: Optional[PersonalInfo] = PersonalInfo()
    summary: Optional[str] = ""
    experiences: Optional[List[ExperienceItem]] = []
    educations: Optional[List[EducationItem]] = []
    skills: Optional[List[SkillItem]] = []
    projects: Optional[List[ProjectItem]] = []
    certifications: Optional[List[CertificationItem]] = []
    custom_sections: Optional[List[CustomSectionItem]] = []


class ResumeCreate(ResumeBase):
    pass


class ResumeUpdate(BaseModel):
    title: Optional[str] = None
    target_role: Optional[str] = None
    template_id: Optional[str] = None
    personal_info: Optional[PersonalInfo] = None
    summary: Optional[str] = None
    experiences: Optional[List[ExperienceItem]] = None
    educations: Optional[List[EducationItem]] = None
    skills: Optional[List[SkillItem]] = None
    projects: Optional[List[ProjectItem]] = None
    certifications: Optional[List[CertificationItem]] = None
    custom_sections: Optional[List[CustomSectionItem]] = None


class ResumeResponse(BaseModel):
    id: int
    user_id: int
    title: str
    target_role: Optional[str]
    template_id: str
    ats_score: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResumeDetailResponse(ResumeBase):
    id: int
    user_id: int
    ats_score: Optional[float] = None
    ats_feedback: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# AI Request / Response Models
class AISummaryRequest(BaseModel):
    target_role: str
    experience_level: Optional[str] = "Mid-Level"
    key_skills: Optional[List[str]] = []
    existing_summary: Optional[str] = ""


class AIBulletEnhanceRequest(BaseModel):
    bullet_point: str
    target_role: Optional[str] = None
    action_verb_preference: Optional[str] = "High Impact"


class ATSAnalysisRequest(BaseModel):
    job_description: str
    resume_id: Optional[int] = None
    resume_data: Optional[ResumeBase] = None


class ATSAnalysisResponse(BaseModel):
    ats_score: float
    match_percentage: float
    matched_keywords: List[str]
    missing_keywords: List[str]
    strengths: List[str]
    improvements: List[str]
    tailored_suggestions: List[str]
