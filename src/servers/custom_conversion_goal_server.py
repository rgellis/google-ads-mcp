"""custom conversion goal server module."""

from src.services.conversions.custom_conversion_goal_service import (
    register_custom_conversion_goal_tools,
)
from src.servers import create_server

custom_conversion_goal_server = create_server(register_custom_conversion_goal_tools)
