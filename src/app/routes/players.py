from fastapi import Request
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.app.database import Player, session_scope


def add_player_routes(router, templates):
    @router.get("/players")
    async def player_routes(request: Request):
        """Players page - display the roster of competitors."""
        async with session_scope() as session:
            players: list[Player] = (await session.execute(
                select(Player).options(selectinload(Player.teams)))
            ).scalars(
            ).all()
            player_list = [{
                "group": player.group,
                "name": player.name,
                "club": player.club,
                "teams": [
                    team.name for team in player.teams
                ]
            } for player in players]
            return templates.TemplateResponse(
                "players.html",
                {
                    "request": request,
                    "players": player_list,
                },
            )
