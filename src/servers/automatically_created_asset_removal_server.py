"""Automatically created asset removal server module."""

from typing import Any
from fastmcp import FastMCP
from src.services.campaign.automatically_created_asset_removal_service import (
    register_automatically_created_asset_removal_tools,
)

automatically_created_asset_removal_server = FastMCP[Any]()
register_automatically_created_asset_removal_tools(
    automatically_created_asset_removal_server
)
