"""conversion value rule server module."""

from src.services.conversions.conversion_value_rule_service import (
    register_conversion_value_rule_tools,
)
from src.servers import create_server

conversion_value_rule_server = create_server(register_conversion_value_rule_tools)
