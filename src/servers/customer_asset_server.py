"""customer asset server module."""

from src.services.assets.customer_asset_service import register_customer_asset_tools
from src.servers import create_server

customer_asset_server = create_server(register_customer_asset_tools)
