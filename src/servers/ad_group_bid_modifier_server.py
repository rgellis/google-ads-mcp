"""ad group bid modifier server module."""

from src.services.ad_group.ad_group_bid_modifier_service import (
    register_ad_group_bid_modifier_tools,
)
from src.servers import create_server

ad_group_bid_modifier_server = create_server(register_ad_group_bid_modifier_tools)
