"""remarketing action server module."""

from src.services.audiences.remarketing_action_service import (
    register_remarketing_action_tools,
)
from src.servers import create_server

remarketing_action_server = create_server(register_remarketing_action_tools)
