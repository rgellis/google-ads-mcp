"""user data server module."""

from src.services.data_import.user_data_service import register_user_data_tools
from src.servers import create_server

user_data_server = create_server(register_user_data_tools)
