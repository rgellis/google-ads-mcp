"""google ads field server module."""

from src.services.metadata.google_ads_field_service import (
    register_google_ads_field_tools,
)
from src.servers import create_server

google_ads_field_server = create_server(register_google_ads_field_tools)
