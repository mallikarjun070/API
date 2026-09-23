from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from database.db import get_db
from models.user import User
from models.resume import (
    ResumeCreate,
    ResumeUpdate,
    ResumeResponse,
    ResumeDetailResponse,
    AISummaryRequest,
    AIBulletEnhanceRequest,
    ATSAnalysisRequest,
    ATSAnalysisResponse,
)
from services.resume_service import ResumeService
from services.ai_service import AIService
from utils.security import get_current_active_user
from utils.helpers import format_resume_text, generate_resume_pdf

router = APIRouter(prefix="/api/resumes", tags=["Resumes & AI"])


@router.post("", response_model=ResumeDetailResponse, status_code=status.HTTP_201_CREATED)
def create_resume(
    resume_in: ResumeCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new resume."""
    return ResumeService.create(db, current_user.id, resume_in)


@router.get("", response_model=List[ResumeResponse])
def list_resumes(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all resumes belonging to the authenticated user."""
    return ResumeService.list_by_user(db, current_user.id)


@router.get("/{resume_id}", response_model=ResumeDetailResponse)
def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get full details of a specific resume."""
    resume = ResumeService.get_by_id(db, resume_id, current_user.id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    return resume


@router.put("/{resume_id}", response_model=ResumeDetailResponse)
def update_resume(
    resume_id: int,
    resume_in: ResumeUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an existing resume."""
    return ResumeService.update(db, resume_id, current_user.id, resume_in)


@router.delete("/{resume_id}")
def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a resume."""
    ResumeService.delete(db, resume_id, current_user.id)
    return {"success": True, "message": "Resume deleted successfully"}


# ---------------- AI Enhancements & Generation ---------------- #

@router.post("/ai/generate-summary")
def generate_summary(
    request: AISummaryRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Generate professional AI summary options based on role, experience level, and skills."""
    return AIService.generate_summary(
        target_role=request.target_role,
        experience_level=request.experience_level or "Mid-Level",
        key_skills=request.key_skills or [],
        existing_summary=request.existing_summary or ""
    )


@router.post("/ai/enhance-bullet")
def enhance_bullet(
    request: AIBulletEnhanceRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Enhance bullet points into high-impact STAR / XYZ format with action verbs and metrics."""
    return AIService.enhance_bullet(
        bullet_point=request.bullet_point,
        target_role=request.target_role,
        action_verb_preference=request.action_verb_preference or "High Impact"
    )


@router.post("/ai/ats-analysis", response_model=ATSAnalysisResponse)
def ats_analysis(
    request: ATSAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Run comprehensive ATS scan and keyword optimization against a job description."""
    resume_dict = {}
    if request.resume_id:
        resume = ResumeService.get_by_id(db, request.resume_id, current_user.id)
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        resume_dict = {
            "title": resume.title,
            "target_role": resume.target_role,
            "personal_info": resume.personal_info,
            "summary": resume.summary,
            "experiences": resume.experiences,
            "educations": resume.educations,
            "skills": resume.skills,
            "projects": resume.projects,
            "certifications": resume.certifications
        }
    elif request.resume_data:
        resume_dict = request.resume_data.model_dump()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either resume_id or resume_data must be provided"
        )

    resume_text = format_resume_text(resume_dict)
    analysis = AIService.analyze_ats(
        resume_text=resume_text,
        job_description=request.job_description
    )

    # Save to database if resume_id is provided
    if request.resume_id:
        ResumeService.save_ats_feedback(
            db=db,
            resume_id=request.resume_id,
            user_id=current_user.id,
            score=analysis.get("ats_score", 0.0),
            feedback=analysis
        )

    return analysis


@router.get("/{resume_id}/export/pdf")
def export_pdf(
    resume_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate and export the resume as a formatted PDF."""
    resume = ResumeService.get_by_id(db, resume_id, current_user.id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    resume_dict = {
        "title": resume.title,
        "target_role": resume.target_role,
        "personal_info": resume.personal_info,
        "summary": resume.summary,
        "experiences": resume.experiences,
        "educations": resume.educations,
        "skills": resume.skills,
        "projects": resume.projects,
        "certifications": resume.certifications
    }

    pdf_buffer = generate_resume_pdf(resume_dict)
    filename = f"{resume.title.replace(' ', '_')}_Resume.pdf"

    return Response(
        content=pdf_buffer.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
