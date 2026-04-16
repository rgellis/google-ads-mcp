"""incentive server module."""

from typing import Any
from fastmcp import FastMCP
from src.services.account.incentive_service import register_incentive_tools

incentive_server = FastMCP[Any]()
register_incentive_tools(incentive_server)
