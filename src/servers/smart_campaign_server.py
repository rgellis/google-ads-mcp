"""smart campaign server module."""

from src.services.campaign.smart_campaign_service import register_smart_campaign_tools
from src.servers import create_server

smart_campaign_server = create_server(register_smart_campaign_tools)
