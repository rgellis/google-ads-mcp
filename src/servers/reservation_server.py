"""reservation server module."""

from typing import Any
from fastmcp import FastMCP
from src.services.campaign.reservation_service import register_reservation_tools

reservation_server = FastMCP[Any]()
register_reservation_tools(reservation_server)
