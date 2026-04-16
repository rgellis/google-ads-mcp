"""incentive server module."""

from src.services.account.incentive_service import register_incentive_tools
from src.servers import create_server

incentive_server = create_server(register_incentive_tools)
