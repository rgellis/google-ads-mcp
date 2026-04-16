"""customer client link server module."""

from src.services.account.customer_client_link_service import (
    register_customer_client_link_tools,
)
from src.servers import create_server

customer_client_link_server = create_server(register_customer_client_link_tools)
