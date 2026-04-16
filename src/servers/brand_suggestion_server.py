"""brand suggestion server module."""

from src.services.planning.brand_suggestion_service import (
    register_brand_suggestion_tools,
)
from src.servers import create_server

brand_suggestion_server = create_server(register_brand_suggestion_tools)
