"""Base router module for the application."""

from __future__ import annotations

from fastapi import APIRouter
from jinja2_fragments.fastapi import Jinja2Blocks

from src.config import Settings

from .players import add_player_routes
from .root import add_root_routes


class RouterBase:
    """Base class for managing application routes and templates."""

    __instance: RouterBase | None = None

    def __init__(self):
        """Initialize the router base with settings and templates."""
        self.settings: Settings = Settings()
        self.templates: Jinja2Blocks = Jinja2Blocks(
            directory=self.settings.TEMPLATE_DIR
        )
        self.router: APIRouter = APIRouter()

        self.create_routes()

    def create_routes(self):
        """Create and add routes to the router."""
        add_player_routes(self.router, self.templates)
        add_root_routes(self.router, self.templates)

    @classmethod
    def instance(cls) -> RouterBase:
        """Get the singleton instance of RouterBase."""
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    @classmethod
    def router(cls) -> APIRouter:
        """Get the APIRouter instance."""
        return cls.instance().router

    @classmethod
    def settings(cls) -> Settings:
        """Get the application settings."""
        return cls.instance().settings

    @classmethod
    def templates(cls) -> Jinja2Blocks:
        """Get the Jinja2 templates instance."""
        return cls.instance().templates
