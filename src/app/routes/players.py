import logging

from fastapi import Form, Request, Response
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
                    "players": players,
                    "clubs": club_list,
                    "teams": team_list,
                    "groups": group_list,
                },
            )


    @router.get("/players/{player_id}")
    async def get_player_row(player_id: int, request: Request, editable: bool = False):
        """Returns a single player row, either read-only or editable."""
        async with session_scope() as session:
            player = await session.get(
                Player,
                player_id,
                options=[
                    selectinload(Player.teams),
                    selectinload(Player.group),
                    selectinload(Player.club),
                ],
            )
            if not player:
                return Response(status_code=404)

            clubs = (await session.execute(select(Club))).scalars().all()
            teams = (await session.execute(select(Team))).scalars().all()

            template = "shared/_player_row_edit.html" if editable else "shared/_player_row.html"
            return templates.TemplateResponse(
                template,
                {
                    "request": request,
                    "player": player,
                    "clubs": clubs,
                    "teams": teams,
                },
            )

    @router.put("/api/players/{player_id}/club")
    async def update_player_club(
        player_id: int,
        request: Request,
        club_id: str = Form(None),
        new_club_name: str = Form(None),
    ):
        logger.info(f"Updating player {player_id} club to {club_id} (new: {new_club_name})")
        """HTMX endpoint to update player club."""
        async with session_scope() as session:
            player = await session.get(Player, player_id)
            if not player:
                return Response(status_code=404)

            if club_id == "new" and new_club_name:
                new_club = Club(name=new_club_name)
                session.add(new_club)
                await session.flush()
                player.club_id = new_club.id
            elif club_id == "" or club_id == "None" or club_id is None:
                player.club_id = None
            else:
                try:
                    player.club_id = int(club_id)
                except ValueError:
                    pass  # Or handle error

            await session.commit()

        # Return the read-only row after update
        return await get_player_row(player_id, request, editable=False)

