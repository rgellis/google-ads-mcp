"""campaign group server module."""

from src.services.campaign.campaign_group_service import register_campaign_group_tools
from src.servers import create_server

campaign_group_server = create_server(register_campaign_group_tools)
