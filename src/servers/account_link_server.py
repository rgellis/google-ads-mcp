"""account link server module."""

from src.services.account.account_link_service import register_account_link_tools
from src.servers import create_server

account_link_server = create_server(register_account_link_tools)
