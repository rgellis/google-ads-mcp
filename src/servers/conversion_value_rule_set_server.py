"""conversion value rule set server module."""

from src.services.conversions.conversion_value_rule_set_service import (
    register_conversion_value_rule_set_tools,
)
from src.servers import create_server

conversion_value_rule_set_server = create_server(
    register_conversion_value_rule_set_tools
)
