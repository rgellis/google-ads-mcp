"""ad group asset server module."""

from src.services.ad_group.ad_group_asset_service import register_ad_group_asset_tools
from src.servers import create_server

ad_group_asset_server = create_server(register_ad_group_asset_tools)
