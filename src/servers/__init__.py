"""Google Ads MCP server factories."""

from typing import Any, Callable

from fastmcp import FastMCP


def create_server(register_fn: Callable[..., Any]) -> FastMCP[Any]:
    """Create a FastMCP server and register tools with it.

    Args:
        register_fn: A register_*_tools function that accepts a FastMCP instance

    Returns:
        Configured FastMCP server with tools registered
    """
    server = FastMCP[Any]()
    register_fn(server)
    return server
