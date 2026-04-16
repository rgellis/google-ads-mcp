"""keyword server module."""

from src.services.ad_group.keyword_service import register_keyword_tools
from src.servers import create_server

keyword_server = create_server(register_keyword_tools)
