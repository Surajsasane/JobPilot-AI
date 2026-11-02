# JobPilot AI

A job-search assistant that helps users organize preferences, discover jobs from permitted sources, compare roles with their resumes, and prepare application drafts.

## MVP status

This repository starts with a safe, extensible foundation:
- FastAPI backend with health and demo job endpoints
- React + Vite frontend scaffold
- PostgreSQL configuration template
- Clear separation between job discovery, matching, and application preparation

**Important:** Job discovery integrations must use official APIs, feeds, or sources whose terms permit the intended access. This starter does not bypass CAPTCHAs, login controls, or anti-bot systems, and it does not submit applications automatically.

## Project structure

```
backend/
  app/
    main.py
    core/config.py
  requirements.txt
  .env.example
frontend/
  index.html
  package.json
  src/App.jsx
  src/main.jsx
  src/style.css
docker-compose.yml
.gitignore
```

## Run backend (Python 3.10+)

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs: http://127.0.0.1:8000/docs

## Run frontend (Node.js 20+)

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

## Configuration

Copy `backend/.env.example` to `backend/.env` and configure your own local values. Never commit passwords, API keys, OAuth tokens, or production secrets.

## Roadmap

1. User authentication and tenant isolation
2. Resume upload and structured profile extraction
3. Job source adapters using permitted APIs/feeds
4. Resume-to-job matching and saved searches
5. Application draft generation and user review
6. Subscription billing and production deployment

## License

This project is an original starter implementation. A license will be selected before public commercial distribution.
