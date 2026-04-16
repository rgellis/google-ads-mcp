"""custom audience server module."""

from src.services.audiences.custom_audience_service import (
    register_custom_audience_tools,
)
from src.servers import create_server

custom_audience_server = create_server(register_custom_audience_tools)
