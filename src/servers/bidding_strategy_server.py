"""bidding strategy server module."""

from src.services.bidding.bidding_strategy_service import (
    register_bidding_strategy_tools,
)
from src.servers import create_server

bidding_strategy_server = create_server(register_bidding_strategy_tools)
