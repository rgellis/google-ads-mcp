"""keyword plan ad group server module."""

from src.services.planning.keyword_plan_ad_group_service import (
    register_keyword_plan_ad_group_tools,
)
from src.servers import create_server

keyword_plan_ad_group_server = create_server(register_keyword_plan_ad_group_tools)
