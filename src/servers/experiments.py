"""Experiment servers."""

from src.servers import create_server
from src.services.campaign.campaign_draft_service import register_campaign_draft_tools
from src.services.campaign.experiment_arm_service import register_experiment_arm_tools
from src.services.campaign.experiment_service import register_experiment_tools

experiment_server = create_server(register_experiment_tools)
experiment_arm_server = create_server(register_experiment_arm_tools)
campaign_draft_server = create_server(register_campaign_draft_tools)
