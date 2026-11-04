from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.dependencies import get_current_user
from app.models import JobPreference, User
from app.schemas import JobPreferenceResponse, JobPreferenceUpdate, UserProfileUpdate, UserResponse

router = APIRouter()

@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch("/profile", response_model=UserResponse)
def update_profile(payload: UserProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.full_name = payload.full_name.strip()
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/preferences", response_model=JobPreferenceResponse)
def get_preferences(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    preference = db.query(JobPreference).filter(JobPreference.user_id == current_user.id).first()
    if preference is None:
        return JobPreferenceResponse()
    return preference

@router.put("/preferences", response_model=JobPreferenceResponse)
def save_preferences(payload: JobPreferenceUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    preference = db.query(JobPreference).filter(JobPreference.user_id == current_user.id).first()
    values = payload.model_dump()
    if preference is None:
        preference = JobPreference(user_id=current_user.id, **values)
    else:
        for key, value in values.items():
            setattr(preference, key, value)
    db.add(preference)
    db.commit()
    db.refresh(preference)
    return preference
