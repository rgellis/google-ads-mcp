"""campaign draft server module."""

from src.services.campaign.campaign_draft_service import register_campaign_draft_tools
from src.servers import create_server

campaign_draft_server = create_server(register_campaign_draft_tools)
