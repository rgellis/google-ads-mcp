"""customer user access invitation server module."""

from src.services.account.customer_user_access_invitation_service import (
    register_customer_user_access_invitation_tools,
)
from src.servers import create_server

customer_user_access_invitation_server = create_server(
    register_customer_user_access_invitation_tools
)
