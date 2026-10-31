import hashlib
import tempfile
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from backend.app import database
from backend.app.main import app

class LmsApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tempdir=tempfile.TemporaryDirectory()
        database.DB_PATH=str(Path(cls.tempdir.name)/"test.db")
        database.initialize()
        cls.client=TestClient(app)
        cls.tokens={}
        for account in ("student","admin","mentor"):
            cls.tokens[account]=cls.login(account)["access_token"]

    @classmethod
    def tearDownClass(cls):
        cls.client.close()
        cls.tempdir.cleanup()

    @classmethod
    def login(cls,account):
        credentials={"student":("student@demo.local","StudentDemo!2026"),"admin":("admin@demo.local","AdminDemo!2026"),"mentor":("mentor@demo.local","MentorDemo!2026")}[account]
        response=cls.client.post("/api/v1/auth/login",json={"email":credentials[0],"password":credentials[1]})
        if response.status_code != 200: raise AssertionError(response.text)
        return response.json()

    def auth(self,account="student"):
        return {"Authorization":f"Bearer {self.tokens[account]}"}

    def test_health_and_public_catalogue(self):
        self.assertEqual(self.client.get("/api/v1/health").status_code,200)
        self.assertEqual(self.client.get("/api/v1/ready").json()["database"],"sqlite-local")
        self.assertGreaterEqual(len(self.client.get("/api/v1/opportunities").json()),3)

    def test_password_login_expiry_and_logout_revocation(self):
        invalid=self.client.post("/api/v1/auth/login",json={"email":"student@demo.local","password":"wrong"})
        self.assertEqual(invalid.status_code,401)
        login=self.login("student")
        headers={"Authorization":f"Bearer {login['access_token']}"}
        self.assertEqual(self.client.get("/api/v1/me",headers=headers).status_code,200)
        self.assertEqual(self.client.post("/api/v1/auth/logout",headers=headers).status_code,200)
        self.assertEqual(self.client.get("/api/v1/me",headers=headers).status_code,401)
        expired=self.login("student")["access_token"]
        with database.connect() as db:
            db.execute("UPDATE sessions SET expires_at='2000-01-01 00:00:00' WHERE token_hash=?",(hashlib.sha256(expired.encode()).hexdigest(),))
        self.assertEqual(self.client.get("/api/v1/me",headers={"Authorization":f"Bearer {expired}"}).status_code,401)

    def test_application_is_private_and_duplicate_is_rejected(self):
        response=self.client.post("/api/v1/applications",headers=self.auth(),json={"opportunity_id":"intern-product"})
        self.assertEqual(response.status_code,201)
        self.assertEqual(self.client.post("/api/v1/applications",headers=self.auth(),json={"opportunity_id":"intern-product"}).status_code,409)
        self.assertEqual(len(self.client.get("/api/v1/applications",headers=self.auth()).json()),1)
        self.assertEqual(self.client.get("/api/v1/applications",headers=self.auth("mentor")).status_code,403)

    def test_role_check_and_scoped_decision(self):
        app_id=self.client.get("/api/v1/applications",headers=self.auth()).json()[0]["id"]
        self.assertEqual(self.client.post(f"/api/v1/applications/{app_id}/decision?status=accepted",headers=self.auth()).status_code,403)
        self.assertEqual(self.client.post(f"/api/v1/applications/{app_id}/decision?status=accepted",headers=self.auth("admin")).status_code,200)
        self.assertEqual(self.client.post(f"/api/v1/applications/{app_id}/decision?status=accepted",headers=self.auth("admin")).status_code,200)
        self.assertEqual(self.client.post(f"/api/v1/applications/{app_id}/decision?status=declined",headers=self.auth("admin")).status_code,409)
        self.assertEqual(len(self.client.get("/api/v1/internship-records",headers=self.auth()).json()),1)
        records=self.client.get("/api/v1/internship-records",headers=self.auth("admin")).json()
        self.assertEqual(len(records),1)
        mentors=self.client.get("/api/v1/organization/mentors",headers=self.auth("admin")).json()
        self.assertEqual(len(mentors),1)
        self.assertEqual(self.client.post(f"/api/v1/internship-records/{records[0]['id']}/assign-mentor",headers=self.auth("admin"),json={"mentor_id":mentors[0]["id"]}).status_code,200)
        assigned=self.client.get("/api/v1/mentor/assignments",headers=self.auth("mentor")).json()
        self.assertEqual(len(assigned),1)
        self.assertEqual(assigned[0]["candidate_name"],"XYZ")
        self.assertEqual(self.client.get("/api/v1/mentor/assignments",headers=self.auth()).status_code,403)

    def test_learning_requires_enrolment_and_progress_is_derived(self):
        no_access=self.client.post("/api/v1/courses/course-product/lessons/complete",headers=self.auth(),json={"lesson_no":1})
        self.assertEqual(no_access.status_code,403)
        self.assertEqual(self.client.post("/api/v1/courses/course-product/enrolments",headers=self.auth()).status_code,201)
        complete=self.client.post("/api/v1/courses/course-product/lessons/complete",headers=self.auth(),json={"lesson_no":1})
        self.assertEqual(complete.json()["progress"],13)

    def test_workshop_registration_is_unique(self):
        self.assertEqual(self.client.post("/api/v1/workshops/registrations",headers=self.auth(),json={"workshop_id":"workshop-career"}).status_code,201)
        self.assertEqual(self.client.post("/api/v1/workshops/registrations",headers=self.auth(),json={"workshop_id":"workshop-career"}).status_code,409)

if __name__=="__main__": unittest.main()
