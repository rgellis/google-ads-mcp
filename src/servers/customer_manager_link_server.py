"""customer manager link server module."""

from src.services.account.customer_manager_link_service import (
    register_customer_manager_link_tools,
)
from src.servers import create_server

customer_manager_link_server = create_server(register_customer_manager_link_tools)
