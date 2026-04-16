"""campaign lifecycle goal server module."""

from src.services.campaign.campaign_lifecycle_goal_service import (
    register_campaign_lifecycle_goal_tools,
)
from src.servers import create_server

campaign_lifecycle_goal_server = create_server(register_campaign_lifecycle_goal_tools)
