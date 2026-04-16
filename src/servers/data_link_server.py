"""data link server module."""

from src.services.data_import.data_link_service import register_data_link_tools
from src.servers import create_server

data_link_server = create_server(register_data_link_tools)
