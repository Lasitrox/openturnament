from fastapi import Request

from src.app.database import Player, session_scope


def player_routes(router, templates):
    @router.get("/players")
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
            return templates.TemplateResponse(
                "players.html",
                {
                    "request": request,
                    "players": player_list,
                },
            )
