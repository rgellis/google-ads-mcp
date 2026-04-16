"""campaign asset server module."""

from src.services.campaign.campaign_asset_service import register_campaign_asset_tools
from src.servers import create_server

campaign_asset_server = create_server(register_campaign_asset_tools)
