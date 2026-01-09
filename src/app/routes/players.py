import logging

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
            players = (
                await session.execute(
                    select(Player).options(
                        selectinload(Player.teams),
                        selectinload(Player.group),
                        selectinload(Player.club),
                    )
                )
            ).scalars().all()
            
            clubs = (await session.execute(select(Club))).scalars().all()
            teams = (await session.execute(select(Team))).scalars().all()
            groups = (await session.execute(select(Group))).scalars().all()

            return templates.TemplateResponse(
                "players.html",
                {
                    "request": request,
                    "players": players,
                    "clubs": clubs,
                    "teams": teams,
                    "groups": groups,
                },
            )

    @router.get("/players/{player_id}/name")
    async def get_player_name_cell(player_id: int, request: Request):
        """Returns a single player name cell fragment."""
        async with session_scope() as session:
            player = await session.get(Player, player_id)
            if not player:
                return Response(status_code=404)
            return templates.TemplateResponse(
                "players/player_name_cell.html",
                {"request": request, "player": player},
            )

    @router.get("/players/{player_id}/teams")
    async def get_player_team_cell(player_id: int, request: Request):
        """Returns a single player teams cell fragment."""
        async with session_scope() as session:
            player = (
                await session.execute(
                    select(Player)
                    .where(Player.id == player_id)
                    .options(selectinload(Player.teams))
                )
            ).scalar_one_or_none()
            if not player:
                return Response(status_code=404)
            return templates.TemplateResponse(
                "players/player_team_cell.html",
                {"request": request, "player": player},
            )

    @router.get("/players/{player_id}/club")
    async def get_player_club_cell(player_id: int, request: Request):
        """Returns a single player club cell fragment."""
        async with session_scope() as session:
            player = (
                await session.execute(
                    select(Player)
                    .where(Player.id == player_id)
                    .options(selectinload(Player.club))
                )
            ).scalar_one_or_none()
            if not player:
                return Response(status_code=404)
            clubs = (await session.execute(select(Club))).scalars().all()
            return templates.TemplateResponse(
                "players/player_club_cell.html",
                {"request": request, "player": player, "clubs": clubs},
            )

    @router.get("/players/{player_id}/row")
    async def get_player_row(player_id: int, request: Request):
        """Returns a single player row fragment."""
        async with session_scope() as session:
            player = (
                await session.execute(
                    select(Player).where(Player.id == player_id).options(
                        selectinload(Player.teams),
                        selectinload(Player.group),
                        selectinload(Player.club),
                    )
                )
            ).scalar_one_or_none()

            if not player:
                return Response(status_code=404)

            clubs = (await session.execute(select(Club))).scalars().all()
            teams = (await session.execute(select(Team))).scalars().all()

            return templates.TemplateResponse(
                "players/players_row.html",
                {
                    "request": request,
                    "player": player,
                    "clubs": clubs,
                    "teams": teams,
                },
            )

    @router.post("/players/{player_id}/club/dispatch")
    async def dispatch_club_action(player_id: int, request: Request, club_id: str = Form(...)):
        """Unified endpoint to handle selection changes."""
        if club_id == "new":
            logger.info(f"Displaying new club form for player {player_id}")
            return Response(
                content=f"""
                                <td class="py-3 px-4 text-left whitespace-nowrap" hx-disinherit="*">
                                    <div class="flex gap-2">
                                        <input type="text" name="new_club_name" class="border rounded px-2 py-1 w-32" placeholder="Club name...">
                                        <button hx-post="/players/{player_id}/club"
                                                hx-include="closest td"
                                                hx-target="closest td"
                                                hx-swap="outerHTML"
                                                class="text-teal-600 font-bold">✓</button>
                                        <button hx-get="/players/{player_id}/club" hx-target="closest td" hx-swap="outerHTML" class="text-gray-400">✕</button>
                                    </div>
                                </td>
                            """
            )
        
        async with session_scope() as session:
            player = await session.get(Player, player_id)
            if player:
                try:
                    player.club_id = int(club_id) if club_id and club_id.isdigit() else None
                except ValueError:
                    player.club_id = None
                await session.commit()
                return await get_player_club_cell(player_id, request)
                
        return Response(status_code=400, content="Invalid request")

    @router.put("/players/{player_id}/club")
    async def update_player_club(player_id: int, club_id: int | None = Form(None)):
        logger.info(f"Updating player {player_id} club to {club_id}")
        """HTMX endpoint to update player club."""
        async with session_scope() as session:
            player = await session.get(Player, player_id)
            if player:
                player.club_id = int(club_id)
                await session.commit()
        return Response(status_code=204)

    @router.post("/players/{player_id}/club")
    async def create_club_and_assign(
        player_id: int, request: Request, new_club_name: str = Form(...)
    ):
        """Creates a new club, assigns it to the player, and returns the updated dropdown."""
        async with session_scope() as session:
            # Check if club already exists
            existing_club = (await session.execute(
                select(Club).where(Club.name == new_club_name)
            )).scalar_one_or_none()
            
            if existing_club:
                new_club = existing_club
            else:
                # 1. Create the club
                new_club = Club(name=new_club_name)
                session.add(new_club)
                await session.flush()  # Get the ID

            # 2. Update the player
            player = await session.get(Player, player_id)
            if player:
                player.club_id = new_club.id

            await session.commit()

            # Return the updated cell
            return await get_player_club_cell(player_id, request)
