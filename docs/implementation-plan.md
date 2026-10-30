# Implementation plan

## Workspace findings

The workspace was empty apart from `.dist`; there was no existing application or Git executable. Node 24, npm 11, Python 3.13, FastAPI 0.135, Pydantic 2.12 and Uvicorn 0.42 are available. PostgreSQL, Docker, SQLAlchemy and Alembic are unavailable in the inspected environment.

## Architecture and assumptions

- Modular monolith: Next.js App Router frontend and FastAPI REST API under `/api/v1`.
- Use SQLite as an explicit local demonstration adapter so persistent workflows can run in this environment. The intended PostgreSQL/SQLAlchemy/Alembic production stack remains a follow-up; this deviation is not production-ready and is documented.
- Development-only bearer tokens are intentionally simple and clearly labelled. Production must replace this with a managed identity provider and secure session lifecycle.
- Implement core data flows first: opportunities/applications, course enrolment/progress, workshops, notifications, and public certificate lookup. Project upload and remaining domain workflows are staged and documented instead of being represented as operational when they are not.
- No external services, credentials, or paid resources are assumed.

## Milestones

1. Foundation: create frontend/backend skeleton, local configuration, health checks, design system and project docs.
2. Identity and authorization: development identity, roles, scoped checks and audit events.
3. Core workflows: persist internship applications, courses/progress, workshops and registrations.
4. Files, certificates, notifications: implement honest local notification and certificate demo flows; defer scanning/email integrations until configured.
5. Dashboards and reports: expose database-backed views and meaningful empty states.
6. Hardening and handover: run checks available in the workspace and document deviations and unfinished work.

## Initial structure

```text
frontend/       Next.js app, reusable UI and API client
backend/app/    FastAPI application, auth, database and domain routes
backend/tests/  API/business-rule checks
docs/           architecture, traceability and operational notes
```

## Handover status

| Milestone | Status | Evidence / remaining work |
|---|---|---|
| 1. Foundation | Complete for local demo | Next.js production build, FastAPI health/readiness, local setup docs; SQLite substitutes for PostgreSQL. |
| 2. Identity and authorization | Partial | Password login, expiring revocable sessions, role checks and organization/assignment-scoped data are implemented. Managed identity, registration/verification/reset, MFA and broader tenant membership administration remain. |
| 3. Core workflows | Partial | Applications/review with duplicate-safe participation creation, mentor assignment/rosters, course enrolment/progress and workshop registration are persistent. Quiz/assessment, ZIP project work and mentorship sessions remain. |
| 4. Files, certificates and notifications | Partial | Notification list/read API and safe public certificate lookup exist. Upload/scanning, certificate eligibility/issuance/PDF/QR/revocation, outbox, email and worker remain. |
| 5. Dashboards and reporting | Partial | Responsive role-aware demo dashboard reads API records. Required route-by-route workspaces, admin reports and exports remain. |
| 6. Hardening and handover | Partial | Six API tests, frontend lint and production build passed. Dependency/secret scans, PostgreSQL migration validation, accessibility/browser checks, operational backup tests and production security review remain. |
