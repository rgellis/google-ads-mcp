"""recommendation server module."""

from src.services.planning.recommendation_service import register_recommendation_tools
from src.servers import create_server

recommendation_server = create_server(register_recommendation_tools)
