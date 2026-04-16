"""google ads server module."""

from src.services.metadata.google_ads_service import register_google_ads_tools
from src.servers import create_server

google_ads_server = create_server(register_google_ads_tools)
