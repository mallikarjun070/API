import io
from typing import Any, Dict, Optional
from fastapi.responses import JSONResponse


def api_response(
    success: bool = True,
    message: str = "",
    data: Optional[Any] = None,
    status_code: int = 200,
    errors: Optional[Any] = None
) -> JSONResponse:
    """Standardized JSON response envelope."""
    payload = {
        "success": success,
        "message": message,
        "data": data,
        "errors": errors
    }
    return JSONResponse(content=payload, status_code=status_code)


def format_resume_text(resume_dict: Dict[str, Any]) -> str:
    """Convert a structured resume dictionary into clean plain text for AI analysis."""
    lines = []
    
    # Personal Info
    pinfo = resume_dict.get("personal_info") or {}
    name = pinfo.get("full_name") or ""
    role = pinfo.get("job_title") or resume_dict.get("target_role") or ""
    contact = " | ".join(filter(None, [
        pinfo.get("email"),
        pinfo.get("phone"),
        pinfo.get("location"),
        pinfo.get("linkedin"),
        pinfo.get("github")
    ]))
    
    if name:
        lines.append(f"NAME: {name}")
    if role:
        lines.append(f"TARGET ROLE: {role}")
    if contact:
        lines.append(f"CONTACT: {contact}")
    
    # Summary
    summary = resume_dict.get("summary")
    if summary:
        lines.append("\nPROFESSIONAL SUMMARY:")
        lines.append(summary)
    
    # Experiences
    experiences = resume_dict.get("experiences") or []
    if experiences:
        lines.append("\nWORK EXPERIENCE:")
        for exp in experiences:
            pos = exp.get("position", "")
            comp = exp.get("company", "")
            start = exp.get("start_date", "")
            end = exp.get("end_date", "Present" if exp.get("is_current") else "")
            lines.append(f"- {pos} at {comp} ({start} - {end})")
            bullets = exp.get("bullets") or []
            for b in bullets:
                lines.append(f"  * {b}")
    
    # Skills
    skills = resume_dict.get("skills") or []
    if skills:
        lines.append("\nSKILLS:")
        for sk in skills:
            cat = sk.get("category", "General")
            items = ", ".join(sk.get("items", []))
            lines.append(f"- {cat}: {items}")
    
    # Education
    educations = resume_dict.get("educations") or []
    if educations:
        lines.append("\nEDUCATION:")
        for edu in educations:
            deg = edu.get("degree", "")
            field = edu.get("field_of_study", "")
            inst = edu.get("institution", "")
            start = edu.get("start_date", "")
            end = edu.get("end_date", "")
            lines.append(f"- {deg} in {field}, {inst} ({start} - {end})")
            if edu.get("details"):
                lines.append(f"  * {edu.get('details')}")

    # Projects
    projects = resume_dict.get("projects") or []
    if projects:
        lines.append("\nPROJECTS:")
        for proj in projects:
            title = proj.get("title", "")
            tech = proj.get("tech_stack", "")
            lines.append(f"- {title} (Tech: {tech})")
            desc = proj.get("description", "")
            if desc:
                lines.append(f"  {desc}")
            for b in proj.get("bullets", []):
                lines.append(f"  * {b}")

    # Certifications
    certifications = resume_dict.get("certifications") or []
    if certifications:
        lines.append("\nCERTIFICATIONS:")
        for cert in certifications:
            cname = cert.get("name", "")
            iss = cert.get("issuer", "")
            dt = cert.get("date", "")
            lines.append(f"- {cname} by {iss} ({dt})")

    return "\n".join(lines)


