from src.app.database import get_db
from src.app.routes import base
from fastapi import APIRouter, Form, Request


@base.router.get("/players")
async def players(request: Request):
    """Players page - display the roster of competitors."""
    async with get_db() as session:
        db.
        return base.templates.TemplateResponse(
            "players.html",
            {
                "request": request,
                "players": all_players,
            },
        )
