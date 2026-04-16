"""customer label server module."""

from src.services.account.customer_label_service import register_customer_label_tools
from src.servers import create_server

customer_label_server = create_server(register_customer_label_tools)
