"""asset server module."""

from src.services.assets.asset_service import register_asset_tools
from src.servers import create_server

asset_server = create_server(register_asset_tools)
