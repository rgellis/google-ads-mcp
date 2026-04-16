"""customer sk ad network server module."""

from typing import Any
from fastmcp import FastMCP
from src.services.account.customer_sk_ad_network_service import (
    register_customer_sk_ad_network_tools,
)

customer_sk_ad_network_server = FastMCP[Any]()
register_customer_sk_ad_network_tools(customer_sk_ad_network_server)
