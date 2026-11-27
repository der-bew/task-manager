import argparse
import asyncio
import sys

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import async_session, engine
from models.task import Task
from models.user import User


SAMPLE_TASKS = [
    ("Plan the week", "Set priorities and schedule the work to complete this week."),
    ("Review project goals", "Check the project goals and confirm they remain relevant."),
    ("Update the task backlog", "Add new work and refine existing items in the backlog."),
    ("Organize project files", "Sort project files and remove outdated duplicates."),
    ("Prepare meeting notes", "Collect the agenda, discussion points, and action items for the meeting."),
    ("Review open questions", "Identify unanswered questions and assign owners to resolve them."),
    ("Write project documentation", "Document the project's setup, usage, and important decisions."),
    ("Check upcoming deadlines", "Review approaching due dates and flag work at risk of delay."),
    ("Prioritize pending work", "Rank unfinished tasks by urgency and impact."),
    ("Review the project schedule", "Compare planned dates with current progress and adjust as needed."),
    ("Create a progress report", "Summarize completed work, remaining tasks, and current risks."),
    ("Update the project roadmap", "Revise upcoming milestones and priorities based on current plans."),
    ("Review team feedback", "Collect team feedback and identify improvements to pursue."),
    ("Prepare the next milestone", "Define the deliverables and tasks needed for the next milestone."),
    ("Check completed tasks", "Verify completed work and record any follow-up actions."),
    ("Organize reference materials", "Arrange useful links and documents so they are easy to find."),
    ("Draft a project summary", "Write a concise overview of the project's purpose and progress."),
    ("Review the testing checklist", "Check that planned test cases cover the relevant requirements."),
    ("Plan the next release", "Identify release scope, outstanding work, and the target date."),
    ("Update the issue tracker", "Record new issues and update the status of existing ones."),
    ("Review outstanding changes", "Examine pending changes and identify any remaining review work."),
    ("Prepare a status update", "Share recent progress, upcoming work, and any blockers."),
    ("Check project dependencies", "Review dependencies and identify updates or potential conflicts."),
    ("Schedule a retrospective", "Set a time to discuss what went well and what could improve."),
    ("Plan the next sprint", "Select and estimate the work to include in the next sprint."),
]


async def seed_tasks(email: str, session: AsyncSession) -> int:
    user = await session.scalar(select(User).where(User.email == email.strip().lower()))
    if user is None:
        raise LookupError("User not found. Register the account before seeding tasks.")

    session.add_all(
        Task(title=title, description=description, owner_id=user.id)
        for title, description in SAMPLE_TASKS
    )
    await session.commit()
    return len(SAMPLE_TASKS)


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
