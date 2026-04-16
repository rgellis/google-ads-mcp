"""bidding data exclusion server module."""

from src.services.bidding.bidding_data_exclusion_service import (
    register_bidding_data_exclusion_tools,
)
from src.servers import create_server

bidding_data_exclusion_server = create_server(register_bidding_data_exclusion_tools)
