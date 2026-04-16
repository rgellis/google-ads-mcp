"""reservation server module."""

from src.services.campaign.reservation_service import register_reservation_tools
from src.servers import create_server

reservation_server = create_server(register_reservation_tools)
