"""campaign shared set server module."""

from src.services.campaign.campaign_shared_set_service import (
    register_campaign_shared_set_tools,
)
from src.servers import create_server

campaign_shared_set_server = create_server(register_campaign_shared_set_tools)
