"""Account management servers."""

from src.servers import create_server
from src.services.account.account_budget_proposal_service import (
    register_account_budget_proposal_tools,
)
from src.services.account.account_link_service import register_account_link_tools
from src.services.account.billing_setup_service import register_billing_setup_tools
from src.services.account.customer_client_link_service import (
    register_customer_client_link_tools,
)
from src.services.account.customer_lifecycle_goal_service import (
    register_customer_lifecycle_goal_tools,
)
from src.services.account.customer_manager_link_service import (
    register_customer_manager_link_tools,
)
from src.services.account.customer_sk_ad_network_service import (
    register_customer_sk_ad_network_tools,
)
from src.services.account.customer_user_access_invitation_service import (
    register_customer_user_access_invitation_tools,
)
from src.services.account.customer_user_access_service import (
    register_customer_user_access_tools,
)
from src.services.account.goal_service import register_goal_tools
from src.services.account.identity_verification_service import (
    register_identity_verification_tools,
)
from src.services.account.incentive_service import register_incentive_tools
from src.services.account.payments_account_service import (
    register_payments_account_tools,
)
from src.services.data_import.data_link_service import register_data_link_tools
from src.services.product_integration.product_link_invitation_service import (
    register_product_link_invitation_tools,
)
from src.services.product_integration.product_link_service import (
    register_product_link_tools,
)
from src.services.product_integration.third_party_app_analytics_link_service import (
    register_third_party_app_analytics_link_tools,
)

customer_user_access_server = create_server(register_customer_user_access_tools)
customer_user_access_invitation_server = create_server(
    register_customer_user_access_invitation_tools
)
customer_client_link_server = create_server(register_customer_client_link_tools)
customer_manager_link_server = create_server(register_customer_manager_link_tools)
account_link_server = create_server(register_account_link_tools)
account_budget_proposal_server = create_server(register_account_budget_proposal_tools)
billing_setup_server = create_server(register_billing_setup_tools)
payments_account_server = create_server(register_payments_account_tools)
identity_verification_server = create_server(register_identity_verification_tools)
product_link_server = create_server(register_product_link_tools)
product_link_invitation_server = create_server(register_product_link_invitation_tools)
data_link_server = create_server(register_data_link_tools)
goal_server = create_server(register_goal_tools)
incentive_server = create_server(register_incentive_tools)
customer_lifecycle_goal_server = create_server(register_customer_lifecycle_goal_tools)
customer_sk_ad_network_server = create_server(register_customer_sk_ad_network_tools)
third_party_app_analytics_link_server = create_server(
    register_third_party_app_analytics_link_tools
)
