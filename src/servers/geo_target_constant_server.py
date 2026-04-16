"""geo target constant server module."""

from src.services.targeting.geo_target_constant_service import (
    register_geo_target_constant_tools,
)
from src.servers import create_server

geo_target_constant_server = create_server(register_geo_target_constant_tools)
