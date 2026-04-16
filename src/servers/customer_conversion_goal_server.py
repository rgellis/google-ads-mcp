"""customer conversion goal server module."""

from src.services.conversions.customer_conversion_goal_service import (
    register_customer_conversion_goal_tools,
)
from src.servers import create_server

customer_conversion_goal_server = create_server(register_customer_conversion_goal_tools)
