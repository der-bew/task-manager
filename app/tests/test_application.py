import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import main
from api.v1.auth import login, register
from core.security import create_access_token
from db.session import get_db
from schemas.user import UserCreate


class ApplicationTests(unittest.TestCase):
    def test_authentication_and_task_flow(self):
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        sessions = async_sessionmaker(engine, expire_on_commit=False)

        async def test_db():
            async with sessions() as session:
                yield session

        main.app.dependency_overrides[get_db] = test_db
        try:
            with patch.object(main, "engine", engine), TestClient(main.app) as client:
                user = {"email": "Example@Example.com", "password": "password123"}
                response = client.post("/api/v1/auth/register", json=user)
                self.assertEqual(response.status_code, 201)
                self.assertEqual(response.json()["email"], "example@example.com")
                self.assertEqual(client.post("/api/v1/auth/register", json=user).status_code, 400)

                response = client.post("/api/v1/auth/login", data={
                    "username": user["email"], "password": user["password"]
                })
                self.assertEqual(response.status_code, 200)
                headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
                response = client.post("/api/v1/tasks/", json={"title": "First"}, headers=headers)
                self.assertEqual(response.status_code, 201)
                task_id = response.json()["id"]
                response = client.get("/api/v1/tasks/", headers=headers)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()["total"], 1)
                self.assertEqual(client.patch(
                    f"/api/v1/tasks/{task_id}", json={"is_completed": True}, headers=headers
                ).json()["is_completed"], True)

                for subject in ("invalid", "9" * 100):
                    token = create_access_token(subject)
                    response = client.get("/api/v1/tasks/", headers={"Authorization": f"Bearer {token}"})
                    self.assertEqual(response.status_code, 401)
        finally:
            main.app.dependency_overrides.pop(get_db, None)


class RegistrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_inactive_user_cannot_log_in(self):
        db = MagicMock()
        db.scalar = AsyncMock(return_value=SimpleNamespace(is_active=False))
        form = SimpleNamespace(username="user@example.com", password="password123")
        with self.assertRaises(HTTPException) as error:
            await login(db, form)
        self.assertEqual(error.exception.status_code, 401)

    async def test_integrity_errors_only_report_duplicate_when_user_exists(self):
        for existing in (1, None):
            with self.subTest(existing=existing):
                db = MagicMock()
                result = MagicMock()
                result.scalar_one_or_none.return_value = None
                db.execute = AsyncMock(return_value=result)
                db.scalar = AsyncMock(return_value=existing)
                db.commit = AsyncMock(side_effect=IntegrityError("insert", {}, Exception()))
                db.rollback = AsyncMock()
                data = UserCreate(email="user@example.com", password="password123")
                with patch("api.v1.auth.get_password_hash", return_value="hash"):
                    with self.assertRaises(HTTPException if existing else IntegrityError):
                        await register(data, db)
                db.rollback.assert_awaited_once()
