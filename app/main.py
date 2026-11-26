from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.v1 import task, auth
from core.config import settings
from db.session import engine
from db.base import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield
    finally:
        await engine.dispose()

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(task.router, prefix="/api/v1")