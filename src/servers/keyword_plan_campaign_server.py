"""keyword plan campaign server module."""

from src.services.planning.keyword_plan_campaign_service import (
    register_keyword_plan_campaign_tools,
)
from src.servers import create_server

keyword_plan_campaign_server = create_server(register_keyword_plan_campaign_tools)
