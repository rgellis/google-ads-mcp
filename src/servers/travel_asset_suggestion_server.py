"""travel asset suggestion server module."""

from src.services.planning.travel_asset_suggestion_service import (
    register_travel_asset_suggestion_tools,
)
from src.servers import create_server

travel_asset_suggestion_server = create_server(register_travel_asset_suggestion_tools)
