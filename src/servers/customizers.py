"""Customizer servers."""

from src.servers import create_server
from src.services.ad_group.ad_group_criterion_customizer_service import (
    register_ad_group_criterion_customizer_tools,
)
from src.services.ad_group.ad_group_customizer_service import (
    register_ad_group_customizer_tools,
)
from src.services.ad_group.ad_parameter_service import register_ad_parameter_tools
from src.services.campaign.campaign_customizer_service import (
    register_campaign_customizer_tools,
)
from src.services.account.customer_customizer_service import (
    register_customer_customizer_tools,
)
from src.services.shared.customizer_attribute_service import (
    register_customizer_attribute_tools,
)

customizer_sdk_server = create_server(register_customizer_attribute_tools)
customer_customizer_server = create_server(register_customer_customizer_tools)
campaign_customizer_server = create_server(register_campaign_customizer_tools)
ad_group_customizer_server = create_server(register_ad_group_customizer_tools)
ad_group_criterion_customizer_server = create_server(
    register_ad_group_criterion_customizer_tools
)
ad_parameter_server = create_server(register_ad_parameter_tools)
