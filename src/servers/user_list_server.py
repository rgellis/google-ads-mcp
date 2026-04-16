"""user list server module."""

from src.services.audiences.user_list_service import register_user_list_tools
from src.servers import create_server

user_list_server = create_server(register_user_list_tools)
