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

    @router.post("/players/{player_id}/club/dispatch")
    async def dispatch_club_action(player_id: int, club_id: str = Form(...)):
        """Unified endpoint to handle selection changes."""
        if club_id == "new":
            logger.info(f"Displaying new club form for player {player_id}")
            return Response(
                content=f"""
                                <div class="flex gap-2">
                                    <input type="text" name="new_club_name" class="border rounded px-2 py-1 w-32" placeholder="Club name...">
                                    <button hx-post="/players/{player_id}/club"
                                            hx-include="closest td"
                                            hx-target="closest td"
                                            class="text-teal-600 font-bold">✓</button>
                                    <button hx-get="/players" hx-target="body" class="text-gray-400">✕</button>
                                </div>
                            """
            )
        return Response(status_code=400, content={"message": "Invalid club ID"})

    @router.put("/api/players/{player_id}/club")
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
            # 1. Create the club
            new_club = Club(name=new_club_name)
            session.add(new_club)
            await session.flush()  # Get the ID

            # 2. Update the player
            player = await session.get(Player, player_id)
            if player:
                player.club_id = new_club.id

            await session.commit()

            # 3. Get all clubs to re-render the select
            clubs = (await session.execute(select(Club))).scalars().all()

            # Return the select fragment (matching the one in players.html)
            # In a real app, you might move this to a shared jinja macro
            options = "".join(
                [
                    f'<option value="{c.id}" {"selected" if c.id == new_club.id else ""}>{c.name}</option>'
                    for c in clubs
                ]
            )

            return Response(
                content=f"""
                        <select name="club_id" class="bg-transparent border border-slate-300 rounded px-2 py-1 focus:outline-none focus:border-teal-500"
                                hx-put="/players/{player_id}/club" hx-target="this" hx-swap="outerHTML">
                            {options}
                            <option disabled>──────────</option>
                            <option value="new" hx-get="/players/{player_id}/club/new" hx-target="closest td" hx-swap="innerHTML">+ Add New Club...</option>
                        </select>
                    """
            )
