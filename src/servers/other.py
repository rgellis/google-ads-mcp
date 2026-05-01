"""Other servers: smart campaigns, batch jobs, user data, local services, campaign groups."""

from src.servers import create_server
from src.services.campaign.campaign_goal_config_service import (
    register_campaign_goal_config_tools,
)
from src.services.campaign.campaign_group_service import register_campaign_group_tools
from src.services.campaign.campaign_lifecycle_goal_service import (
    register_campaign_lifecycle_goal_tools,
)
from src.services.campaign.reservation_service import register_reservation_tools
from src.services.campaign.smart_campaign_service import register_smart_campaign_tools
from src.services.campaign.smart_campaign_setting_service import (
    register_smart_campaign_setting_tools,
)
from src.services.data_import.batch_job_service import register_batch_job_tools
from src.services.data_import.local_services_lead_service import (
    register_local_services_lead_tools,
)
from src.services.data_import.user_data_service import register_user_data_tools

smart_campaign_server = create_server(register_smart_campaign_tools)
smart_campaign_setting_server = create_server(register_smart_campaign_setting_tools)
batch_job_server = create_server(register_batch_job_tools)
user_data_server = create_server(register_user_data_tools)
local_services_lead_server = create_server(register_local_services_lead_tools)
campaign_group_server = create_server(register_campaign_group_tools)
campaign_goal_config_server = create_server(register_campaign_goal_config_tools)
campaign_lifecycle_goal_server = create_server(register_campaign_lifecycle_goal_tools)
reservation_server = create_server(register_reservation_tools)
