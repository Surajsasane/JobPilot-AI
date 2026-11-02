# JobPilot AI

A job-search assistant for organizing job preferences, discovering opportunities from permitted sources, matching roles, and preparing applications for user review.

## Current MVP features

- User registration and login (JWT access tokens)
- Argon2 password hashing
- User profile endpoint
- Private resume upload (PDF, DOC, DOCX; 5 MB default limit)
- Resume list scoped to the signed-in user
- PDF/DOCX text extraction and keyword-based skill detection
- Resume-to-demo-job matching with match scores
- SQLAlchemy database models; SQLite local setup and PostgreSQL support
- React dashboard for account creation, login, resume upload, skill analysis, and job matches

**Important limitations:** Job listings are sample/demo data, not live vacancies. Resume skill extraction currently works with selectable-text PDF and DOCX files. Scanned-image PDFs need OCR, and legacy .doc files must be converted to PDF or DOCX for analysis. The matching logic is keyword-based, not an AI model.

**Safety:** Job-source integrations must use official APIs, feeds, or sources whose terms permit the intended access. This starter does not bypass CAPTCHAs, login controls, or anti-bot systems, and it does not automatically submit applications.

## Run locally on Windows

### 1. Backend

Open CMD in the project folder:

```bat
cd backend
python -m venv .venv
.venv\Scripts\activate
copy .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend: http://127.0.0.1:8000  
API documentation: http://127.0.0.1:8000/docs

The backend creates a local SQLite database named `jobpilot.db`. Uploaded resumes are stored in `backend/uploads`.

### 2. Frontend

Open a second CMD window in the project folder:

```bat
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

Register, sign in, upload a PDF or DOCX resume, then click **Analyze & match jobs** beside the uploaded resume.

## API endpoints

- `GET /health` — backend health check
- `POST /api/v1/auth/register` — create account
- `POST /api/v1/auth/login` — sign in and receive JWT
- `GET /api/v1/auth/me` — current user (Bearer token required)
- `POST /api/v1/resumes/upload` — upload resume (Bearer token required)
- `GET /api/v1/resumes/` — list your resumes (Bearer token required)
- `POST /api/v1/resumes/{resume_id}/analyze` — extract skills and rank demo jobs (Bearer token required)
- `GET /api/v1/jobs` — demo jobs
- `POST /api/v1/jobs/match` — keyword match against demo jobs

## PostgreSQL

For local SQLite, keep the example `DATABASE_URL`. To use PostgreSQL, set a SQLAlchemy URL in `backend/.env`:

```env
DATABASE_URL=postgresql+psycopg://USERNAME:PASSWORD@localhost:5432/jobpilot
```

Start the included database services with `docker compose up -d` if Docker is installed.

## Security before production

- Replace `SECRET_KEY` with a long random secret and keep it private.
- Never commit `.env`, passwords, API keys, OAuth tokens, or production secrets.
- Use HTTPS and configure CORS for the deployed frontend domain.
- Use private durable object storage for resumes; local disk is development-only.
- Add email verification, password reset, rate limiting, malware scanning, and database migrations.
- Add retention/deletion controls and verify tenant ownership on every file operation.
- Run security and integration tests before accepting paying customers.

## Roadmap

1. OCR for scanned resumes and improved skill extraction
2. User job preferences and scheduled discovery
3. Real job-source adapters using permitted APIs/feeds
4. Application tracking and user-reviewed application drafts
5. Razorpay subscriptions and production deployment

This is a development MVP, not yet a production-ready paid SaaS.
