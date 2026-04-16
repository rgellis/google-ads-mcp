"""campaign server module."""

from src.services.campaign.campaign_service import register_campaign_tools
from src.servers import create_server

campaign_server = create_server(register_campaign_tools)
