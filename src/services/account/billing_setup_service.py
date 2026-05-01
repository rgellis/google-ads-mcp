"""Billing setup service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.enums.types.time_type import TimeTypeEnum
from google.ads.googleads.v23.resources.types.billing_setup import BillingSetup
from google.ads.googleads.v23.services.services.billing_setup_service import (
    BillingSetupServiceClient,
)
from google.ads.googleads.v23.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v23.services.types.billing_setup_service import (
    BillingSetupOperation,
    MutateBillingSetupRequest,
    MutateBillingSetupResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import (
    format_customer_id,
    gaql_enum_name,
    gaql_int,
    get_logger,
    serialize_proto_message,
    set_optional_submessage,
)

logger = get_logger(__name__)


class BillingSetupService:
    """Billing setup service for managing billing configurations."""

    def __init__(self) -> None:
        """Initialize the billing setup service."""
        self._client: Optional[BillingSetupServiceClient] = None

    @property
    def client(self) -> BillingSetupServiceClient:
        """Get the billing setup service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("BillingSetupService")
        assert self._client is not None
        return self._client

    async def create_billing_setup(
        self,
        ctx: Context,
        customer_id: str,
        payments_account_id: Optional[str] = None,
        payments_account_info: Optional[Dict[str, Any]] = None,
        start_date: Optional[str] = None,
        start_time_type: Optional[TimeTypeEnum.TimeType] = None,
    ) -> Dict[str, Any]:
        """Create a billing setup for a customer.

        Note: MutateBillingSetupRequest does not support partial_failure,
        validate_only, or response_content_type — those parameters were
        removed because passing them was a silent no-op.

        ``payments_account_id`` and ``payments_account_info`` are
        mutually-exclusive members of the BillingSetup payments-account
        oneof. Pass exactly one:

        - ``payments_account_id``: link an existing payments account
          by ID. The wrapper builds the
          ``customers/{customer_id}/paymentsAccounts/{id}`` resource
          name for you.
        - ``payments_account_info``: dict that builds an inline
          ``BillingSetup.PaymentsAccountInfo`` submessage, used when
          you want the API to create a new payments account along
          with the billing setup. See the v23 BillingSetup proto
          reference for the full nested schema; common fields:
          ``payments_account_name``, ``payments_profile_id``,
          ``secondary_payments_profile_id``, ``payments_account_id``.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            payments_account_id: The payments account ID to link
            payments_account_info: Inline payments-account-info dict.
                Mutually exclusive with payments_account_id.
            start_date: Start date in YYYY-MM-DD format (used when start_time_type is not NOW)
            start_time_type: Optional start time type enum (NOW or
                FUTURE). The proto's start_time oneof requires exactly one
                of start_date_time or start_time_type — supply start_date OR
                start_time_type, not both. Omit both to let the API handle defaults.

        Returns:
            Created billing setup details
        """
        if payments_account_id is None and payments_account_info is None:
            raise ValueError(
                "create_billing_setup requires payments_account_id or "
                "payments_account_info."
            )
        if payments_account_id is not None and payments_account_info is not None:
            raise ValueError(
                "payments_account_id and payments_account_info are mutually "
                "exclusive (BillingSetup.payments_account oneof)."
            )
        try:
            customer_id = format_customer_id(customer_id)

            billing_setup = BillingSetup()

            if payments_account_id is not None:
                billing_setup.payments_account = (
                    f"customers/{customer_id}/paymentsAccounts/{payments_account_id}"
                )
            if payments_account_info is not None:
                set_optional_submessage(
                    billing_setup,
                    "payments_account_info",
                    payments_account_info,
                    BillingSetup.PaymentsAccountInfo,
                )

            # Set start date/time (mutually exclusive oneof fields)
            if start_time_type is not None:
                billing_setup.start_time_type = start_time_type
            elif start_date:
                billing_setup.start_date_time = start_date

            # Create operation
            operation = BillingSetupOperation()
            operation.create = billing_setup

            # Create request
            request = MutateBillingSetupRequest()
            request.customer_id = customer_id
            request.operation = operation

            # Make the API call
            response: MutateBillingSetupResponse = self.client.mutate_billing_setup(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created billing setup for customer {customer_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create billing setup: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_billing_setups(
        self,
        ctx: Context,
        customer_id: str,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List billing setups for a customer.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            status_filter: Optional status filter (UNKNOWN, PENDING, APPROVED, CANCELLED)

        Returns:
            List of billing setups
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use GoogleAdsService for search
            sdk_client = get_sdk_client()
            google_ads_service: GoogleAdsServiceClient = sdk_client.client.get_service(
                "GoogleAdsService"
            )

            # Build query
            query = """
                SELECT
                    billing_setup.resource_name,
                    billing_setup.id,
                    billing_setup.status,
                    billing_setup.payments_account,
                    billing_setup.start_date_time,
                    billing_setup.start_time_type,
                    billing_setup.end_date_time,
                    billing_setup.end_time_type
                FROM billing_setup
            """

            if status_filter:
                query += f" WHERE billing_setup.status = '{gaql_enum_name(status_filter, 'status_filter')}'"

            query += " ORDER BY billing_setup.id"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            billing_setups = []
            for row in response:
                billing_setup = row.billing_setup
                billing_setups.append(serialize_proto_message(billing_setup))

            await ctx.log(
                level="info",
                message=f"Found {len(billing_setups)} billing setups",
            )

            return billing_setups

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to list billing setups: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def get_billing_setup(
        self,
        ctx: Context,
        customer_id: str,
        billing_setup_id: str,
    ) -> Dict[str, Any]:
        """Get details of a specific billing setup.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            billing_setup_id: The billing setup ID

        Returns:
            Billing setup details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use GoogleAdsService for search
            sdk_client = get_sdk_client()
            google_ads_service: GoogleAdsServiceClient = sdk_client.client.get_service(
                "GoogleAdsService"
            )

            # Build query
            query = f"""
                SELECT
                    billing_setup.resource_name,
                    billing_setup.id,
                    billing_setup.status,
                    billing_setup.payments_account,
                    billing_setup.start_date_time,
                    billing_setup.start_time_type,
                    billing_setup.end_date_time,
                    billing_setup.end_time_type
                FROM billing_setup
                WHERE billing_setup.id = {gaql_int(billing_setup_id, "billing_setup_id")}
            """

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process result
            for row in response:
                billing_setup = row.billing_setup

                await ctx.log(
                    level="info",
                    message=f"Found billing setup {billing_setup_id}",
                )

                return serialize_proto_message(billing_setup)

            # If no billing setup found
            raise Exception(f"Billing setup {billing_setup_id} not found")

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to get billing setup: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_payments_accounts(
        self,
        ctx: Context,
        customer_id: str,
    ) -> List[Dict[str, Any]]:
        """List available payments accounts for a customer.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID

        Returns:
            List of payments accounts
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use GoogleAdsService for search
            sdk_client = get_sdk_client()
            google_ads_service: GoogleAdsServiceClient = sdk_client.client.get_service(
                "GoogleAdsService"
            )

            # Build query
            query = """
                SELECT
                    payments_account.resource_name,
                    payments_account.payments_account_id,
                    payments_account.name,
                    payments_account.currency_code,
                    payments_account.payments_profile_id
                FROM payments_account
                ORDER BY payments_account.name
            """

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            payments_accounts = []
            for row in response:
                payments_account = row.payments_account
                payments_accounts.append(serialize_proto_message(payments_account))

            await ctx.log(
                level="info",
                message=f"Found {len(payments_accounts)} payments accounts",
            )

            return payments_accounts

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to list payments accounts: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_billing_setup(
        self,
        ctx: Context,
        customer_id: str,
        billing_setup_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove (cancel) a pending billing setup.

        Note: MutateBillingSetupRequest does not support partial_failure,
        validate_only, or response_content_type.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            billing_setup_resource_name: Resource name of the billing setup to cancel

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)

            operation = BillingSetupOperation()
            operation.remove = billing_setup_resource_name

            request = MutateBillingSetupRequest()
            request.customer_id = customer_id
            request.operation = operation

            response: MutateBillingSetupResponse = self.client.mutate_billing_setup(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Removed billing setup: {billing_setup_resource_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove billing setup: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_billing_setup_tools(
    service: BillingSetupService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the billing setup service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_billing_setup(
        ctx: Context,
        customer_id: str,
        payments_account_id: Optional[str] = None,
        payments_account_info: Optional[Dict[str, Any]] = None,
        start_date: Optional[str] = None,
        start_time_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a billing setup for a customer.

        Pass exactly one of ``payments_account_id`` (link existing
        payments account) or ``payments_account_info`` (inline new
        payments-account submessage). Both are members of the
        BillingSetup payments-account oneof.

        Args:
            customer_id: The customer ID
            payments_account_id: Existing payments account ID to link.
            payments_account_info: Inline payments-account-info dict
                used to create a new payments account inline. See the
                v23 BillingSetup proto reference for the schema —
                common fields: ``payments_account_name``,
                ``payments_profile_id``,
                ``secondary_payments_profile_id``,
                ``payments_account_id``.
            start_date: Start date in YYYY-MM-DD format. Mutually exclusive
                with start_time_type (proto oneof). Omit both to let the API
                handle defaults.
            start_time_type: Optional - NOW or FUTURE. Mutually exclusive
                with start_date.

        Returns:
            Created billing setup details
        """
        start_enum = (
            getattr(TimeTypeEnum.TimeType, start_time_type)
            if start_time_type is not None
            else None
        )

        return await service.create_billing_setup(
            ctx=ctx,
            customer_id=customer_id,
            payments_account_id=payments_account_id,
            payments_account_info=payments_account_info,
            start_date=start_date,
            start_time_type=start_enum,
        )

    async def list_billing_setups(
        ctx: Context,
        customer_id: str,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List billing setups for a customer.

        For filters beyond the structured params here (substring-on-name,
        date ranges, metric thresholds, custom SELECT/ORDER BY,
        multi-condition AND/OR), use ``search_google_ads`` with a
        free-form GAQL query.

        Args:
            customer_id: The customer ID
            status_filter: Optional status filter (UNKNOWN, PENDING, APPROVED, CANCELLED)

        Returns:
            List of billing setups with details
        """
        return await service.list_billing_setups(
            ctx=ctx,
            customer_id=customer_id,
            status_filter=status_filter,
        )

    async def get_billing_setup(
        ctx: Context,
        customer_id: str,
        billing_setup_id: str,
    ) -> Dict[str, Any]:
        """Get details of a specific billing setup.

        Args:
            customer_id: The customer ID
            billing_setup_id: The billing setup ID

        Returns:
            Billing setup details including status and account information
        """
        return await service.get_billing_setup(
            ctx=ctx,
            customer_id=customer_id,
            billing_setup_id=billing_setup_id,
        )

    async def list_payments_accounts(
        ctx: Context,
        customer_id: str,
    ) -> List[Dict[str, Any]]:
        """List available payments accounts for a customer.

        For filters beyond the structured params here (substring-on-name,
        date ranges, metric thresholds, custom SELECT/ORDER BY,
        multi-condition AND/OR), use ``search_google_ads`` with a
        free-form GAQL query.

        Args:
            customer_id: The customer ID

        Returns:
            List of payments accounts that can be linked to billing setups
        """
        return await service.list_payments_accounts(
            ctx=ctx,
            customer_id=customer_id,
        )

    async def remove_billing_setup(
        ctx: Context,
        customer_id: str,
        billing_setup_resource_name: str,
    ) -> Dict[str, Any]:
        """Remove (cancel) a pending billing setup.

        Only pending billing setups can be removed.

        Args:
            customer_id: The customer ID
            billing_setup_resource_name: Resource name of the billing setup to cancel

        Returns:
            Removal result
        """
        return await service.remove_billing_setup(
            ctx=ctx,
            customer_id=customer_id,
            billing_setup_resource_name=billing_setup_resource_name,
        )

    tools.extend(
        [
            create_billing_setup,
            list_billing_setups,
            get_billing_setup,
            list_payments_accounts,
            remove_billing_setup,
        ]
    )
    return tools


def register_billing_setup_tools(mcp: FastMCP[Any]) -> BillingSetupService:
    """Register billing setup tools with the MCP server.

    Returns the BillingSetupService instance for testing purposes.
    """
    service = BillingSetupService()
    tools = create_billing_setup_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
