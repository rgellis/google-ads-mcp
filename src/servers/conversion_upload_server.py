"""conversion upload server module."""

from src.services.conversions.conversion_upload_service import (
    register_conversion_upload_tools,
)
from src.servers import create_server

conversion_upload_server = create_server(register_conversion_upload_tools)
