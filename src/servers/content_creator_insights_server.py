"""content creator insights server module."""

from typing import Any
from fastmcp import FastMCP
from src.services.audiences.content_creator_insights_service import (
    register_content_creator_insights_tools,
)

content_creator_insights_server = FastMCP[Any]()
register_content_creator_insights_tools(content_creator_insights_server)
