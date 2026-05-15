"""Discipline routes for the application."""

import logging

from fastapi import Form, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.app.database import Discipline, DisciplineGroup, session_scope


async def get_discipline_row(discipline_id: int, request: Request, templates, editable: bool = False):
    """Returns a single discipline row, either read-only or editable."""
    async with session_scope() as session:
        discipline = await session.get(
            Discipline,
            discipline_id,
            options=[
                selectinload(Discipline.group),
            ],
        )
        if not discipline:
            return Response(status_code=404)

        template = "shared/_discipline_row_edit.html" if editable else "shared/_discipline_row.html"
        return templates.TemplateResponse(
            template,
            {
                "request": request,
                "discipline": discipline,
            },
        )


async def update_discipline_logic(
    discipline_id: int,
    request: Request,
    templates,
    discipline_name: str | None,
):
    """HTMX logic to update discipline name."""
    logger = logging.getLogger(__name__)
    logger.info(
        "Updating discipline %s: name=%s",
        discipline_id,
        discipline_name,
    )
    async with session_scope() as session:
        discipline = await session.get(Discipline, discipline_id)
        if not discipline:
            return Response(status_code=404)

        if discipline_name:
            discipline.name = discipline_name

        await session.commit()

    # Return the read-only row after update
    return await get_discipline_row(discipline_id, request, templates, editable=False)


def add_discipline_routes(router, templates):  # noqa: C901
    """Add routes related to disciplines to the router."""
    logger = logging.getLogger(__name__)

    @router.get("/disciplines")
    async def discipline_routes(request: Request):
        """Disciplines page - display the roster of disciplines."""
        logger.info("Displaying disciplines page")
        async with session_scope() as session:
            disciplines = list(
                (
                    await session.execute(
                        select(Discipline).options(
                            selectinload(Discipline.group),
                        )
                    )
                )
                .scalars()
                .all()
            )
            groups = (await session.execute(select(DisciplineGroup))).scalars().all()

            group_list = [{"id": group.id, "name": group.name} for group in groups]

            return templates.TemplateResponse(
                "disciplines.html",
                {
                    "request": request,
                    "disciplines": disciplines,
                    "groups": group_list,
                },
            )

    @router.get("/disciplines/{discipline_id}")
    async def get_discipline_row_endpoint(discipline_id: int, request: Request, editable: bool = False):
        """Returns a single discipline row, either read-only or editable."""
        return await get_discipline_row(discipline_id, request, templates, editable)

    @router.put("/api/disciplines/{discipline_id}")
    async def update_discipline_endpoint(
        discipline_id: int,
        request: Request,
        discipline_name: str | None = Form(None),
    ):
        """HTMX endpoint to update discipline name."""
        return await update_discipline_logic(
            discipline_id,
            request,
            templates,
            discipline_name,
        )

    @router.get("/api/discipline_groups/{group_id}/edit")
    async def edit_discipline_group_title(group_id: int, request: Request):
        """Returns the editable discipline group title fragment."""
        async with session_scope() as session:
            group = await session.get(DisciplineGroup, group_id)
            if not group:
                return Response(status_code=404)
            return templates.TemplateResponse(
                "shared/_discipline_group_title_edit.html", {"request": request, "group": group}
            )

    @router.get("/api/discipline_groups/{group_id}")
    async def get_discipline_group_title(group_id: int, request: Request):  # noqa: ARG001
        """Returns the read-only discipline group title fragment."""
        async with session_scope() as session:
            group = await session.get(DisciplineGroup, group_id)
            if not group:
                return Response(status_code=404)
            return Response(
                f'<h3 id="group-title-{group.id}" class="text-xl font-semibold text-slate-700 mb-4 border-b-2 '
                f'border-teal-500 inline-block self-start cursor-pointer hover:text-teal-600" '
                f'hx-get="/api/discipline_groups/{group.id}/edit" hx-target="this" '
                f'hx-swap="outerHTML">{group.name}</h3>'
            )

    @router.put("/api/discipline_groups/{group_id}")
    async def update_discipline_group_title(group_id: int, request: Request, group_name: str = Form(...)):  # noqa: ARG001
        """Updates the discipline group title and returns the read-only fragment."""
        async with session_scope() as session:
            group = await session.get(DisciplineGroup, group_id)
            if not group:
                return Response(status_code=404)
            group.name = group_name
            await session.commit()
            return Response(
                f'<h3 id="group-title-{group.id}" class="text-xl font-semibold text-slate-700 mb-4 border-b-2 '
                f'border-teal-500 inline-block self-start cursor-pointer hover:text-teal-600" '
                f'hx-get="/api/discipline_groups/{group.id}/edit" hx-target="this" '
                f'hx-swap="outerHTML">{group.name}</h3>'
            )

    @router.post("/api/discipline_groups")
    async def add_discipline_group(request: Request, group_name: str = Form(...)):  # noqa: ARG001
        """Creates a new discipline group and reloads the disciplines page."""
        async with session_scope() as session:
            new_group = DisciplineGroup(name=group_name)
            session.add(new_group)
            await session.commit()

            return Response(headers={"HX-Refresh": "true"})

    @router.get("/api/discipline_groups/{group_id}/disciplines/add/button")
    async def get_add_discipline_button(group_id: int, request: Request):
        """Returns the button fragment for adding a new discipline to a group."""
        return templates.TemplateResponse(
            "shared/_discipline_add_button.html", {"request": request, "group_id": group_id}
        )

    @router.get("/api/discipline_groups/{group_id}/disciplines/add/form")
    async def get_add_discipline_form(group_id: int, request: Request):
        """Returns the form fragment for adding a new discipline to a group."""
        return templates.TemplateResponse(
            "shared/_discipline_add_form.html", {"request": request, "group_id": group_id}
        )

    @router.post("/api/discipline_groups/{group_id}/disciplines")
    async def add_discipline_to_group(group_id: int, request: Request, discipline_name: str = Form(...)):  # noqa: ARG001
        """Creates a new discipline in the specified group and reloads the page."""
        async with session_scope() as session:
            new_discipline = Discipline(name=discipline_name, group_id=group_id)
            session.add(new_discipline)
            await session.commit()
            return Response(headers={"HX-Refresh": "true"})

    @router.get("/api/discipline_groups/add/form")
    async def get_add_discipline_group_form(request: Request):
        """Returns the form fragment for adding a new discipline group."""
        return templates.TemplateResponse("shared/_discipline_group_add_form.html", {"request": request})

    @router.get("/api/discipline_groups/add/button")
    async def get_add_discipline_group_button(request: Request):
        """Returns the button fragment for adding a new discipline group."""
        return templates.TemplateResponse("shared/_discipline_group_add_button.html", {"request": request})
