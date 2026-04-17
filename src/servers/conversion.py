"""Conversion tracking and upload servers."""

from src.servers import create_server
from src.services.audiences.remarketing_action_service import (
    register_remarketing_action_tools,
)
from src.services.campaign.campaign_conversion_goal_service import (
    register_campaign_conversion_goal_tools,
)
from src.services.conversions.conversion_adjustment_upload_service import (
    register_conversion_adjustment_upload_tools,
)
from src.services.conversions.conversion_custom_variable_service import (
    register_conversion_custom_variable_tools,
)
from src.services.conversions.conversion_goal_campaign_config_service import (
    register_conversion_goal_campaign_config_tools,
)
from src.services.conversions.conversion_upload_service import (
    register_conversion_upload_tools,
)
from src.services.conversions.conversion_value_rule_service import (
    register_conversion_value_rule_tools,
)
from src.services.conversions.conversion_value_rule_set_service import (
    register_conversion_value_rule_set_tools,
)
from src.services.conversions.custom_conversion_goal_service import (
    register_custom_conversion_goal_tools,
)
from src.services.conversions.customer_conversion_goal_service import (
    register_customer_conversion_goal_tools,
)
from src.services.data_import.offline_user_data_job_service import (
    register_offline_user_data_job_tools,
)

conversion_upload_server = create_server(register_conversion_upload_tools)
conversion_adjustment_upload_server = create_server(
    register_conversion_adjustment_upload_tools
)
conversion_value_rule_server = create_server(register_conversion_value_rule_tools)
conversion_value_rule_set_server = create_server(
    register_conversion_value_rule_set_tools
)
conversion_custom_variable_server = create_server(
    register_conversion_custom_variable_tools
)
conversion_goal_campaign_config_server = create_server(
    register_conversion_goal_campaign_config_tools
)
custom_conversion_goal_server = create_server(register_custom_conversion_goal_tools)
customer_conversion_goal_server = create_server(register_customer_conversion_goal_tools)
campaign_conversion_goal_server = create_server(register_campaign_conversion_goal_tools)
offline_user_data_job_server = create_server(register_offline_user_data_job_tools)
remarketing_action_server = create_server(register_remarketing_action_tools)
