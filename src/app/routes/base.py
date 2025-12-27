from dataclasses import dataclass

from fastapi import APIRouter
from jinja2_fragments.fastapi import Jinja2Blocks

from src.app.config import Settings


@dataclass
class Base:
    settings = Settings()
    templates = Jinja2Blocks(directory=settings.TEMPLATE_DIR)
    router = APIRouter()


base = Base()
