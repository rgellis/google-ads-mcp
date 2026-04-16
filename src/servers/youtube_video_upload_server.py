"""youtube video upload server module."""

from src.services.assets.youtube_video_upload_service import (
    register_youtube_video_upload_tools,
)
from src.servers import create_server

youtube_video_upload_server = create_server(register_youtube_video_upload_tools)
