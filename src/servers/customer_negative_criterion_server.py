"""customer negative criterion server module."""

from src.services.targeting.customer_negative_criterion_service import (
    register_customer_negative_criterion_tools,
)
from src.servers import create_server

customer_negative_criterion_server = create_server(
    register_customer_negative_criterion_tools
)
