# ARS — Upload MVP

## Run locally
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```
Open http://localhost:8080/upload

## Deploy on Render
- Root Directory: `backend`
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
Env vars:
- `ARS_API_KEY` (recommended)
- `SLACK_WEBHOOK_URL` (optional)
- `DATABASE_URL` (optional; defaults to sqlite)

Generated: 2025-12-17
