import unittest
from fastapi.testclient import TestClient
from main import app
from db import Base, engine, db_session
from models import User, Link


class NoBuzzNetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        db_session.remove()
        Base.metadata.drop_all(bind=engine)

    def test_register_user(self):
        response = self.client.post(
            "/register",
            data={"name": "Jane", "email": "jane@example.com", "password": "testpass"},
            follow_redirects=False
        )
        self.assertEqual(response.status_code, 303)

        user = db_session.query(User).filter_by(email="jane@example.com").first()
        self.assertIsNotNone(user)

    def test_login_page_opens(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn("login", response.text.lower())

    def test_add_link(self):
        user = User(name="TestUser", email="test@test.com", hashed_password="fake", auth_provider="local")
        db_session.add(user)
        db_session.commit()

        link = Link(
            link="https://www.google.com",
            description="Google",
            owner=user.id,
            icon="https://www.google.com/favicon.ico"
        )
        db_session.add(link)
        db_session.commit()

        found = db_session.query(Link).filter_by(description="Google").first()
        self.assertIsNotNone(found)

if __name__ == "__main__":
    unittest.main()