"""Campaign goal config server module."""

from typing import Any
from fastmcp import FastMCP
from src.services.campaign.campaign_goal_config_service import (
    register_campaign_goal_config_tools,
)

campaign_goal_config_server = FastMCP[Any]()
register_campaign_goal_config_tools(campaign_goal_config_server)
