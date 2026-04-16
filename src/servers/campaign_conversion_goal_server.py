"""campaign conversion goal server module."""

from src.services.campaign.campaign_conversion_goal_service import (
    register_campaign_conversion_goal_tools,
)
from src.servers import create_server

campaign_conversion_goal_server = create_server(register_campaign_conversion_goal_tools)
