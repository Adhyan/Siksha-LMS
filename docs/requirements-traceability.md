# Requirements traceability

Status is deliberately conservative: **Implemented** means present in source; **Verified** means the check was actually run.

| Requirement | Location | Status |
|---|---|---|
| Workspace inspection and architecture plan | `docs/implementation-plan.md` | Verified |
| Traceability | This document | Implemented |
| FastAPI `/api/v1` and health/readiness | `backend/app/main.py` | Implemented and API-tested |
| Local persistent store | `backend/app/database.py` | Implemented with SQLite compatibility deviation |
| Password-verified demo identity, revocable sessions, server-side role checks | `backend/app/auth.py`, `backend/app/main.py` | Implemented and API-tested for local demos only |
| Opportunities and applications | `backend/app/main.py` | Implemented and API-tested |
| Acceptance creates exactly one internship record | `backend/app/database.py`, `backend/app/main.py` | Implemented and API-tested for idempotent repeated acceptance |
| Organization application review and mentor assignment; mentor-only assigned roster | `backend/app/main.py`, `frontend/app/page.tsx` | Implemented with organization/assignment scope and API-tested |
| Course enrolment and lesson progress | `backend/app/main.py` | Implemented and API-tested, compact demo domain |
| Workshops, registrations, notifications | `backend/app/main.py` | Implemented and API-tested for registrations |
| Public certificate lookup | `backend/app/main.py` | Implemented as safe lookup only; no issuance/PDF workflow |
| Responsive sign-in and role-specific candidate, mentor, and organization-admin workspaces | `frontend/app/page.tsx`, `frontend/app/globals.css` | Implemented; admin review and mentor assignment connected to scoped APIs |
| Public-facing homepage/catalogue/detail/legal pages | Not implemented | Deferred; published opportunities, courses, workshops and certificate lookup are API-only |
| Required route-specific role workspaces | Not implemented | Deferred; current UI is a single responsive dashboard route with tabs |
| PostgreSQL, SQLAlchemy, Alembic | — | Deferred; tooling unavailable, SQLite fallback documented |
| Managed authentication, MFA, email, object storage, malware scan | — | Deferred pending configuration |
| ZIP submissions, mentorship, full course authoring, admin operations | — | Deferred |
| Backend API/business tests | `backend/tests/test_api.py` | Verified: 6 tests pass, including acceptance idempotency |
| Frontend production build | `frontend/package.json` | Verified: Next.js 16.4.3 build passes |
| Frontend lint | `frontend/package.json`, `frontend/eslint.config.mjs` | Verified: passes |
