import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import Settings
from app.routes import base
from src.logging_setup import setup_logging

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    """Context manager for FastAP
    on app startup, and will run code after `yeld` on app shutdown.
    """
    logger = logging.getLogger(__name__)
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


def get_app() -> FastAPI:
    """Create a FastAPI app with the specified settings."""
    app = FastAPI(lifespan=lifespan, **settings.fastapi_kwargs)

    app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

    app.include_router(base.router)

    return app


if __name__ == "__main__":
    setup_logging()
    logging.getLogger(__name__).info("Starting FastAPI application")
    app = get_app()
    uvicorn.run(app, host="127.0.0.1", port=8000)
