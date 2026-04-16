"""campaign goal config server module."""

from src.services.campaign.campaign_goal_config_service import (
    register_campaign_goal_config_tools,
)
from src.servers import create_server

campaign_goal_config_server = create_server(register_campaign_goal_config_tools)
