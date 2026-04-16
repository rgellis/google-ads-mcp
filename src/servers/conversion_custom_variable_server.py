"""conversion custom variable server module."""

from src.services.conversions.conversion_custom_variable_service import (
    register_conversion_custom_variable_tools,
)
from src.servers import create_server

conversion_custom_variable_server = create_server(
    register_conversion_custom_variable_tools
)
