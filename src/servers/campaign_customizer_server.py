"""campaign customizer server module."""

from src.services.campaign.campaign_customizer_service import (
    register_campaign_customizer_tools,
)
from src.servers import create_server

campaign_customizer_server = create_server(register_campaign_customizer_tools)
