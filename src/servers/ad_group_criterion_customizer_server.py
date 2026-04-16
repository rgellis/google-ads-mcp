"""ad group criterion customizer server module."""

from src.services.ad_group.ad_group_criterion_customizer_service import (
    register_ad_group_criterion_customizer_tools,
)
from src.servers import create_server

ad_group_criterion_customizer_server = create_server(
    register_ad_group_criterion_customizer_tools
)
