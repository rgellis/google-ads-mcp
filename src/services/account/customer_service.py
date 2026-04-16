"""Customer service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.resources.types.customer import Customer
from google.ads.googleads.v23.services.services.customer_service import (
    CustomerServiceClient,
)
from google.ads.googleads.v23.services.types.customer_service import (
    CreateCustomerClientRequest,
    CreateCustomerClientResponse,
    CustomerOperation,
    ListAccessibleCustomersRequest,
    ListAccessibleCustomersResponse,
    MutateCustomerRequest,
    MutateCustomerResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class CustomerService:
    """Customer service for managing Google Ads customers."""

    def __init__(self) -> None:
        """Initialize the customer service."""
        self._client: Optional[CustomerServiceClient] = None

    @property
    def client(self) -> CustomerServiceClient:
        """Get the customer service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CustomerService")
        assert self._client is not None
        return self._client

    async def create_customer_client(
        self,
        ctx: Context,
        manager_customer_id: str,
        descriptive_name: str,
        currency_code: str = "USD",
        time_zone: str = "America/New_York",
    ) -> Dict[str, Any]:
        """Create a new client customer under a manager account.

        Args:
            ctx: FastMCP context
            manager_customer_id: The manager customer ID
            descriptive_name: Name of the new client
            currency_code: Currency code (e.g. USD, EUR)
            time_zone: Time zone ID

        Returns:
            Created customer details
        """
        try:
            manager_customer_id = format_customer_id(manager_customer_id)

            # Create a new customer object
            customer = Customer()
            customer.descriptive_name = descriptive_name
            customer.currency_code = currency_code
            customer.time_zone = time_zone

            # Create the request
            request = CreateCustomerClientRequest()
            request.customer_id = manager_customer_id
            request.customer_client = customer

            # Make the API call
            response: CreateCustomerClientResponse = self.client.create_customer_client(
                request=request
            )

            # Extract customer ID from resource name
            customer_resource = response.resource_name
            customer_id = customer_resource.split("/")[-1] if customer_resource else ""

            await ctx.log(
                level="info",
                message=f"Created customer client {customer_id} under manager {manager_customer_id}",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create customer client: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_accessible_customers(self, ctx: Context) -> Dict[str, Any]:
        """List all accessible customers for the authenticated user.

        Args:
            ctx: FastMCP context

        Returns:
            List of accessible customer resource names and IDs
        """
        try:
            request = ListAccessibleCustomersRequest()

            response: ListAccessibleCustomersResponse = (
                self.client.list_accessible_customers(request=request)
            )

            customer_ids = [
                resource_name.split("/")[-1]
                for resource_name in response.resource_names
                if resource_name
            ]

            await ctx.log(
                level="info",
                message=f"Found {len(customer_ids)} accessible customers",
            )

            return {
                "resource_names": list(response.resource_names),
                "customer_ids": customer_ids,
            }

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to list accessible customers: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def mutate_customer(
        self,
        ctx: Context,
        customer_id: str,
        descriptive_name: Optional[str] = None,
        auto_tagging_enabled: Optional[bool] = None,
        tracking_url_template: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a customer's settings.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID to update
            descriptive_name: New descriptive name (optional)
            auto_tagging_enabled: Enable/disable auto-tagging (optional)
            tracking_url_template: New tracking URL template (optional)

        Returns:
            Updated customer details
        """
        try:
            customer_id = format_customer_id(customer_id)

            customer = Customer()
            customer.resource_name = f"customers/{customer_id}"

            update_mask_fields = []

            if descriptive_name is not None:
                customer.descriptive_name = descriptive_name
                update_mask_fields.append("descriptive_name")

            if auto_tagging_enabled is not None:
                customer.auto_tagging_enabled = auto_tagging_enabled
                update_mask_fields.append("auto_tagging_enabled")

            if tracking_url_template is not None:
                customer.tracking_url_template = tracking_url_template
                update_mask_fields.append("tracking_url_template")

            operation = CustomerOperation()
            operation.update = customer
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_fields)
            )

            request = MutateCustomerRequest()
            request.customer_id = customer_id
            request.operation = operation

            response: MutateCustomerResponse = self.client.mutate_customer(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Updated customer {customer_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to mutate customer: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_customer_tools(
    service: CustomerService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the customer service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_customer_client(
        ctx: Context,
        manager_customer_id: str,
        descriptive_name: str,
        currency_code: str = "USD",
        time_zone: str = "America/New_York",
    ) -> Dict[str, Any]:
        """Create a new client customer under a manager account.

        Args:
            manager_customer_id: The manager customer ID
            descriptive_name: Name of the new client
            currency_code: Currency code (e.g. USD, EUR)
            time_zone: Time zone ID

        Returns:
            Created customer details
        """
        return await service.create_customer_client(
            ctx=ctx,
            manager_customer_id=manager_customer_id,
            descriptive_name=descriptive_name,
            currency_code=currency_code,
            time_zone=time_zone,
        )

    async def list_accessible_customers(ctx: Context) -> Dict[str, Any]:
        """List all accessible customers for the authenticated user.

        Returns:
            List of accessible customer resource names and IDs
        """
        return await service.list_accessible_customers(ctx=ctx)

    async def mutate_customer(
        ctx: Context,
        customer_id: str,
        descriptive_name: Optional[str] = None,
        auto_tagging_enabled: Optional[bool] = None,
        tracking_url_template: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a customer's settings.

        Args:
            customer_id: The customer ID to update
            descriptive_name: New descriptive name (optional)
            auto_tagging_enabled: Enable/disable auto-tagging (optional)
            tracking_url_template: New tracking URL template (optional)

        Returns:
            Updated customer details
        """
        return await service.mutate_customer(
            ctx=ctx,
            customer_id=customer_id,
            descriptive_name=descriptive_name,
            auto_tagging_enabled=auto_tagging_enabled,
            tracking_url_template=tracking_url_template,
        )

    tools.extend([create_customer_client, list_accessible_customers, mutate_customer])
    return tools


def register_customer_tools(mcp: FastMCP[Any]) -> CustomerService:
    """Register customer tools with the MCP server.

    Returns the CustomerService instance for testing purposes.
    """
    service = CustomerService()
    tools = create_customer_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
