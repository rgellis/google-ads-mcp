"""product link invitation server module."""

from src.services.product_integration.product_link_invitation_service import (
    register_product_link_invitation_tools,
)
from src.servers import create_server

product_link_invitation_server = create_server(register_product_link_invitation_tools)
