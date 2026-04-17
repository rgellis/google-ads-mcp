"""Labels, shared sets, and organization servers."""

from src.servers import create_server
from src.services.ad_group.ad_group_ad_label_service import (
    register_ad_group_ad_label_tools,
)
from src.services.ad_group.ad_group_criterion_label_service import (
    register_ad_group_criterion_label_tools,
)
from src.services.ad_group.ad_group_label_service import register_ad_group_label_tools
from src.services.campaign.campaign_label_service import register_campaign_label_tools
from src.services.campaign.campaign_shared_set_service import (
    register_campaign_shared_set_tools,
)
from src.services.account.customer_label_service import register_customer_label_tools
from src.services.shared.label_service import register_label_tools
from src.services.shared.shared_criterion_service import register_shared_criterion_tools
from src.services.shared.shared_set_service import register_shared_set_tools

label_server = create_server(register_label_tools)
campaign_label_server = create_server(register_campaign_label_tools)
ad_group_label_server = create_server(register_ad_group_label_tools)
ad_group_ad_label_server = create_server(register_ad_group_ad_label_tools)
ad_group_criterion_label_server = create_server(register_ad_group_criterion_label_tools)
customer_label_server = create_server(register_customer_label_tools)
shared_set_server = create_server(register_shared_set_tools)
shared_criterion_server = create_server(register_shared_criterion_tools)
campaign_shared_set_server = create_server(register_campaign_shared_set_tools)
