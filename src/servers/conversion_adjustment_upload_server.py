"""conversion adjustment upload server module."""

from src.services.conversions.conversion_adjustment_upload_service import (
    register_conversion_adjustment_upload_tools,
)
from src.servers import create_server

conversion_adjustment_upload_server = create_server(
    register_conversion_adjustment_upload_tools
)
