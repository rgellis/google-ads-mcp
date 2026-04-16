"""conversion server module."""

from src.services.conversions.conversion_service import register_conversion_tools
from src.servers import create_server

conversion_server = create_server(register_conversion_tools)
