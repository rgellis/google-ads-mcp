"""product link server module."""

from src.services.product_integration.product_link_service import (
    register_product_link_tools,
)
from src.servers import create_server

product_link_server = create_server(register_product_link_tools)
