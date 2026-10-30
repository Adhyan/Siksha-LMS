# Backend

The local API persists data in SQLite at `backend/data/lms.db` by default. Set `LMS_DB_PATH` to choose another file. Run from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```

OpenAPI is at `/docs`; health is `/api/v1/health`, readiness is `/api/v1/ready`. Use the credentials in the root README with `POST /api/v1/auth/login` to obtain a random eight-hour bearer session. `POST /api/v1/auth/logout` revokes that session. This local auth adapter does not include verification, password recovery, rate limiting, MFA, or a managed identity provider and must not be deployed. SQLite initialization is repeatable but is not a substitute for versioned Alembic migrations.
