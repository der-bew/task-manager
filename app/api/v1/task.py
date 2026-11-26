from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select

from api.deps import AdminUser, CurrentUser, DBSession, PaginationDep
from models.task import Task
from schemas.pagination import PaginatedResponse
from schemas.task import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate, db: DBSession, current_user: CurrentUser):
    task = Task(**task_data.model_dump(), owner_id=current_user.id)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task

@router.get("/", response_model=PaginatedResponse[TaskRead])
async def list_my_tasks(pagination: PaginationDep, db: DBSession, current_user: CurrentUser):
    # count the total item for current user
    count_query = select(func.count()).select_from(Task).where(Task.owner_id == current_user.id)
    total = (await db.execute(count_query)).scalar_one()

    # fetch the paginated items
    query = (
        select(Task)
        .where(Task.owner_id == current_user.id)
        .order_by(Task.created_at.desc(), Task.id.desc())
        .offset(pagination.offset)
        .limit(pagination.size)
    )
    items = (await db.execute(query)).scalars().all()
    return PaginatedResponse.create(items=items, total=total, params=pagination)

@router.get("/all", response_model=PaginatedResponse[TaskRead])
async def list_all_tasks_admin(pagination: PaginationDep, db: DBSession, current_user: AdminUser):
    count_query = select(func.count()).select_from(Task)
    total = (await db.execute(count_query)).scalar_one()
    query = select(Task).order_by(Task.created_at.desc(), Task.id.desc()).offset(pagination.offset).limit(pagination.size)
    items = (await db.execute(query)).scalars().all()
    return PaginatedResponse.create(items=items, total=total, params=pagination)

@router.get("/{task_id}", response_model=TaskRead)
async def get_task(task_id: int, db: DBSession, current_user: CurrentUser):
    query = select(Task).where(Task.id == task_id)
    task = (await db.execute(query)).scalars().first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the owner of this task")
    return task

@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(task_id: int, task_data: TaskUpdate, db: DBSession, current_user: CurrentUser):
    query = select(Task).where(Task.id == task_id)
    task = (await db.execute(query)).scalars().first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    # Resource-level authorization check
    if task.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the owner of this task")

    for key, value in task_data.model_dump(exclude_unset=True).items():
        setattr(task, key, value)

    await db.commit()
    await db.refresh(task)
    return task