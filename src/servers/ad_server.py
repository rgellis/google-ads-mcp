"""ad server module."""

from src.services.ad_group.ad_service import register_ad_tools
from src.servers import create_server

ad_server = create_server(register_ad_tools)
