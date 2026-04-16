"""campaign criterion server module."""

from src.services.campaign.campaign_criterion_service import (
    register_campaign_criterion_tools,
)
from src.servers import create_server

campaign_criterion_server = create_server(register_campaign_criterion_tools)
