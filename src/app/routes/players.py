from fastapi import Request
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.app.database import Club, Group, Player, Team, session_scope


def add_player_routes(router, templates):
    @router.get("/players")
    async def player_routes(request: Request):
        """Players page - display the roster of competitors."""
        async with session_scope() as session:
            players: list[Player] = (
                (
                    await session.execute(
                        select(Player).options(
                            selectinload(Player.teams),
                            selectinload(Player.group),
                            selectinload(Player.club),
                        )
                    )
                )
                .scalars()
                .all()
            )
            player_list = [
                {
                    "group": player.group.id,
                    "name": player.name,
                    "club": player.club.id,
                    "teams": [team.id for team in player.teams],
                }
                for player in players
            ]
            club_list = [
                {"id": club.id, "name": club.name}
                for club in (await session.execute(select(Club))).scalars().all()
            ]
            team_list = [
                {"id": team.id, "name": team.name}
                for team in (await session.execute(select(Team))).scalars().all()
            ]
            group_list = [
                {"id": group.id, "name": group.name}
                for group in (await session.execute(select(Group))).scalars().all()
            ]
            return templates.TemplateResponse(
                "players.html",
                {
                    "request": request,
                    "players": player_list,
                    "clubs": club_list,
                    "teams": team_list,
                    "groups": group_list,
                },
            )
