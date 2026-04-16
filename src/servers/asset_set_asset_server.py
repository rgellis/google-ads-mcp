"""asset set asset server module."""

from src.services.assets.asset_set_asset_service import register_asset_set_asset_tools
from src.servers import create_server

asset_set_asset_server = create_server(register_asset_set_asset_tools)
