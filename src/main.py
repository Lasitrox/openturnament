import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from data.testdata import insert_data
from logging_setup import setup_logging
from src.app.config import Settings
from src.app.database.base import DataBase
from src.app.database.base import engine as db_engine
from src.app.routes import RouterBase

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    """Context manager for FastAPI
    on app startup, and will run code after `yield` on app shutdown.
    """
    logger = logging.getLogger(__name__)

    # Create tables using the existing engine from base.py
    logger.info("Creating tables")
    async with db_engine.begin() as conn:
        # This will create all tables defined in your models if they don't exist
        await conn.run_sync(DataBase.metadata.create_all)

    # Note: Ensure insert_data() handles existing data to avoid duplicates on restart
    if settings.USE_TEST_DATABASE:
        try:
            await insert_data()
        except Exception:
            logger.exception("Error inserting test data")

    try:
        await (
            await asyncio.create_subprocess_exec(
                "tailwindcss",
                "-i",
                str(settings.STATIC_DIR / "src" / "tw.css"),
                "-o",
                str(settings.STATIC_DIR / "css" / "main.css"),
            )
        ).wait()
    except FileNotFoundError:
        try:
            await (
                await asyncio.create_subprocess_exec(
                    "./.venv/bin/tailwindcss",
                    "-i",
                    str(settings.STATIC_DIR / "src" / "tw.css"),
                    "-o",
                    str(settings.STATIC_DIR / "css" / "main.css"),
                )
            ).wait()
        except Exception:
            logger.exception("Error running tailwindcss")
    except Exception:
        logger.exception("Error running tailwindcss")

    yield

    if settings.USE_TEST_DATABASE:
        logger.info("Dropping tables")
        async with db_engine.begin() as conn:
            await conn.run_sync(DataBase.metadata.drop_all)

    await db_engine.dispose()


def get_app() -> FastAPI:
    """Create a FastAPI app with the specified settings."""
    app = FastAPI(lifespan=lifespan, **settings.fastapi_kwargs)

    app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

    app.include_router(RouterBase.router())

    return app


if __name__ == "__main__":
    setup_logging()
    logging.getLogger(__name__).info("Starting FastAPI application")
    app = get_app()
    uvicorn.run(app, host="127.0.0.1", port=8000)
