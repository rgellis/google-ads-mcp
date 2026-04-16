"""asset group signal server module."""

from src.services.assets.asset_group_signal_service import (
    register_asset_group_signal_tools,
)
from src.servers import create_server

asset_group_signal_server = create_server(register_asset_group_signal_tools)
