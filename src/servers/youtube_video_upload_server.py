"""YouTube video upload server module."""

from typing import Any

from fastmcp import FastMCP

from src.services.assets.youtube_video_upload_service import (
    register_youtube_video_upload_tools,
)

youtube_video_upload_server = FastMCP[Any]()
register_youtube_video_upload_tools(youtube_video_upload_server)
