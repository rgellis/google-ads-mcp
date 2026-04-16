"""local services lead server module."""

from src.services.data_import.local_services_lead_service import (
    register_local_services_lead_tools,
)
from src.servers import create_server

local_services_lead_server = create_server(register_local_services_lead_tools)
