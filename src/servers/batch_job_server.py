"""batch job server module."""

from src.services.data_import.batch_job_service import register_batch_job_tools
from src.servers import create_server

batch_job_server = create_server(register_batch_job_tools)
