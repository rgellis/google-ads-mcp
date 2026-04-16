"""recommendation subscription server module."""

from src.services.planning.recommendation_subscription_service import (
    register_recommendation_subscription_tools,
)
from src.servers import create_server

recommendation_subscription_server = create_server(
    register_recommendation_subscription_tools
)
