"""smart campaign setting server module."""

from src.services.campaign.smart_campaign_setting_service import (
    register_smart_campaign_setting_tools,
)
from src.servers import create_server

smart_campaign_setting_server = create_server(register_smart_campaign_setting_tools)
