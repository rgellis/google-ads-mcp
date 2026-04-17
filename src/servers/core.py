"""Core servers: customer, campaign, budget, ad groups, keywords, ads, conversions, search."""

from src.servers import create_server
from src.services.account.customer_service import register_customer_tools
from src.services.ad_group.ad_group_ad_service import register_ad_group_ad_tools
from src.services.ad_group.ad_group_service import register_ad_group_tools
from src.services.ad_group.ad_service import register_ad_tools
from src.services.ad_group.keyword_service import register_keyword_tools
from src.services.bidding.budget_service import register_budget_tools
from src.services.campaign.campaign_service import register_campaign_tools
from src.services.conversions.conversion_service import register_conversion_tools
from src.services.metadata.google_ads_service import register_google_ads_tools

customer_service_server = create_server(register_customer_tools)
campaign_server = create_server(register_campaign_tools)
budget_server = create_server(register_budget_tools)
ad_group_server = create_server(register_ad_group_tools)
keyword_server = create_server(register_keyword_tools)
ad_server = create_server(register_ad_tools)
ad_group_ad_server = create_server(register_ad_group_ad_tools)
conversion_server = create_server(register_conversion_tools)
google_ads_server = create_server(register_google_ads_tools)
