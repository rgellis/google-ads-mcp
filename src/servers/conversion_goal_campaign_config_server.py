"""conversion goal campaign config server module."""

from src.services.conversions.conversion_goal_campaign_config_service import (
    register_conversion_goal_campaign_config_tools,
)
from src.servers import create_server

conversion_goal_campaign_config_server = create_server(
    register_conversion_goal_campaign_config_tools
)
