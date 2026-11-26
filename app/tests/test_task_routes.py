import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from fastapi import HTTPException
from pydantic import ValidationError

from api.deps import get_current_user
from api.v1.task import get_task, list_all_tasks_admin, list_my_tasks, update_task
from core.security import create_access_token
from schemas.pagination import PaginationParams
from schemas.task import TaskUpdate


class TaskRouteTests(unittest.IsolatedAsyncioTestCase):
    async def test_list_routes_apply_pagination(self):
        user = SimpleNamespace(id=1, is_admin=True)
        params = PaginationParams(page=3, size=5)
        for route in (list_my_tasks, list_all_tasks_admin):
            with self.subTest(route=route.__name__):
                db = MagicMock()
                count = MagicMock()
                count.scalar_one.return_value = 7
                rows = MagicMock()
                rows.scalars.return_value.all.return_value = []
                db.execute = AsyncMock(side_effect=[count, rows])

                response = await route(params, db, user)

                self.assertEqual((response.total, response.page, response.pages), (7, 3, 2))
                query = db.execute.await_args_list[1].args[0]
                compiled = query.compile().params
                self.assertIn(5, compiled.values())
                self.assertIn(10, compiled.values())

    async def test_task_access_is_restricted_to_owner_or_admin(self):
        task = SimpleNamespace(owner_id=1)
        result = MagicMock()
        result.scalars.return_value.first.return_value = task
        db = MagicMock()
        db.execute = AsyncMock(return_value=result)

        with self.assertRaises(HTTPException) as error:
            await get_task(3, db, SimpleNamespace(id=2, is_admin=False))
        self.assertEqual(error.exception.status_code, 403)
        self.assertIs(await get_task(3, db, SimpleNamespace(id=2, is_admin=True)), task)

        with self.assertRaises(HTTPException) as error:
            await update_task(3, TaskUpdate(title="changed"), db, SimpleNamespace(id=2, is_admin=False))
        self.assertEqual(error.exception.status_code, 403)

        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        self.assertIs(await update_task(3, TaskUpdate(title="changed"), db, SimpleNamespace(id=1, is_admin=False)), task)
        self.assertEqual(task.title, "changed")
        db.commit.assert_awaited_once()

    async def test_authentication_awaits_database_query(self):
        user = SimpleNamespace(id=1, is_active=True)
        result = MagicMock()
        result.scalar_one_or_none.return_value = user
        db = MagicMock()
        db.execute = AsyncMock(return_value=result)

        self.assertIs(await get_current_user(db, create_access_token("1")), user)
        db.execute.assert_awaited_once()


class TaskUpdateTests(unittest.TestCase):
    def test_partial_update_validation(self):
        self.assertEqual(TaskUpdate(description=None).model_dump(exclude_unset=True), {"description": None})
        for field in ("title", "is_completed"):
            with self.subTest(field=field), self.assertRaises(ValidationError):
                TaskUpdate.model_validate({field: None})
        with self.assertRaises(ValidationError):
            TaskUpdate(description="x" * 10001)
