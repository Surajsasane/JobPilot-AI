from datetime import timezone
from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db import get_db
from app.dependencies import get_current_user
from app.models import Resume, User
from app.schemas import ResumeResponse
from app.services.resume_analyzer import extract_resume_text, extract_skills, match_jobs

router = APIRouter()
ALLOWED_TYPES = {".pdf": "application/pdf", ".doc": "application/msword", ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}

@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    original_name = Path(file.filename or "resume").name
    extension = Path(original_name).suffix.lower()
    if extension not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF, DOC, and DOCX files are supported")
    if file.content_type and file.content_type not in {ALLOWED_TYPES[extension], "application/octet-stream"}:
        raise HTTPException(status_code=400, detail="File content type does not match the file extension")
    max_bytes = settings.max_upload_mb * 1024 * 1024
    content = await file.read(max_bytes + 1)
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty")
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail=f"Resume must be {settings.max_upload_mb} MB or smaller")
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"user_{current_user.id}_{uuid4().hex}{extension}"
    destination = upload_dir / stored_name
    destination.write_bytes(content)
    resume = Resume(original_filename=original_name, stored_filename=stored_name, content_type=ALLOWED_TYPES[extension], size_bytes=len(content), user_id=current_user.id)
    try:
        db.add(resume)
        db.commit()
        db.refresh(resume)
    except Exception:
        db.rollback()
        destination.unlink(missing_ok=True)
        raise
    created = resume.created_at
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    return ResumeResponse(id=resume.id, original_filename=resume.original_filename, content_type=resume.content_type, size_bytes=resume.size_bytes, created_at=created.isoformat())

@router.get("/", response_model=list[ResumeResponse])
def list_resumes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.id.desc()).all()
    return [ResumeResponse(id=item.id, original_filename=item.original_filename, content_type=item.content_type, size_bytes=item.size_bytes, created_at=(item.created_at.replace(tzinfo=timezone.utc) if item.created_at.tzinfo is None else item.created_at).isoformat()) for item in items]

@router.post("/{resume_id}/analyze")
def analyze_resume(resume_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    file_path = Path(settings.upload_dir) / resume.stored_filename
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Resume file is missing from storage")
    text = extract_resume_text(file_path)
    skills = extract_skills(text)
    return {"resume_id": resume.id, "filename": resume.original_filename, "skills": skills, "skill_count": len(skills), "matched_jobs": match_jobs(skills), "note": "Keyword-based extraction from selectable PDF/DOCX text. Review results; this is not an AI assessment."}
