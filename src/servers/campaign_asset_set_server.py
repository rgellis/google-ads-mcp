"""campaign asset set server module."""

from src.services.campaign.campaign_asset_set_service import (
    register_campaign_asset_set_tools,
)
from src.servers import create_server

campaign_asset_set_server = create_server(register_campaign_asset_set_tools)
