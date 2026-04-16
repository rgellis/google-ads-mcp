"""campaign label server module."""

from src.services.campaign.campaign_label_service import register_campaign_label_tools
from src.servers import create_server

campaign_label_server = create_server(register_campaign_label_tools)
