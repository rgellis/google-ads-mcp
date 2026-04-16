"""Customer asset set service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.resources.types.customer_asset_set import (
    CustomerAssetSet,
)
from google.ads.googleads.v23.services.services.customer_asset_set_service import (
    CustomerAssetSetServiceClient,
)
from google.ads.googleads.v23.services.types.customer_asset_set_service import (
    CustomerAssetSetOperation,
    MutateCustomerAssetSetsRequest,
    MutateCustomerAssetSetsResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import (
    format_customer_id,
    get_logger,
    serialize_proto_message,
    set_request_options,
)

logger = get_logger(__name__)


class CustomerAssetSetService:
    """Service for managing customer-level asset set links."""

    def __init__(self) -> None:
        self._client: Optional[CustomerAssetSetServiceClient] = None

    @property
    def client(self) -> CustomerAssetSetServiceClient:
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CustomerAssetSetService")
        assert self._client is not None
        return self._client

    async def link_asset_set_to_customer(
        self,
        ctx: Context,
        customer_id: str,
        asset_set_resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Link an asset set to a customer.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            asset_set_resource_name: Resource name of the asset set

        Returns:
            Created customer asset set link details
        """
        try:
            customer_id = format_customer_id(customer_id)

            customer_asset_set = CustomerAssetSet()
            customer_asset_set.asset_set = asset_set_resource_name
            customer_asset_set.customer = f"customers/{customer_id}"

            operation = CustomerAssetSetOperation()
            operation.create = customer_asset_set

            request = MutateCustomerAssetSetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCustomerAssetSetsResponse = (
                self.client.mutate_customer_asset_sets(request=request)
            )

            await ctx.log(level="info", message="Linked asset set to customer")

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to link asset set to customer: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def unlink_asset_set_from_customer(
        self,
        ctx: Context,
        customer_id: str,
        customer_asset_set_resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Unlink an asset set from a customer.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            customer_asset_set_resource_name: Resource name of the customer asset set link

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)

            operation = CustomerAssetSetOperation()
            operation.remove = customer_asset_set_resource_name

            request = MutateCustomerAssetSetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateCustomerAssetSetsResponse = (
                self.client.mutate_customer_asset_sets(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Unlinked asset set from customer: {customer_asset_set_resource_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to unlink asset set from customer: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_customer_asset_set_tools(
    service: CustomerAssetSetService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the customer asset set service."""
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def link_asset_set_to_customer(
        ctx: Context,
        customer_id: str,
        asset_set_resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Link an asset set to a customer.

        Args:
            customer_id: The customer ID
            asset_set_resource_name: Resource name of the asset set

        Returns:
            Created link details
        """
        return await service.link_asset_set_to_customer(
            ctx=ctx,
            customer_id=customer_id,
            asset_set_resource_name=asset_set_resource_name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def unlink_asset_set_from_customer(
        ctx: Context,
        customer_id: str,
        customer_asset_set_resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Unlink an asset set from a customer.

        Args:
            customer_id: The customer ID
            customer_asset_set_resource_name: Resource name of the link to remove

        Returns:
            Removal result
        """
        return await service.unlink_asset_set_from_customer(
            ctx=ctx,
            customer_id=customer_id,
            customer_asset_set_resource_name=customer_asset_set_resource_name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    tools.extend([link_asset_set_to_customer, unlink_asset_set_from_customer])
    return tools


def register_customer_asset_set_tools(
    mcp: FastMCP[Any],
) -> CustomerAssetSetService:
    """Register customer asset set tools with the MCP server."""
    service = CustomerAssetSetService()
    tools = create_customer_asset_set_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
