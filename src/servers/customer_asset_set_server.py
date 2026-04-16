"""customer asset set server module."""

from src.services.assets.customer_asset_set_service import (
    register_customer_asset_set_tools,
)
from src.servers import create_server

customer_asset_set_server = create_server(register_customer_asset_set_tools)
