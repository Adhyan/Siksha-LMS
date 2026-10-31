"""SQLite-backed local persistence adapter. Replace with PostgreSQL in production."""
import os
import sqlite3
import hashlib
import secrets
from contextlib import contextmanager
from pathlib import Path

DB_PATH = os.getenv("LMS_DB_PATH", str(Path(__file__).resolve().parents[1] / "data" / "lms.db"))

def create_password_hash(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000).hex()
    return f"pbkdf2_sha256$310000${salt.hex()}${digest}"

# Keep the demo seed data compatible with existing imports.
_demo_password_hash = create_password_hash

@contextmanager
def connect():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH, timeout=15)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def initialize():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, role TEXT NOT NULL, organization_id TEXT, password_hash TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS sessions(token_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id), expires_at TEXT NOT NULL, revoked INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS opportunities(id TEXT PRIMARY KEY, title TEXT NOT NULL, organization TEXT NOT NULL, location TEXT NOT NULL, category TEXT NOT NULL, description TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'published', organization_id TEXT NOT NULL DEFAULT 'northstar');
        CREATE TABLE IF NOT EXISTS applications(id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id), opportunity_id TEXT NOT NULL REFERENCES opportunities(id), status TEXT NOT NULL DEFAULT 'submitted', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE(user_id, opportunity_id));
        CREATE TABLE IF NOT EXISTS internship_records(id TEXT PRIMARY KEY, application_id TEXT NOT NULL UNIQUE REFERENCES applications(id), user_id TEXT NOT NULL REFERENCES users(id), opportunity_id TEXT NOT NULL REFERENCES opportunities(id), created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE(user_id,opportunity_id));
        CREATE TABLE IF NOT EXISTS mentor_assignments(id TEXT PRIMARY KEY, internship_record_id TEXT NOT NULL UNIQUE REFERENCES internship_records(id), mentor_id TEXT NOT NULL REFERENCES users(id), assigned_by TEXT NOT NULL REFERENCES users(id), created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS courses(id TEXT PRIMARY KEY, title TEXT NOT NULL, category TEXT NOT NULL, lessons INTEGER NOT NULL, published INTEGER NOT NULL DEFAULT 1);
        CREATE TABLE IF NOT EXISTS enrolments(id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id), course_id TEXT NOT NULL REFERENCES courses(id), UNIQUE(user_id,course_id));
        CREATE TABLE IF NOT EXISTS lesson_completions(user_id TEXT NOT NULL REFERENCES users(id), course_id TEXT NOT NULL REFERENCES courses(id), lesson_no INTEGER NOT NULL, PRIMARY KEY(user_id,course_id,lesson_no));
        CREATE TABLE IF NOT EXISTS workshops(id TEXT PRIMARY KEY, title TEXT NOT NULL, date TEXT NOT NULL, format TEXT NOT NULL, seats INTEGER NOT NULL, published INTEGER NOT NULL DEFAULT 1);
        CREATE TABLE IF NOT EXISTS workshop_registrations(id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id), workshop_id TEXT NOT NULL REFERENCES workshops(id), UNIQUE(user_id,workshop_id));
        CREATE TABLE IF NOT EXISTS notifications(id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id), title TEXT NOT NULL, body TEXT NOT NULL, read INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS certificates(id TEXT PRIMARY KEY, display_name TEXT NOT NULL, programme TEXT NOT NULL, organization TEXT NOT NULL, completion_date TEXT NOT NULL, status TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS audit_logs(id INTEGER PRIMARY KEY AUTOINCREMENT, actor_id TEXT NOT NULL, action TEXT NOT NULL, entity TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        """)
        opportunity_columns={row["name"] for row in db.execute("PRAGMA table_info(opportunities)")}
        if "organization_id" not in opportunity_columns:
            db.execute("ALTER TABLE opportunities ADD COLUMN organization_id TEXT NOT NULL DEFAULT 'northstar'")
        db.execute("INSERT OR IGNORE INTO users VALUES(?,?,?,?,?,?)", ('demo-student','XYZ','student@demo.local','student','northstar',_demo_password_hash('StudentDemo!2026')))
        db.execute("INSERT OR IGNORE INTO users VALUES(?,?,?,?,?,?)", ('demo-admin','XYZ','admin@demo.local','organization_admin','northstar',_demo_password_hash('AdminDemo!2026')))
        db.execute("INSERT OR IGNORE INTO users VALUES(?,?,?,?,?,?)", ('demo-mentor','XYZ','mentor@demo.local','mentor','northstar',_demo_password_hash('MentorDemo!2026')))
        db.execute("UPDATE users SET name='XYZ' WHERE id IN ('demo-student','demo-admin','demo-mentor')")
        db.executemany("INSERT OR IGNORE INTO opportunities VALUES(?,?,?,?,?,?,?,?)", [
            ('intern-product','Product Operations Intern','Tech & Trend Media Pvt. Ltd.','Hybrid · Bengaluru','Operations','Help teams turn learner feedback into clear, measurable product improvements.','published','northstar'),
            ('intern-data','Data Analytics Intern','Tech & Trend Media Pvt. Ltd.','Remote · India','Technology','Build dashboards and answer practical questions using real programme data.','published','northstar'),
            ('intern-design','Learning Experience Intern','Tech & Trend Media Pvt. Ltd.','On-site · Pune','Design','Create accessible learning journeys with instructors and subject experts.','published','northstar')])
        db.execute("UPDATE opportunities SET organization=? WHERE organization='Northstar Learning'", ('Tech & Trend Media Pvt. Ltd.',))
        db.executemany("INSERT OR IGNORE INTO courses VALUES(?,?,?,?,1)", [('course-product','Product thinking at work','Business',8),('course-data','Data storytelling','Technology',6),('course-design','Designing accessible learning','Design',7)])
        db.executemany("INSERT OR IGNORE INTO workshops VALUES(?,?,?,?,?,1)", [('workshop-career','Building a portfolio that gets noticed','2026-11-12','Online',60),('workshop-data','From spreadsheet to story','2026-11-19','Bengaluru',35),('workshop-interview','Interview practice studio','2026-11-26','Online',40)])
