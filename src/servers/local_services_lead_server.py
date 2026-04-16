"""local services lead server module."""

from typing import Any
from fastmcp import FastMCP
from src.services.data_import.local_services_lead_service import (
    register_local_services_lead_tools,
)

local_services_lead_server = FastMCP[Any]()
register_local_services_lead_tools(local_services_lead_server)
