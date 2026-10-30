# Architecture and operations

## Current local prototype

The system is a modular monolith with a Next.js App Router frontend and FastAPI API. The REST API is versioned at `/api/v1`; Pydantic validates payloads and FastAPI publishes OpenAPI. SQLite stores relational records locally, with foreign keys and uniqueness constraints. Startup creates missing tables and seeds safe demo catalogue rows. Because SQLAlchemy and Alembic were unavailable during workspace inspection, schema changes currently need a future migration conversion before the schema evolves.

The main implemented domain paths are applications, course enrolments/progress, workshop registrations, notifications and public certificate status. Demo auth in `backend/app/auth.py` uses fixed local IDs and must be replaced before hosting the app.

## Target boundaries

When upgraded, retain domain modules for identity/organizations, internships, learning, projects/files, mentorship/workshops, certificates, notifications/jobs and reporting. Keep policy checks in API/service boundaries; repositories should apply organization, ownership, programme and assignment scope. PostgreSQL is the system of record. Binary files belong in private S3-compatible storage, not database blobs or public buckets.

## Upload and scanning target

The prototype does not accept files. A production upload flow should authorize assignment membership and deadline before issuing an upload intent, store to private quarantine under an opaque key, enforce configurable size/type/signature limits, hash content, inspect ZIP paths/entry counts/expanded size/compression ratio without executing uploaded code, and keep files unavailable to reviewers until a real isolated malware scanner returns a recorded result. Scanner unavailability must remain pending or blocked.

## Certificates target

The prototype only supports a public lookup API and does not issue certificates. The target flow snapshots completion-rule version, checks eligibility server-side, records authorized approval and a unique issuance transaction, generates a versioned PDF and QR that encodes only the verification identifier, stores the document privately, and exposes a minimal verification response. Revocation must preserve history.

## Jobs, email and operations

No external email or job worker is connected. The production direction is a database-backed outbox/job table with bounded exponential retries, stable deduplication keys, delivery status and operator visibility. `/api/v1/health` checks process health; `/api/v1/ready` verifies SQLite access. Production readiness needs dependency health, structured logs, metrics, secret/dependency scans, backups and a tested restore procedure.

## Backup and deployment

The local database is `backend/data/lms.db`; stop the backend before copying it for a consistent local backup. Restore by placing a known-good copy at the configured path and starting the API. Production requires managed PostgreSQL backups and a documented restore drill. The target deployment separates frontend, API and worker, uses HTTPS, private storage, managed secrets and separate dev/staging/production configuration. No deployment or cloud service has been created.
