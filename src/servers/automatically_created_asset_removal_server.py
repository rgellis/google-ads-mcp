"""automatically created asset removal server module."""

from src.services.campaign.automatically_created_asset_removal_service import (
    register_automatically_created_asset_removal_tools,
)
from src.servers import create_server

automatically_created_asset_removal_server = create_server(
    register_automatically_created_asset_removal_tools
)
