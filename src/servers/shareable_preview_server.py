"""shareable preview server module."""

from src.services.metadata.shareable_preview_service import (
    register_shareable_preview_tools,
)
from src.servers import create_server

shareable_preview_server = create_server(register_shareable_preview_tools)
