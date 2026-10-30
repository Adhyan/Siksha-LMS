import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import Header, HTTPException
from .database import connect

def _password_matches(password: str, encoded: str) -> bool:
    try:
        scheme, rounds, salt_hex, digest = encoded.split("$")
        if scheme != "pbkdf2_sha256": return False
        candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), int(rounds)).hex()
        return secrets.compare_digest(candidate, digest)
    except (ValueError, TypeError):
        return False

def create_session(email: str, password: str):
    with connect() as db:
        user = db.execute("SELECT * FROM users WHERE email=?", (email.strip().lower(),)).fetchone()
        if not user or not _password_matches(password, user["password_hash"]):
            raise HTTPException(401, "Email or password is incorrect.")
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        expiry = (datetime.now(timezone.utc) + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        db.execute("INSERT INTO sessions(token_hash,user_id,expires_at) VALUES(?,?,?)", (token_hash,user["id"],expiry))
        return token, {k:v for k,v in dict(user).items() if k != "password_hash"}

def current_user(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Sign in to continue.")
    token_hash = hashlib.sha256(authorization.removeprefix("Bearer ").encode()).hexdigest()
    with connect() as db:
        row = db.execute("SELECT u.* FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token_hash=? AND s.revoked=0 AND s.expires_at>datetime('now')", (token_hash,)).fetchone()
    if not row:
        raise HTTPException(401, "Session expired or revoked. Sign in again.")
    return {k:v for k,v in dict(row).items() if k != "password_hash"}

def require_role(user, *roles):
    if user["role"] not in roles:
        raise HTTPException(403, "You do not have permission to perform this action.")
