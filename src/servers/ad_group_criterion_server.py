"""ad group criterion server module."""

from src.services.ad_group.ad_group_criterion_service import (
    register_ad_group_criterion_tools,
)
from src.servers import create_server

ad_group_criterion_server = create_server(register_ad_group_criterion_tools)
