"""keyword plan ad group keyword server module."""

from src.services.planning.keyword_plan_ad_group_keyword_service import (
    register_keyword_plan_ad_group_keyword_tools,
)
from src.servers import create_server

keyword_plan_ad_group_keyword_server = create_server(
    register_keyword_plan_ad_group_keyword_tools
)
