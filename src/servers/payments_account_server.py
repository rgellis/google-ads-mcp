"""payments account server module."""

from src.services.account.payments_account_service import (
    register_payments_account_tools,
)
from src.servers import create_server

payments_account_server = create_server(register_payments_account_tools)
