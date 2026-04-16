"""audience server module."""

from src.services.audiences.audience_service import register_audience_tools
from src.servers import create_server

audience_server = create_server(register_audience_tools)
