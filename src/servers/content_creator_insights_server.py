"""content creator insights server module."""

from src.services.audiences.content_creator_insights_service import (
    register_content_creator_insights_tools,
)
from src.servers import create_server

content_creator_insights_server = create_server(register_content_creator_insights_tools)
