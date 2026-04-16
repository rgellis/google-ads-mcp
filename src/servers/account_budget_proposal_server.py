"""account budget proposal server module."""

from src.services.account.account_budget_proposal_service import (
    register_account_budget_proposal_tools,
)
from src.servers import create_server

account_budget_proposal_server = create_server(register_account_budget_proposal_tools)
