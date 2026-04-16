"""label server module."""

from src.services.shared.label_service import register_label_tools
from src.servers import create_server

label_server = create_server(register_label_tools)
