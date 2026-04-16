"""ad parameter server module."""

from src.services.ad_group.ad_parameter_service import register_ad_parameter_tools
from src.servers import create_server

ad_parameter_server = create_server(register_ad_parameter_tools)
