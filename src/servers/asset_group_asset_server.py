"""asset group asset server module."""

from src.services.assets.asset_group_asset_service import (
    register_asset_group_asset_tools,
)
from src.servers import create_server

asset_group_asset_server = create_server(register_asset_group_asset_tools)
