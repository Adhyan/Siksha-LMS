from contextlib import asynccontextmanager
import hashlib
from uuid import uuid4
from fastapi import FastAPI, Depends, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from .database import connect, initialize
from .auth import current_user, create_session, require_role

@asynccontextmanager
async def lifespan(app):
    initialize()
    yield

app = FastAPI(title="Northstar LMS API", version="0.1.0", description="Local demonstration API. Demo authentication is not suitable for production.", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"], allow_credentials=False, allow_methods=["GET","POST","PATCH"], allow_headers=["Authorization","Content-Type"])

class ApplicationIn(BaseModel):
    opportunity_id: str

class RegistrationIn(BaseModel):
    workshop_id: str

class CompletionIn(BaseModel):
    lesson_no: int = Field(ge=1)

class LoginIn(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=200)

class MentorAssignmentIn(BaseModel):
    mentor_id: str

@app.get("/api/v1/health")
def health(): return {"status":"ok"}

@app.get("/api/v1/ready")
def ready():
    with connect() as db: db.execute("SELECT 1")
    return {"status":"ready","database":"sqlite-local"}

@app.get("/api/v1/me")
def me(user=Depends(current_user)): return {k:v for k,v in user.items() if k != "organization_id"} | {"organization_id":user["organization_id"]}

@app.post("/api/v1/auth/login")
def login(payload: LoginIn):
    token, user = create_session(payload.email, payload.password)
    return {"access_token":token,"token_type":"bearer","expires_in":28800,"user":{k:v for k,v in user.items() if k != "organization_id"} | {"organization_id":user["organization_id"]}}

@app.post("/api/v1/auth/logout")
def logout(authorization: str | None = Header(default=None),user=Depends(current_user)):
    if authorization is None: raise HTTPException(401,"Sign in to continue.")
    token_hash=hashlib.sha256(authorization.removeprefix("Bearer ").encode()).hexdigest()
    with connect() as db: db.execute("UPDATE sessions SET revoked=1 WHERE token_hash=?",(token_hash,))
    return {"status":"signed_out"}

@app.get("/api/v1/opportunities")
def opportunities(q: str = Query(default="", max_length=100)):
    with connect() as db:
        return [dict(r) for r in db.execute("SELECT id,title,organization,location,category,description FROM opportunities WHERE status='published' AND (title LIKE ? OR category LIKE ? OR location LIKE ?) ORDER BY title", (f"%{q}%",)*3)]

@app.get("/api/v1/applications")
def applications(user=Depends(current_user)):
    with connect() as db:
        if user["role"] in ("student","intern"):
            rows=db.execute("SELECT a.id,a.status,a.created_at,o.title opportunity_title FROM applications a JOIN opportunities o ON o.id=a.opportunity_id WHERE a.user_id=? ORDER BY a.created_at DESC",(user["id"],))
        elif user["role"] in ("organization_admin","platform_admin"):
            rows=db.execute("SELECT a.id,a.status,a.created_at,o.title opportunity_title,u.name candidate_name FROM applications a JOIN opportunities o ON o.id=a.opportunity_id JOIN users u ON u.id=a.user_id WHERE (?='platform_admin' OR o.organization_id=?) ORDER BY a.created_at DESC",(user["role"],user["organization_id"]))
        else:
            raise HTTPException(403,"You do not have permission to review applications.")
        return [dict(r) for r in rows]

@app.post("/api/v1/applications", status_code=201)
def apply(payload: ApplicationIn, user=Depends(current_user)):
    require_role(user,"student","intern")
    with connect() as db:
        if not db.execute("SELECT 1 FROM opportunities WHERE id=? AND status='published'",(payload.opportunity_id,)).fetchone(): raise HTTPException(404,"Published opportunity not found.")
        ident=str(uuid4())
        try: db.execute("INSERT INTO applications(id,user_id,opportunity_id) VALUES(?,?,?)",(ident,user["id"],payload.opportunity_id))
        except Exception as exc:
            if "UNIQUE" in str(exc): raise HTTPException(409,"You have already applied to this opportunity.")
            raise
        db.execute("INSERT INTO audit_logs(actor_id,action,entity) VALUES(?,?,?)",(user["id"],"application.submitted",ident))
        return {"id":ident,"status":"submitted"}

@app.post("/api/v1/applications/{application_id}/decision")
def decide(application_id: str, status: str = Query(pattern="^(accepted|declined|under_review)$"), user=Depends(current_user)):
    require_role(user,"organization_admin","platform_admin")
    with connect() as db:
        row=db.execute("SELECT a.id,a.user_id,a.status current_status,a.opportunity_id,o.organization_id FROM applications a JOIN opportunities o ON o.id=a.opportunity_id WHERE a.id=?",(application_id,)).fetchone()
        if not row: raise HTTPException(404,"Application not found.")
        if user["role"] != "platform_admin" and user["organization_id"] != row["organization_id"]: raise HTTPException(403,"Organization scope denied.")
        if row["current_status"] in ("accepted","declined") and row["current_status"] != status:
            raise HTTPException(409,"A final application decision cannot be changed.")
        db.execute("UPDATE applications SET status=? WHERE id=?",(status,application_id))
        if status == "accepted":
            db.execute("INSERT OR IGNORE INTO internship_records(id,application_id,user_id,opportunity_id) VALUES(?,?,?,?)",(str(uuid4()),application_id,row["user_id"],row["opportunity_id"]))
        db.execute("INSERT INTO audit_logs(actor_id,action,entity) VALUES(?,?,?)",(user["id"],f"application.{status}",application_id))
        return {"id":application_id,"status":status}

@app.get("/api/v1/internship-records")
def internship_records(user=Depends(current_user)):
    with connect() as db:
        if user["role"] in ("student","intern"):
            rows=db.execute("SELECT r.id,r.created_at,o.title opportunity_title FROM internship_records r JOIN opportunities o ON o.id=r.opportunity_id WHERE r.user_id=? ORDER BY r.created_at DESC",(user["id"],))
        elif user["role"] in ("organization_admin","platform_admin"):
            rows=db.execute("SELECT r.id,r.created_at,o.title opportunity_title,u.name candidate_name FROM internship_records r JOIN opportunities o ON o.id=r.opportunity_id JOIN users u ON u.id=r.user_id WHERE (?='platform_admin' OR o.organization_id=?) ORDER BY r.created_at DESC",(user["role"],user["organization_id"]))
        else:
            raise HTTPException(403,"You do not have permission to view internship records.")
        return [dict(row) for row in rows]

@app.get("/api/v1/organization/mentors")
def organization_mentors(user=Depends(current_user)):
    require_role(user,"organization_admin","platform_admin")
    with connect() as db:
        rows=db.execute("SELECT id,name FROM users WHERE role='mentor' AND (?='platform_admin' OR organization_id=?) ORDER BY name",(user["role"],user["organization_id"]))
        return [dict(row) for row in rows]

@app.post("/api/v1/internship-records/{record_id}/assign-mentor")
def assign_mentor(record_id: str,payload: MentorAssignmentIn,user=Depends(current_user)):
    require_role(user,"organization_admin","platform_admin")
    with connect() as db:
        record=db.execute("SELECT r.id,o.organization_id FROM internship_records r JOIN opportunities o ON o.id=r.opportunity_id WHERE r.id=?",(record_id,)).fetchone()
        mentor=db.execute("SELECT id FROM users WHERE id=? AND role='mentor' AND (?='platform_admin' OR organization_id=?)",(payload.mentor_id,user["role"],user["organization_id"])).fetchone()
        if not record or not mentor: raise HTTPException(404,"Internship record or organization mentor not found.")
        if user["role"] != "platform_admin" and record["organization_id"] != user["organization_id"]:
            raise HTTPException(403,"Organization scope denied.")
        existing=db.execute("SELECT id FROM mentor_assignments WHERE internship_record_id=?",(record_id,)).fetchone()
        if existing:
            db.execute("UPDATE mentor_assignments SET mentor_id=?,assigned_by=?,created_at=CURRENT_TIMESTAMP WHERE id=?",(payload.mentor_id,user["id"],existing["id"]))
            assignment_id=existing["id"]
        else:
            assignment_id=str(uuid4())
            db.execute("INSERT INTO mentor_assignments(id,internship_record_id,mentor_id,assigned_by) VALUES(?,?,?,?)",(assignment_id,record_id,payload.mentor_id,user["id"]))
        db.execute("INSERT INTO audit_logs(actor_id,action,entity) VALUES(?,?,?)",(user["id"],"mentor.assigned",record_id))
        return {"id":assignment_id,"internship_record_id":record_id,"mentor_id":payload.mentor_id,"status":"assigned"}

@app.get("/api/v1/mentor/assignments")
def mentor_assignments(user=Depends(current_user)):
    require_role(user,"mentor")
    with connect() as db:
        rows=db.execute("SELECT r.id internship_record_id,r.created_at,o.title opportunity_title,u.name candidate_name FROM mentor_assignments m JOIN internship_records r ON r.id=m.internship_record_id JOIN users u ON u.id=r.user_id JOIN opportunities o ON o.id=r.opportunity_id WHERE m.mentor_id=? ORDER BY m.created_at DESC",(user["id"],))
        return [dict(row) for row in rows]

@app.get("/api/v1/courses")
def courses():
    with connect() as db: return [dict(r) for r in db.execute("SELECT id,title,category,lessons FROM courses WHERE published=1 ORDER BY title")]

@app.post("/api/v1/courses/{course_id}/enrolments",status_code=201)
def enrol(course_id: str,user=Depends(current_user)):
    require_role(user,"student","intern")
    with connect() as db:
        course=db.execute("SELECT id FROM courses WHERE id=? AND published=1",(course_id,)).fetchone()
        if not course: raise HTTPException(404,"Course not found.")
        ident=str(uuid4())
        try: db.execute("INSERT INTO enrolments VALUES(?,?,?)",(ident,user["id"],course_id))
        except Exception as exc:
            if "UNIQUE" in str(exc): raise HTTPException(409,"Already enrolled.")
            raise
        return {"id":ident,"course_id":course_id,"status":"enrolled"}

@app.post("/api/v1/courses/{course_id}/lessons/complete")
def complete_lesson(course_id: str,payload: CompletionIn,user=Depends(current_user)):
    with connect() as db:
        course=db.execute("SELECT lessons FROM courses WHERE id=?",(course_id,)).fetchone()
        if not course: raise HTTPException(404,"Course not found.")
        if payload.lesson_no>course["lessons"]: raise HTTPException(422,"Lesson number exceeds course length.")
        if not db.execute("SELECT 1 FROM enrolments WHERE course_id=? AND user_id=?",(course_id,user["id"])).fetchone(): raise HTTPException(403,"Enrolment required.")
        db.execute("INSERT OR IGNORE INTO lesson_completions VALUES(?,?,?)",(user["id"],course_id,payload.lesson_no))
        count=db.execute("SELECT COUNT(*) n FROM lesson_completions WHERE user_id=? AND course_id=?",(user["id"],course_id)).fetchone()["n"]
        return {"completed_lessons":count,"total_lessons":course["lessons"],"progress":(count*100+course["lessons"]//2)//course["lessons"]}

@app.get("/api/v1/courses/progress")
def progress(user=Depends(current_user)):
    with connect() as db:
        return [dict(r) for r in db.execute("SELECT c.id course_id,c.title,c.lessons total_lessons,COUNT(l.lesson_no) completed_lessons,CAST(COUNT(l.lesson_no)*100.0/c.lessons AS INTEGER) progress FROM enrolments e JOIN courses c ON c.id=e.course_id LEFT JOIN lesson_completions l ON l.course_id=c.id AND l.user_id=e.user_id WHERE e.user_id=? GROUP BY c.id",(user["id"],))]

@app.get("/api/v1/workshops")
def workshops():
    with connect() as db: return [dict(r) for r in db.execute("SELECT id,title,date,format,seats FROM workshops WHERE published=1 ORDER BY date")]

@app.post("/api/v1/workshops/registrations",status_code=201)
def register(payload: RegistrationIn,user=Depends(current_user)):
    require_role(user,"student","intern")
    with connect() as db:
        workshop=db.execute("SELECT seats FROM workshops WHERE id=? AND published=1",(payload.workshop_id,)).fetchone()
        if not workshop: raise HTTPException(404,"Workshop not found.")
        used=db.execute("SELECT COUNT(*) n FROM workshop_registrations WHERE workshop_id=?",(payload.workshop_id,)).fetchone()["n"]
        if used>=workshop["seats"]: raise HTTPException(409,"Workshop is full.")
        try: db.execute("INSERT INTO workshop_registrations VALUES(?,?,?)",(str(uuid4()),user["id"],payload.workshop_id))
        except Exception as exc:
            if "UNIQUE" in str(exc): raise HTTPException(409,"Already registered.")
            raise
        return {"status":"registered"}

@app.get("/api/v1/notifications")
def notifications(user=Depends(current_user)):
    with connect() as db: return [dict(r) for r in db.execute("SELECT id,title,body,read,created_at FROM notifications WHERE user_id=? ORDER BY created_at DESC",(user["id"],))]

@app.patch("/api/v1/notifications/{notification_id}")
def mark_read(notification_id: str,user=Depends(current_user)):
    with connect() as db:
        cursor=db.execute("UPDATE notifications SET read=1 WHERE id=? AND user_id=?",(notification_id,user["id"]))
        if not cursor.rowcount: raise HTTPException(404,"Notification not found.")
    return {"status":"read"}

@app.get("/api/v1/public/certificates/{certificate_id}")
def verify(certificate_id: str):
    with connect() as db: row=db.execute("SELECT id,display_name,programme,organization,completion_date,status FROM certificates WHERE id=?",(certificate_id,)).fetchone()
    if not row: raise HTTPException(404,"Certificate not found.")
    return dict(row)
