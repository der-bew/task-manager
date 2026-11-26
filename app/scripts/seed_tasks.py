import argparse
import asyncio
import sys

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import async_session, engine
from models.task import Task
from models.user import User


TASK_TITLES = [
    "Plan the week",
    "Review project goals",
    "Update the task backlog",
    "Organize project files",
    "Prepare meeting notes",
    "Review open questions",
    "Write project documentation",
    "Check upcoming deadlines",
    "Prioritize pending work",
    "Review the project schedule",
    "Create a progress report",
    "Update the project roadmap",
    "Review team feedback",
    "Prepare the next milestone",
    "Check completed tasks",
    "Organize reference materials",
    "Draft a project summary",
    "Review the testing checklist",
    "Plan the next release",
    "Update the issue tracker",
    "Review outstanding changes",
    "Prepare a status update",
    "Check project dependencies",
    "Schedule a retrospective",
    "Plan the next sprint",
]


async def seed_tasks(email: str, session: AsyncSession) -> int:
    user = await session.scalar(select(User).where(User.email == email.strip().lower()))
    if user is None:
        raise LookupError("User not found. Register the account before seeding tasks.")

    session.add_all(Task(title=title, owner_id=user.id) for title in TASK_TITLES)
    await session.commit()
    return len(TASK_TITLES)


async def main(email: str) -> int:
    try:
        async with async_session() as session:
            try:
                count = await seed_tasks(email, session)
            except LookupError as exc:
                print(exc, file=sys.stderr)
                return 1
        print(f"Added {count} tasks for {email.strip().lower()}.")
        return 0
    finally:
        await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add sample tasks for an existing user.")
    parser.add_argument("email", help="Email address of the task owner")
    args = parser.parse_args()
    raise SystemExit(asyncio.run(main(args.email)))
