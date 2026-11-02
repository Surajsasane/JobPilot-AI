# JobPilot AI

A job-search assistant for organizing job preferences, discovering opportunities from permitted sources, matching roles, and preparing applications for user review.

## Current MVP features

- User registration and login (JWT access tokens)
- Password hashing with Argon2
- User profile endpoint
- Private resume upload (PDF, DOC, DOCX; maximum 5 MB by default)
- Resume list scoped to the signed-in user
- SQLAlchemy database models for users and resumes
- SQLite for simple local development; PostgreSQL supported through configuration
- React dashboard with registration, login, resume upload, and demo job matching

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

The backend runs at http://127.0.0.1:8000 and creates a local SQLite database file named `jobpilot.db`. Uploaded resumes are stored in `backend/uploads`.

API documentation: http://127.0.0.1:8000/docs

### 2. Frontend

Open a second CMD window in the project folder:

```bat
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

Register an account in the dashboard, sign in, and upload a PDF, DOC, or DOCX resume.

## Main API endpoints

- `POST /api/v1/auth/register` — create an account
- `POST /api/v1/auth/login` — sign in and receive a JWT
- `GET /api/v1/auth/me` — current signed-in user (Bearer token required)
- `POST /api/v1/resumes/upload` — upload a resume (Bearer token required)
- `GET /api/v1/resumes/` — list your own resumes (Bearer token required)
- `GET /health` — backend health check

## PostgreSQL

For local SQLite, keep the example `DATABASE_URL`. To use PostgreSQL, set a PostgreSQL SQLAlchemy URL in `backend/.env`, for example:

```env
DATABASE_URL=postgresql+psycopg://USERNAME:PASSWORD@localhost:5432/jobpilot
```

The `docker-compose.yml` file includes PostgreSQL and Redis services. Start them with `docker compose up -d`, then configure the PostgreSQL URL above.

## Security notes before deployment

- Replace `SECRET_KEY` with a long, randomly generated secret.
- Never commit `.env`, passwords, API keys, OAuth tokens, or production secrets.
- Use HTTPS in production and configure CORS for your real frontend domain.
- Configure private, durable object storage for resumes; local disk storage is only for development.
- Add email verification, password reset, rate limiting, malware scanning, and database migrations before production.
- Keep uploaded resume access private and enforce tenant ownership on every endpoint.

## Roadmap

1. Resume text extraction and profile parsing
2. Saved job preferences and scheduled job discovery
3. Permitted job-source adapters and duplicate detection
4. Better resume-to-job matching and application tracking
5. Subscription billing and production deployment

This is an MVP foundation, not yet a production-ready paid SaaS.
