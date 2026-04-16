"""billing setup server module."""

from src.services.account.billing_setup_service import register_billing_setup_tools
from src.servers import create_server

billing_setup_server = create_server(register_billing_setup_tools)
