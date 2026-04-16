"""Goal server module."""

from typing import Any
from fastmcp import FastMCP
from src.services.account.goal_service import register_goal_tools

goal_server = FastMCP[Any]()
register_goal_tools(goal_server)
