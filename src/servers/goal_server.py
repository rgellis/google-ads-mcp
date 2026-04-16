"""goal server module."""

from src.services.account.goal_service import register_goal_tools
from src.servers import create_server

goal_server = create_server(register_goal_tools)
