"""bidding seasonality adjustment server module."""

from src.services.bidding.bidding_seasonality_adjustment_service import (
    register_bidding_seasonality_adjustment_tools,
)
from src.servers import create_server

bidding_seasonality_adjustment_server = create_server(
    register_bidding_seasonality_adjustment_tools
)
