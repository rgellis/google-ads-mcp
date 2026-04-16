"""asset group listing group filter server module."""

from src.services.assets.asset_group_listing_group_filter_service import (
    register_asset_group_listing_group_filter_tools,
)
from src.servers import create_server

asset_group_listing_group_filter_server = create_server(
    register_asset_group_listing_group_filter_tools
)
