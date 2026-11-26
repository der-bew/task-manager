import unittest

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from api.v1.task import list_my_tasks
from db.base import Base
from models.task import Task
from models.user import User
from schemas.pagination import PaginationParams
from scripts.seed_tasks import seed_tasks


class SeedTasksTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        self.sessions = async_sessionmaker(self.engine, expire_on_commit=False)

    async def asyncTearDown(self):
        await self.engine.dispose()

    async def test_seeded_tasks_are_paginated_for_the_selected_user(self):
        async with self.sessions() as session:
            user = User(email="owner@example.com", hashed_password="unused")
            other = User(email="other@example.com", hashed_password="unused")
            session.add_all([user, other])
            await session.commit()

            self.assertEqual(await seed_tasks(" Owner@Example.com ", session), 25)
            pages = [
                await list_my_tasks(PaginationParams(page=page, size=10), session, user)
                for page in (1, 2, 3)
            ]
            self.assertEqual([len(page.items) for page in pages], [10, 10, 5])
            self.assertTrue(all(page.total == 25 and page.pages == 3 for page in pages))
            self.assertEqual(len({task.id for page in pages for task in page.items}), 25)
            other_page = await list_my_tasks(PaginationParams(), session, other)
            self.assertEqual(other_page.total, 0)

    async def test_unknown_user_does_not_create_tasks(self):
        async with self.sessions() as session:
            with self.assertRaises(LookupError):
                await seed_tasks("missing@example.com", session)
            self.assertEqual(await session.scalar(select(func.count()).select_from(Task)), 0)
