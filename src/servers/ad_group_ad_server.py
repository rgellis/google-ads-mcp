"""ad group ad server module."""

from src.services.ad_group.ad_group_ad_service import register_ad_group_ad_tools
from src.servers import create_server

ad_group_ad_server = create_server(register_ad_group_ad_tools)
