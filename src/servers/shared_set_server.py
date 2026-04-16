"""shared set server module."""

from src.services.shared.shared_set_service import register_shared_set_tools
from src.servers import create_server

shared_set_server = create_server(register_shared_set_tools)
