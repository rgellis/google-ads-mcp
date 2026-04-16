"""benchmarks server module."""

from typing import Any
from fastmcp import FastMCP
from src.services.planning.benchmarks_service import register_benchmarks_tools

benchmarks_server = FastMCP[Any]()
register_benchmarks_tools(benchmarks_server)
