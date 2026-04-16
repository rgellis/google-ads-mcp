"""customer service server module."""

from src.services.account.customer_service import register_customer_tools
from src.servers import create_server

customer_service_server = create_server(register_customer_tools)
