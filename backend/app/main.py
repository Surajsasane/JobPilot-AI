from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from app.core.config import settings
from app.job_catalog import DEMO_JOBS
from app.routers import auth, resumes, profile, applications

app = FastAPI(title=settings.app_name, version="0.3.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router, prefix=f"{settings.api_prefix}/auth", tags=["Authentication"])
app.include_router(resumes.router, prefix=f"{settings.api_prefix}/resumes", tags=["Resumes"])
app.include_router(profile.router, prefix=f"{settings.api_prefix}", tags=["User Profile & Preferences"])
app.include_router(applications.router, prefix=f"{settings.api_prefix}/applications", tags=["Application Tracker"])

class JobSearch(BaseModel):
    keywords: list[str] = Field(default_factory=list)
    location: str | None = None
    remote_only: bool = True

@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name, "environment": settings.environment}

@app.get(f"{settings.api_prefix}/jobs")
def list_demo_jobs():
    return {"items": DEMO_JOBS, "count": len(DEMO_JOBS), "note": "Demo data only; connect permitted job sources for live listings."}

@app.post(f"{settings.api_prefix}/jobs/match")
def match_demo_jobs(search: JobSearch):
    terms = [term.lower() for term in search.keywords]
    ranked = []
    for job in DEMO_JOBS:
        haystack = f"{job['title']} {job['description']} {job['location']}".lower()
        score = sum(1 for term in terms if term in haystack)
        ranked.append({**job, "match_score": round(score / max(len(terms), 1) * 100) if terms else 0})
    ranked.sort(key=lambda item: item["match_score"], reverse=True)
    return {"items": ranked}
