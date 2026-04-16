"""keyword plan idea server module."""

from src.services.planning.keyword_plan_idea_service import (
    register_keyword_plan_idea_tools,
)
from src.servers import create_server

keyword_plan_idea_server = create_server(register_keyword_plan_idea_tools)
