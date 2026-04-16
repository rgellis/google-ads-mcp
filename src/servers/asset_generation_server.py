"""asset generation server module."""

from src.services.assets.asset_generation_service import register_asset_generation_tools
from src.servers import create_server

asset_generation_server = create_server(register_asset_generation_tools)
