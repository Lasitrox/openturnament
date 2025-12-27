from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.app.config import Settings

settings = Settings()
engine = create_async_engine(settings.DATABASE_URL, echo=True)
session_maker = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


@asynccontextmanager
async def session_scope() -> AsyncSession:
    session: AsyncSession = session_maker()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()
