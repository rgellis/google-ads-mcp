"""asset group server module."""

from src.services.assets.asset_group_service import register_asset_group_tools
from src.servers import create_server

asset_group_server = create_server(register_asset_group_tools)
