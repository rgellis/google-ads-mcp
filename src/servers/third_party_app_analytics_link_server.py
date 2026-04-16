"""third party app analytics link server module."""

from src.services.product_integration.third_party_app_analytics_link_service import (
    register_third_party_app_analytics_link_tools,
)
from src.servers import create_server

third_party_app_analytics_link_server = create_server(
    register_third_party_app_analytics_link_tools
)
