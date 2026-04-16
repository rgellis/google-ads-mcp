"""keyword plan server module."""

from src.services.planning.keyword_plan_service import register_keyword_plan_tools
from src.servers import create_server

keyword_plan_server = create_server(register_keyword_plan_tools)
