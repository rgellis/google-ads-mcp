"""search server module."""

from src.services.metadata.search_service import register_search_tools
from src.servers import create_server

search_server = create_server(register_search_tools)
