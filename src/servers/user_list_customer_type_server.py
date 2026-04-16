"""user list customer type server module."""

from src.services.audiences.user_list_customer_type_service import (
    register_user_list_customer_type_tools,
)
from src.servers import create_server

user_list_customer_type_server = create_server(register_user_list_customer_type_tools)
