"""identity verification server module."""

from src.services.account.identity_verification_service import (
    register_identity_verification_tools,
)
from src.servers import create_server

identity_verification_server = create_server(register_identity_verification_tools)
