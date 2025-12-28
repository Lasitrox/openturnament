from src.app.database import session_scope, Player
from src.app.routes import base
from fastapi import APIRouter, Form, Request


@base.router.get("/players")
async def players(request: Request):
    """Players page - display the roster of competitors."""
    async with session_scope() as session:
        players: list[Player] = (await session.execute(session.query(Player))).all()
        player_list = [{
            "name": player.name,
            "club": player.club,
            "teams": [
                team.name for team in player.teams
            ]
        } for player in players]
        return base.templates.TemplateResponse(
            "players.html",
            {
                "request": request,
                "players": player_list,
            },
        )
