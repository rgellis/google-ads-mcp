"""customer lifecycle goal server module."""

from src.services.account.customer_lifecycle_goal_service import (
    register_customer_lifecycle_goal_tools,
)
from src.servers import create_server

customer_lifecycle_goal_server = create_server(register_customer_lifecycle_goal_tools)
