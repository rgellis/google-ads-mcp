"""customizer sdk server module."""

from src.services.shared.customizer_attribute_service import (
    register_customizer_attribute_tools,
)
from src.servers import create_server

customizer_sdk_server = create_server(register_customizer_attribute_tools)
