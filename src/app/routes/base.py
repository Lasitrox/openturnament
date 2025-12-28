from __future__ import annotations

from fastapi import APIRouter
from jinja2_fragments.fastapi import Jinja2Blocks

from src.app.config import Settings

from .players import add_player_routes
from .root import add_root_routes


class RouterBase:
    __instance: RouterBase | None = None

    def __init__(self):
        self.settings: Settings = Settings()
        self.templates: Jinja2Blocks = Jinja2Blocks(directory=self.settings.TEMPLATE_DIR)
        self.router: APIRouter = APIRouter()

        self.create_routes()

    def create_routes(self):
        add_player_routes(self.router, self.templates)
        add_root_routes(self.router, self.templates)

    @classmethod
    def instance(cls) -> RouterBase:
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    @classmethod
    def router(cls) -> APIRouter:
        return cls.instance().router

    @classmethod
    def settings(cls) -> Settings:
        return cls.instance().settings

    @classmethod
    def templates(cls) -> Jinja2Blocks:
        return cls.instance().templates

