from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.config import Settings

settings = Settings()
engine = create_async_engine(settings.DATABASE_URL, echo=False)
session_maker = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


DataBase = declarative_base()


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
