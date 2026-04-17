"""Bidding and budget servers."""

from src.servers import create_server
from src.services.ad_group.ad_group_bid_modifier_service import (
    register_ad_group_bid_modifier_tools,
)
from src.services.bidding.bidding_data_exclusion_service import (
    register_bidding_data_exclusion_tools,
)
from src.services.bidding.bidding_seasonality_adjustment_service import (
    register_bidding_seasonality_adjustment_tools,
)
from src.services.bidding.bidding_strategy_service import (
    register_bidding_strategy_tools,
)
from src.services.campaign.campaign_bid_modifier_service import (
    register_campaign_bid_modifier_tools,
)

bidding_strategy_server = create_server(register_bidding_strategy_tools)
campaign_bid_modifier_server = create_server(register_campaign_bid_modifier_tools)
ad_group_bid_modifier_server = create_server(register_ad_group_bid_modifier_tools)
bidding_data_exclusion_server = create_server(register_bidding_data_exclusion_tools)
bidding_seasonality_adjustment_server = create_server(
    register_bidding_seasonality_adjustment_tools
)
