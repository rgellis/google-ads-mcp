"""customer customizer server module."""

from src.services.account.customer_customizer_service import (
    register_customer_customizer_tools,
)
from src.servers import create_server

customer_customizer_server = create_server(register_customer_customizer_tools)
