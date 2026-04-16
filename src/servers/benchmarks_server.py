"""benchmarks server module."""

from src.services.planning.benchmarks_service import register_benchmarks_tools
from src.servers import create_server

benchmarks_server = create_server(register_benchmarks_tools)
