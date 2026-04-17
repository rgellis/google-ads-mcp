"""Targeting and audience servers."""

from src.servers import create_server
from src.services.ad_group.ad_group_criterion_service import (
    register_ad_group_criterion_tools,
)
from src.services.audiences.audience_service import register_audience_tools
from src.services.audiences.custom_audience_service import (
    register_custom_audience_tools,
)
from src.services.audiences.custom_interest_service import (
    register_custom_interest_tools,
)
from src.services.audiences.user_list_service import register_user_list_tools
from src.services.audiences.user_list_customer_type_service import (
    register_user_list_customer_type_tools,
)
from src.services.campaign.campaign_criterion_service import (
    register_campaign_criterion_tools,
)
from src.services.targeting.customer_negative_criterion_service import (
    register_customer_negative_criterion_tools,
)
from src.services.targeting.geo_target_constant_service import (
    register_geo_target_constant_tools,
)

campaign_criterion_server = create_server(register_campaign_criterion_tools)
ad_group_criterion_server = create_server(register_ad_group_criterion_tools)
customer_negative_criterion_server = create_server(
    register_customer_negative_criterion_tools
)
geo_target_constant_server = create_server(register_geo_target_constant_tools)
audience_server = create_server(register_audience_tools)
custom_interest_server = create_server(register_custom_interest_tools)
custom_audience_server = create_server(register_custom_audience_tools)
user_list_server = create_server(register_user_list_tools)
user_list_customer_type_server = create_server(register_user_list_customer_type_tools)
