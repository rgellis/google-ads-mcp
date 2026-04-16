"""campaign bid modifier server module."""

from src.services.campaign.campaign_bid_modifier_service import (
    register_campaign_bid_modifier_tools,
)
from src.servers import create_server

campaign_bid_modifier_server = create_server(register_campaign_bid_modifier_tools)
