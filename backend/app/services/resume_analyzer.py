import re
from pathlib import Path
from docx import Document
from pypdf import PdfReader
from fastapi import HTTPException
from app.job_catalog import DEMO_JOBS

SKILLS = [
    "python", "sql", "mysql", "postgresql", "mongodb", "pandas", "numpy", "excel",
    "power bi", "tableau", "selenium", "playwright", "api testing", "rest api",
    "fastapi", "django", "flask", "javascript", "react", "html", "css", "git",
    "docker", "aws", "azure", "machine learning", "data analysis", "data visualization",
    "web scraping", "beautifulsoup", "scrapy", "pytest", "linux", "etl", "pytorch",
    "tensorflow", "java", "c++", "communication", "project management"
]

def extract_resume_text(file_path: Path) -> str:
    extension = file_path.suffix.lower()
    try:
        if extension == ".pdf":
            reader = PdfReader(str(file_path))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        elif extension == ".docx":
            document = Document(str(file_path))
            text = "\n".join(paragraph.text for paragraph in document.paragraphs)
            for table in document.tables:
                for row in table.rows:
                    text += "\n" + " ".join(cell.text for cell in row.cells)
        else:
            raise HTTPException(status_code=400, detail="Skill extraction supports PDF and DOCX. Please convert old .doc files to PDF or DOCX.")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=422, detail="Could not read this resume. It may be scanned, password-protected, or corrupted.")
    if not text.strip():
        raise HTTPException(status_code=422, detail="No selectable text found. This may be a scanned image PDF; OCR support is not included yet.")
    return text[:100000]

def extract_skills(text: str) -> list[str]:
    normalized = re.sub(r"[^a-z0-9+#. ]", " ", text.lower())
    found = []
    for skill in SKILLS:
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, normalized):
            found.append(skill)
    return found

def match_jobs(skills: list[str]) -> list[dict]:
    skill_set = set(skills)
    ranked = []
    for job in DEMO_JOBS:
        description = (job["title"] + " " + job["description"]).lower()
        matched = [skill for skill in skills if re.search(r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])", description)]
        score = round(len(matched) / max(len(skill_set), 1) * 100)
        ranked.append({**job, "match_score": score, "matched_skills": matched})
    return sorted(ranked, key=lambda item: item["match_score"], reverse=True)
