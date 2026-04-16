"""asset generation server module."""

from typing import Any
from fastmcp import FastMCP
from src.services.assets.asset_generation_service import register_asset_generation_tools

asset_generation_server = FastMCP[Any]()
register_asset_generation_tools(asset_generation_server)
