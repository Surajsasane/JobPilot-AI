from datetime import timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.db import get_db
from app.dependencies import get_current_user
from app.models import Application, User
from app.schemas import ApplicationCreate, ApplicationResponse, ApplicationUpdate

router = APIRouter()
VALID_STATUSES = {"saved", "applied", "interview", "rejected", "offer"}

def serialize(item: Application) -> ApplicationResponse:
    created = item.created_at.replace(tzinfo=timezone.utc) if item.created_at.tzinfo is None else item.created_at
    updated = item.updated_at.replace(tzinfo=timezone.utc) if item.updated_at.tzinfo is None else item.updated_at
    return ApplicationResponse(
        id=item.id, source=item.source, title=item.title, company=item.company,
        location=item.location, job_url=item.job_url, status=item.status,
        notes=item.notes, created_at=created.isoformat(), updated_at=updated.isoformat()
    )

@router.get("/", response_model=list[ApplicationResponse])
def list_applications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(Application).filter(Application.user_id == current_user.id).order_by(Application.updated_at.desc()).all()
    return [serialize(item) for item in items]

@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(payload: ApplicationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(Application).filter(
        Application.user_id == current_user.id,
        Application.job_url == payload.job_url
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="This job is already in your application tracker")
    item = Application(user_id=current_user.id, **payload.model_dump())
    db.add(item)
    try:
        db.commit()
        db.refresh(item)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="This job is already in your application tracker")
    return serialize(item)

@router.patch("/{application_id}", response_model=ApplicationResponse)
def update_application(application_id: int, payload: ApplicationUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == current_user.id
    ).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Application not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(item, key, value)
    db.add(item)
    db.commit()
    db.refresh(item)
    return serialize(item)
