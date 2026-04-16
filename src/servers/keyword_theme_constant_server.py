"""keyword theme constant server module."""

from src.services.planning.keyword_theme_constant_service import (
    register_keyword_theme_constant_tools,
)
from src.servers import create_server

keyword_theme_constant_server = create_server(register_keyword_theme_constant_tools)
