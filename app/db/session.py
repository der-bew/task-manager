from typing import Any, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings
from db.base import Base


engine = create_async_engine(settings.DATABASE_URL,  echo=settings.SQL_ECHO)

async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
           await session.rollback()
           raise e
        finally:
            await session.close()