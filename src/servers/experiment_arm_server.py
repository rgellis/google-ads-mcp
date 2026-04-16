"""experiment arm server module."""

from src.services.campaign.experiment_arm_service import register_experiment_arm_tools
from src.servers import create_server

experiment_arm_server = create_server(register_experiment_arm_tools)
