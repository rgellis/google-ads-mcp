"""Asset management servers."""

from src.servers import create_server
from src.services.ad_group.ad_group_asset_service import register_ad_group_asset_tools
from src.services.ad_group.ad_group_asset_set_service import (
    register_ad_group_asset_set_tools,
)
from src.services.assets.asset_generation_service import register_asset_generation_tools
from src.services.assets.asset_group_asset_service import (
    register_asset_group_asset_tools,
)
from src.services.assets.asset_group_listing_group_filter_service import (
    register_asset_group_listing_group_filter_tools,
)
from src.services.assets.asset_group_service import register_asset_group_tools
from src.services.assets.asset_group_signal_service import (
    register_asset_group_signal_tools,
)
from src.services.assets.asset_service import register_asset_tools
from src.services.assets.asset_set_asset_service import register_asset_set_asset_tools
from src.services.assets.asset_set_service import register_asset_set_tools
from src.services.assets.customer_asset_service import register_customer_asset_tools
from src.services.assets.customer_asset_set_service import (
    register_customer_asset_set_tools,
)
from src.services.assets.youtube_video_upload_service import (
    register_youtube_video_upload_tools,
)
from src.services.campaign.automatically_created_asset_removal_service import (
    register_automatically_created_asset_removal_tools,
)
from src.services.campaign.campaign_asset_service import register_campaign_asset_tools
from src.services.campaign.campaign_asset_set_service import (
    register_campaign_asset_set_tools,
)

asset_server = create_server(register_asset_tools)
asset_group_server = create_server(register_asset_group_tools)
asset_group_asset_server = create_server(register_asset_group_asset_tools)
asset_group_signal_server = create_server(register_asset_group_signal_tools)
asset_group_listing_group_filter_server = create_server(
    register_asset_group_listing_group_filter_tools
)
asset_set_server = create_server(register_asset_set_tools)
asset_set_asset_server = create_server(register_asset_set_asset_tools)
ad_group_asset_server = create_server(register_ad_group_asset_tools)
ad_group_asset_set_server = create_server(register_ad_group_asset_set_tools)
campaign_asset_server = create_server(register_campaign_asset_tools)
campaign_asset_set_server = create_server(register_campaign_asset_set_tools)
customer_asset_server = create_server(register_customer_asset_tools)
customer_asset_set_server = create_server(register_customer_asset_set_tools)
asset_generation_server = create_server(register_asset_generation_tools)
automatically_created_asset_removal_server = create_server(
    register_automatically_created_asset_removal_tools
)
youtube_video_upload_server = create_server(register_youtube_video_upload_tools)
