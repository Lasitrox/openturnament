import logging
from typing import Optional

from fastapi import Form, Request, Response  # Added Form
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.app.database import Club, Group, Player, Team, session_scope


def add_player_routes(router, templates):
    logger = logging.getLogger(__name__)
    @router.get("/players")
    async def player_routes(request: Request):
        """Players page - display the roster of competitors."""
        logger.info("Displaying players page")
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
                    "id": player.id,
                    "group": player.group.id if player.group else None,
                    "name": player.name,
                    "club": player.club.id if player.club else None,
                    "teams": [team.id for team in player.teams] if player.teams else [],
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

    @router.put("/api/players/{player_id}/club")
    async def update_player_club(player_id: int, club_id: Optional[int] = Form(None)):
        logger.info(
            f"Updating player {player_id} club to {club_id}"
        )
        """HTMX endpoint to update player club."""
        async with session_scope() as session:
            try:
                player = await session.get(Player, player_id)
                if player:
                    player.club_id = club_id
                    return Response(status_code=200)

                return Response(status_code=404)
            except Exception:
                logger.exception("Error updating player club")
                return Response(status_code=400)

            # HTMX expects a response.
            # Since we used hx-swap="none", we can just return a 204 No Content