def generate_resume_pdf(resume_data: Dict[str, Any]) -> io.BytesIO:
    """Generate a clean PDF document for a resume in-memory."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#1A202C")
        )
        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#4A5568")
        )
        section_heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#2B6CB0"),
            spaceAfter=4,
            spaceBefore=10
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#2D3748")
        )
        bullet_style = ParagraphStyle(
            "Bullet",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            leftIndent=15,
            textColor=colors.HexColor("#2D3748")
        )

        story = []
        pinfo = resume_data.get("personal_info") or {}

        # Header
        name = pinfo.get("full_name") or resume_data.get("title", "Resume")
        story.append(Paragraph(name, title_style))
        
        role = pinfo.get("job_title") or resume_data.get("target_role")
        if role:
            story.append(Paragraph(role, subtitle_style))
        
        contacts = list(filter(None, [
            pinfo.get("email"),
            pinfo.get("phone"),
            pinfo.get("location"),
            pinfo.get("linkedin"),
            pinfo.get("github")
        ]))
        if contacts:
            story.append(Paragraph(" • ".join(contacts), subtitle_style))

        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E0"), spaceAfter=10))

        # Summary
        summary = resume_data.get("summary")
        if summary:
            story.append(Paragraph("PROFESSIONAL SUMMARY", section_heading))
            story.append(Paragraph(summary, body_style))
            story.append(Spacer(1, 6))

        # Experience
        experiences = resume_data.get("experiences") or []
        if experiences:
            story.append(Paragraph("WORK EXPERIENCE", section_heading))
            for exp in experiences:
                pos = exp.get("position", "")
                comp = exp.get("company", "")
                start = exp.get("start_date", "")
                end = exp.get("end_date", "Present" if exp.get("is_current") else "")
                loc = exp.get("location", "")
                
                header_line = f"<b>{pos}</b> — {comp}"
                date_line = f"<font color='#718096'>{start} - {end} {f'| {loc}' if loc else ''}</font>"
                story.append(Paragraph(f"{header_line} &nbsp;&nbsp; {date_line}", body_style))
                
                for b in exp.get("bullets", []):
                    story.append(Paragraph(f"• {b}", bullet_style))
                story.append(Spacer(1, 4))

        # Skills
        skills = resume_data.get("skills") or []
        if skills:
            story.append(Paragraph("SKILLS", section_heading))
            for sk in skills:
                cat = sk.get("category", "General")
                items = ", ".join(sk.get("items", []))
                story.append(Paragraph(f"<b>{cat}:</b> {items}", body_style))
            story.append(Spacer(1, 6))

        # Education
        educations = resume_data.get("educations") or []
        if educations:
            story.append(Paragraph("EDUCATION", section_heading))
            for edu in educations:
                deg = edu.get("degree", "")
                field = edu.get("field_of_study", "")
                inst = edu.get("institution", "")
                start = edu.get("start_date", "")
                end = edu.get("end_date", "")
                edu_text = f"<b>{deg} in {field}</b> — {inst} ({start} - {end})" if field else f"<b>{deg}</b> — {inst} ({start} - {end})"
                story.append(Paragraph(edu_text, body_style))
                if edu.get("details"):
                    story.append(Paragraph(f"• {edu.get('details')}", bullet_style))
            story.append(Spacer(1, 6))

        # Projects
        projects = resume_data.get("projects") or []
        if projects:
            story.append(Paragraph("PROJECTS", section_heading))
            for proj in projects:
                title = proj.get("title", "")
                tech = proj.get("tech_stack", "")
                story.append(Paragraph(f"<b>{title}</b> {f'({tech})' if tech else ''}", body_style))
                if proj.get("description"):
                    story.append(Paragraph(proj.get("description"), body_style))
                for b in proj.get("bullets", []):
                    story.append(Paragraph(f"• {b}", bullet_style))
            story.append(Spacer(1, 6))

        # Certifications
        certifications = resume_data.get("certifications") or []
        if certifications:
            story.append(Paragraph("CERTIFICATIONS", section_heading))
            for cert in certifications:
                cname = cert.get("name", "")
                iss = cert.get("issuer", "")
                dt = cert.get("date", "")
                story.append(Paragraph(f"• <b>{cname}</b> — {iss} ({dt})", body_style))

        doc.build(story)
        buffer.seek(0)
        return buffer
    except Exception as e:
        # Fallback simple text buffer if reportlab fails
        buffer = io.BytesIO()
        text_content = format_resume_text(resume_data)
        buffer.write(text_content.encode("utf-8"))
        buffer.seek(0)
        return buffer
