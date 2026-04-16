"""budget server module."""

from src.services.bidding.budget_service import register_budget_tools
from src.servers import create_server

budget_server = create_server(register_budget_tools)
