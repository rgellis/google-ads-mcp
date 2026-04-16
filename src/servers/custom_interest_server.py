"""custom interest server module."""

from src.services.audiences.custom_interest_service import (
    register_custom_interest_tools,
)
from src.servers import create_server

custom_interest_server = create_server(register_custom_interest_tools)
