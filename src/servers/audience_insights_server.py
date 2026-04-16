"""audience insights server module."""

from src.services.audiences.audience_insights_service import (
    register_audience_insights_tools,
)
from src.servers import create_server

audience_insights_server = create_server(register_audience_insights_tools)
