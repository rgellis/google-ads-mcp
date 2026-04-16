"""invoice server module."""

from src.services.account.invoice_service import register_invoice_tools
from src.servers import create_server

invoice_server = create_server(register_invoice_tools)
