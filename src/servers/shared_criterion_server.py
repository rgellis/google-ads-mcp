"""shared criterion server module."""

from src.services.shared.shared_criterion_service import register_shared_criterion_tools
from src.servers import create_server

shared_criterion_server = create_server(register_shared_criterion_tools)
