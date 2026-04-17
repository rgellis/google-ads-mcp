"""Planning and research servers."""

from src.servers import create_server
from src.services.planning.benchmarks_service import register_benchmarks_tools
from src.services.planning.brand_suggestion_service import (
    register_brand_suggestion_tools,
)
from src.services.planning.keyword_plan_ad_group_keyword_service import (
    register_keyword_plan_ad_group_keyword_tools,
)
from src.services.planning.keyword_plan_ad_group_service import (
    register_keyword_plan_ad_group_tools,
)
from src.services.planning.keyword_plan_campaign_keyword_service import (
    register_keyword_plan_campaign_keyword_tools,
)
from src.services.planning.keyword_plan_campaign_service import (
    register_keyword_plan_campaign_tools,
)
from src.services.planning.keyword_plan_idea_service import (
    register_keyword_plan_idea_tools,
)
from src.services.planning.keyword_plan_service import register_keyword_plan_tools
from src.services.planning.keyword_theme_constant_service import (
    register_keyword_theme_constant_tools,
)
from src.services.planning.reach_plan_service import register_reach_plan_tools
from src.services.planning.recommendation_subscription_service import (
    register_recommendation_subscription_tools,
)
from src.services.planning.travel_asset_suggestion_service import (
    register_travel_asset_suggestion_tools,
)

keyword_plan_server = create_server(register_keyword_plan_tools)
keyword_plan_idea_server = create_server(register_keyword_plan_idea_tools)
keyword_plan_ad_group_server = create_server(register_keyword_plan_ad_group_tools)
keyword_plan_campaign_server = create_server(register_keyword_plan_campaign_tools)
keyword_plan_ad_group_keyword_server = create_server(
    register_keyword_plan_ad_group_keyword_tools
)
keyword_plan_campaign_keyword_server = create_server(
    register_keyword_plan_campaign_keyword_tools
)
reach_plan_server = create_server(register_reach_plan_tools)
brand_suggestion_server = create_server(register_brand_suggestion_tools)
keyword_theme_constant_server = create_server(register_keyword_theme_constant_tools)
travel_asset_suggestion_server = create_server(register_travel_asset_suggestion_tools)
recommendation_subscription_server = create_server(
    register_recommendation_subscription_tools
)
benchmarks_server = create_server(register_benchmarks_tools)
