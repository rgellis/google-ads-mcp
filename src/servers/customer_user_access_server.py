"""customer user access server module."""

from src.services.account.customer_user_access_service import (
    register_customer_user_access_tools,
)
from src.servers import create_server

customer_user_access_server = create_server(register_customer_user_access_tools)
