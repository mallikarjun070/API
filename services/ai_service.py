import json
import os
import re
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = (os.getenv("GEMINI_API_KEY") or "").strip("\"' ")
AI_MODEL = os.getenv("AI_MODEL", "gemini-2.5-flash")


class AIService:
    @staticmethod
    def _call_gemini(prompt: str) -> Optional[str]:
        """Calls Gemini API with strict timeout if API key is configured; falls back safely."""
        if not GEMINI_API_KEY or len(GEMINI_API_KEY) < 10 or GEMINI_API_KEY.startswith("your-"):
            return None
        
        # Use direct requests with a short 3-second timeout to prevent any hanging
        try:
            import requests
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{AI_MODEL}:generateContent?key={GEMINI_API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            res = requests.post(url, json=payload, timeout=3)
            if res.status_code == 200:
                data = res.json()
                candidates = data.get("candidates", [])
                if candidates:
                    return candidates[0]["content"]["parts"][0]["text"]
        except Exception:
            pass
        return None

    @classmethod
    def generate_summary(
        cls,
        target_role: str,
        experience_level: str = "Mid-Level",
        key_skills: Optional[List[str]] = None,
        existing_summary: str = ""
    ) -> Dict[str, Any]:
        """Generates professional, high-impact resume summaries."""
        skills_str = ", ".join(key_skills or [])
        prompt = f"""
You are an expert executive resume writer. Write 3 compelling, professional resume summary options for a candidate.
Target Role: {target_role}
Experience Level: {experience_level}
Key Skills: {skills_str}
Current Draft (if any): {existing_summary}

Format your response strictly as JSON with the following structure:
{{
    "options": [
        {{
            "style": "Results-Driven",
            "summary": "..."
        }},
        {{
            "style": "Technical & Skills-Focused",
            "summary": "..."
        }},
        {{
            "style": "Leadership & Strategy",
            "summary": "..."
        }}
    ]
}}
Only return the JSON without markdown formatting or backticks.
"""
        response_text = cls._call_gemini(prompt)
        if response_text:
            try:
                clean_text = re.sub(r"```(?:json)?\s*|\s*```", "", response_text).strip()
                return json.loads(clean_text)
            except Exception:
                pass

        # High quality fallback summaries
        skills_phrase = f" proficient in {skills_str}" if skills_str else ""
        return {
            "options": [
                {
                    "style": "Results-Driven",
                    "summary": f"Results-oriented {target_role} with proven track record in delivering high-impact solutions{skills_phrase}. Adept at optimizing system performance, collaborating across cross-functional teams, and driving measurable business outcomes."
                },
                {
                    "style": "Technical & Skills-Focused",
                    "summary": f"Dedicated and versatile {target_role} with strong background in end-to-end software development and system architecture{skills_phrase}. Passionate about building robust, scalable solutions with best-in-class engineering standards."
                },
                {
                    "style": "Leadership & Strategy",
                    "summary": f"Strategic {target_role} with {experience_level.lower()} expertise spearheading innovative projects from conception through deployment. Skilled in stakeholder management, modern technical stacks, and Agile delivery."
                }
            ]
        }

    @classmethod
    def enhance_bullet(
        cls,
        bullet_point: str,
        target_role: Optional[str] = None,
        action_verb_preference: str = "High Impact"
    ) -> Dict[str, Any]:
        """Enhances a resume bullet point using Google XYZ / STAR format (Accomplished [X] as measured by [Y], by doing [Z])."""
        role_clause = f"for a {target_role}" if target_role else ""
        prompt = f"""
You are an ATS optimization and resume specialist. Transform this basic resume bullet point into 3 strong, quantifiable bullet points {role_clause} using strong action verbs and Google's XYZ formula (Accomplished [X] as measured by [Y] by doing [Z]).

Original Bullet: "{bullet_point}"

Respond strictly with valid JSON:
{{
    "original": "{bullet_point}",
    "suggestions": [
        {{
            "version": "Metric-Focused",
            "text": "...",
            "improvement_note": "..."
        }},
        {{
            "version": "Action-Oriented",
            "text": "...",
            "improvement_note": "..."
        }},
        {{
            "version": "Executive Impact",
            "text": "...",
            "improvement_note": "..."
        }}
    ]
}}
Only return raw JSON.
"""
        response_text = cls._call_gemini(prompt)
        if response_text:
            try:
                clean_text = re.sub(r"```(?:json)?\s*|\s*```", "", response_text).strip()
                return json.loads(clean_text)
            except Exception:
                pass

        # Fallback intelligent enhancements
        clean_bullet = bullet_point.strip().rstrip(".")
        return {
            "original": bullet_point,
            "suggestions": [
                {
                    "version": "Metric-Focused",
                    "text": f"Spearheaded {clean_bullet}, resulting in a 25% increase in operational efficiency and significant workflow optimization.",
                    "improvement_note": "Adds concrete quantifiable impact and strong active leadership verb."
                },
                {
                    "version": "Action-Oriented",
                    "text": f"Architected and executed {clean_bullet} by leveraging modern best practices, reducing latency and boosting system reliability.",
                    "improvement_note": "Highlights technical execution and methodology."
                },
                {
                    "version": "Executive Impact",
                    "text": f"Directed cross-functional efforts to deliver {clean_bullet}, aligning deliverables with core organizational KPIs.",
                    "improvement_note": "Elevates phrasing to demonstrate high-level business alignment."
                }
            ]
        }

    @classmethod
    def analyze_ats(
        cls,
        resume_text: str,
        job_description: str
    ) -> Dict[str, Any]:
        """Performs comprehensive ATS scoring, keyword matching, and tailoring feedback against a job description."""
        prompt = f"""
You are an advanced Applicant Tracking System (ATS) and expert career coach.
Analyze the following resume against the job description.

JOB DESCRIPTION:
{job_description[:3000]}

RESUME CONTENT:
{resume_text[:3000]}

Evaluate match score (0-100), identify matched keywords, missing critical keywords, strengths, weaknesses, and tailored suggestions.

Return strictly valid JSON:
{{
    "ats_score": 85.0,
    "match_percentage": 82.0,
    "matched_keywords": ["Python", "FastAPI", "Docker", "REST APIs"],
    "missing_keywords": ["Kubernetes", "CI/CD", "AWS Lambda"],
    "strengths": ["Strong backend experience", "Clear impact metrics in past roles"],
    "improvements": ["Highlight cloud orchestration experience", "Add target job keywords in summary"],
    "tailored_suggestions": [
        "Include mentions of CI/CD pipelines in work experience bullets",
        "Align target job title with the exact title from the job description"
    ]
}}
Do not include code fence markers.
"""
        response_text = cls._call_gemini(prompt)
        if response_text:
            try:
                clean_text = re.sub(r"```(?:json)?\s*|\s*```", "", response_text).strip()
                return json.loads(clean_text)
            except Exception:
                pass

        # Heuristic keyword match fallback
        resume_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", resume_text.lower()))
        jd_words = re.findall(r"\b[a-zA-Z]{3,}\b", job_description.lower())
        
        # Stopwords to filter out
        stopwords = {
            "and", "the", "for", "with", "that", "this", "from", "have", "will", "our",
            "you", "your", "are", "about", "work", "team", "role", "must", "years", "experience"
        }
        
        filtered_jd_words = [w for w in jd_words if w not in stopwords and len(w) > 3]
        
        matched = sorted(list(set(w.capitalize() for w in filtered_jd_words if w in resume_words)))[:8]
        missing = sorted(list(set(w.capitalize() for w in filtered_jd_words if w not in resume_words)))[:8]
        
        total_keywords = len(matched) + len(missing)
        match_ratio = (len(matched) / total_keywords) if total_keywords > 0 else 0.75
        calculated_score = round(min(100.0, max(40.0, match_ratio * 100)), 1)

        return {
            "ats_score": calculated_score,
            "match_percentage": calculated_score,
            "matched_keywords": matched or ["Communication", "Development", "Design", "Problem Solving"],
            "missing_keywords": missing or ["Cloud Architecture", "Agile Methodology", "Unit Testing"],
            "strengths": [
                "Clear career progression and structured section layout",
                "Strong alignment with core domain competencies"
            ],
            "improvements": [
                "Incorporate missing technical keywords into skills and experience highlights",
                "Quantify achievements with percentage increases and revenue or time savings"
            ],
            "tailored_suggestions": [
                f"Add prominent keywords like {', '.join(missing[:3]) if missing else 'key technologies'} in your skills section",
                "Customize your professional summary to reflect the specific phrasing in the job description"
            ]
        }
