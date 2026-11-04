from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    resumes: Mapped[list["Resume"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    job_preferences: Mapped["JobPreference | None"] = relationship(back_populates="owner", uselist=False, cascade="all, delete-orphan")
    applications: Mapped[list["Application"]] = relationship(back_populates="owner", cascade="all, delete-orphan")

class Resume(Base):
    __tablename__ = "resumes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    content_type: Mapped[str] = mapped_column(String(120), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    owner: Mapped[User] = relationship(back_populates="resumes")

class JobPreference(Base):
    __tablename__ = "job_preferences"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    target_roles: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    locations: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    skills: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    min_experience_years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_experience_years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    min_salary: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_salary: Mapped[int | None] = mapped_column(Integer, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    work_mode: Mapped[str] = mapped_column(String(20), default="any", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    owner: Mapped[User] = relationship(back_populates="job_preferences")


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("user_id", "job_url", name="uq_application_user_job_url"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(40), default="demo", nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    job_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="saved", nullable=False)
    notes: Mapped[str] = mapped_column(String(4000), default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    owner: Mapped[User] = relationship(back_populates="applications")
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
