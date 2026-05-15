"""Player routes for the application."""

import logging
from contextlib import suppress
from typing import Annotated

from fastapi import Form, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.app.database import Club, Group, Player, Team, session_scope


async def get_player_row(player_id: int, request: Request, templates, editable: bool = False):
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


async def update_player_logic(
    player_id: int,
    request: Request,
    templates,
    player_name: str | None,
    club_id: str | None,
    new_club_name: str | None,
    team_ids: list[str] | None,
    new_team_name: str | None,
):
    """HTMX logic to update player name, club and teams."""
    logger = logging.getLogger(__name__)
    logger.info(
        "Updating player %s: name=%s, club=%s (new: %s), teams=%s (new: %s)",
        player_id,
        player_name,
        club_id,
        new_club_name,
        team_ids,
        new_team_name,
    )
    async with session_scope() as session:
        player = await session.get(Player, player_id, options=[selectinload(Player.teams)])
        if not player:
            return Response(status_code=404)

        if player_name:
            player.name = player_name

        if club_id == "new" and new_club_name:
            new_club = Club(name=new_club_name)
            session.add(new_club)
            await session.flush()
            player.club_id = new_club.id
        elif club_id in ("", "None", None):
            player.club_id = None
        else:
            with suppress(ValueError):
                player.club_id = int(club_id)

        # Update teams
        team_ids = team_ids or []
        is_new_team = "new" in team_ids and new_team_name
        selected_team_ids = [int(tid) for tid in team_ids if tid.isdigit()]

        if selected_team_ids or is_new_team:
            teams = (await session.execute(select(Team).where(Team.id.in_(selected_team_ids)))).scalars().all()
            player_teams = list(teams)

            if is_new_team:
                new_team = Team(name=new_team_name)
                session.add(new_team)
                await session.flush()
                player_teams.append(new_team)

            player.teams = player_teams
        else:
            player.teams = []

        await session.commit()

    # Return the read-only row after update
    return await get_player_row(player_id, request, templates, editable=False)


def add_player_routes(router, templates):  # noqa: C901
    """Add routes related to players to the router."""
    logger = logging.getLogger(__name__)

    @router.get("/players")
    async def player_routes(request: Request):
        """Players page - display the roster of competitors."""
        logger.info("Displaying players page")
        async with session_scope() as session:
            players: list[Player] = list(
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
            clubs = (await session.execute(select(Club))).scalars().all()
            teams = (await session.execute(select(Team))).scalars().all()
            groups = (await session.execute(select(Group))).scalars().all()

            club_list = [{"id": club.id, "name": club.name} for club in clubs]
            team_list = [{"id": team.id, "name": team.name} for team in teams]
            group_list = [{"id": group.id, "name": group.name} for group in groups]

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
    async def get_player_row_endpoint(player_id: int, request: Request, editable: bool = False):
        """Returns a single player row, either read-only or editable."""
        return await get_player_row(player_id, request, templates, editable)

    @router.put("/api/players/{player_id}")
    async def update_player_club_endpoint(
        player_id: int,
        request: Request,
        player_name: str | None = Form(None),
        club_id: Annotated[str | None, Form()] = None,
        new_club_name: Annotated[str | None, Form()] = None,
        team_ids: Annotated[list[str] | None, Form()] = None,
        new_team_name: Annotated[str | None, Form()] = None,
    ):
        """HTMX endpoint to update player name, club and teams."""
        return await update_player_logic(
            player_id,
            request,
            templates,
            player_name,
            club_id,
            new_club_name,
            team_ids,
            new_team_name,
        )

    @router.get("/api/groups/{group_id}/edit")
    async def edit_group_title(group_id: int, request: Request):
        """Returns the editable group title fragment."""
        async with session_scope() as session:
            group = await session.get(Group, group_id)
            if not group:
                return Response(status_code=404)
            return templates.TemplateResponse("shared/_group_title_edit.html", {"request": request, "group": group})

    @router.get("/api/groups/{group_id}")
    async def get_group_title(group_id: int, request: Request):  # noqa: ARG001
        """Returns the read-only group title fragment."""
        async with session_scope() as session:
            group = await session.get(Group, group_id)
            if not group:
                return Response(status_code=404)
            return Response(
                f'<h3 id="group-title-{group.id}" class="text-xl font-semibold text-slate-700 mb-4 border-b-2 '
                f'border-teal-500 inline-block self-start cursor-pointer hover:text-teal-600" '
                f'hx-get="/api/groups/{group.id}/edit" hx-target="this" hx-swap="outerHTML">{group.name}</h3>'
            )

    @router.put("/api/groups/{group_id}")
    async def update_group_title(group_id: int, request: Request, group_name: str = Form(...)):  # noqa: ARG001
        """Updates the group title and returns the read-only fragment."""
        async with session_scope() as session:
            group = await session.get(Group, group_id)
            if not group:
                return Response(status_code=404)
            group.name = group_name
            await session.commit()
            return Response(
                f'<h3 id="group-title-{group.id}" class="text-xl font-semibold text-slate-700 mb-4 border-b-2 '
                f'border-teal-500 inline-block self-start cursor-pointer hover:text-teal-600" '
                f'hx-get="/api/groups/{group.id}/edit" hx-target="this" hx-swap="outerHTML">{group.name}</h3>'
            )

    @router.post("/api/groups")
    async def add_group(request: Request, group_name: str = Form(...)):  # noqa: ARG001
        """Creates a new group and reloads the players page (or returns the new group fragment)."""
        async with session_scope() as session:
            new_group = Group(name=group_name)
            session.add(new_group)
            await session.commit()

            return Response(headers={"HX-Refresh": "true"})

    @router.get("/api/groups/{group_id}/players/add/button")
    async def get_add_player_button(group_id: int, request: Request):
        """Returns the button fragment for adding a new player to a group."""
        return templates.TemplateResponse("shared/_player_add_button.html", {"request": request, "group_id": group_id})

    @router.get("/api/groups/{group_id}/players/add/form")
    async def get_add_player_form(group_id: int, request: Request):
        """Returns the form fragment for adding a new player to a group."""
        return templates.TemplateResponse("shared/_player_add_form.html", {"request": request, "group_id": group_id})

    @router.post("/api/groups/{group_id}/players")
    async def add_player_to_group(group_id: int, request: Request, player_name: str = Form(...)):  # noqa: ARG001
        """Creates a new player in the specified group and reloads the page."""
        async with session_scope() as session:
            new_player = Player(name=player_name, group_id=group_id)
            session.add(new_player)
            await session.commit()
            return Response(headers={"HX-Refresh": "true"})

    @router.get("/api/groups/add/form")
    async def get_add_group_form(request: Request):
        """Returns the form fragment for adding a new group."""
        return templates.TemplateResponse("shared/_group_add_form.html", {"request": request})

    @router.get("/api/groups/add/button")
    async def get_add_group_button(request: Request):
        """Returns the button fragment for adding a new group."""
        return templates.TemplateResponse("shared/_group_add_button.html", {"request": request})
