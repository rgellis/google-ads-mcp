"""keyword plan campaign keyword server module."""

from src.services.planning.keyword_plan_campaign_keyword_service import (
    register_keyword_plan_campaign_keyword_tools,
)
from src.servers import create_server

keyword_plan_campaign_keyword_server = create_server(
    register_keyword_plan_campaign_keyword_tools
)
