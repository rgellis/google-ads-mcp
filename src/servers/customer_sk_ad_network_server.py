"""customer sk ad network server module."""

from src.services.account.customer_sk_ad_network_service import (
    register_customer_sk_ad_network_tools,
)
from src.servers import create_server

customer_sk_ad_network_server = create_server(register_customer_sk_ad_network_tools)
