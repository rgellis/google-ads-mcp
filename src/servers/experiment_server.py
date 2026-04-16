"""experiment server module."""

from src.services.campaign.experiment_service import register_experiment_tools
from src.servers import create_server

experiment_server = create_server(register_experiment_tools)
