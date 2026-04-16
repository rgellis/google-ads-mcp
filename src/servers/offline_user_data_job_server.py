"""offline user data job server module."""

from src.services.data_import.offline_user_data_job_service import (
    register_offline_user_data_job_tools,
)
from src.servers import create_server

offline_user_data_job_server = create_server(register_offline_user_data_job_tools)
