"""Asset group listing group filter service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.resources.types.asset_group_listing_group_filter import (
    AssetGroupListingGroupFilter,
)
from google.ads.googleads.v23.services.services.asset_group_listing_group_filter_service import (
    AssetGroupListingGroupFilterServiceClient,
)
from google.ads.googleads.v23.services.types.asset_group_listing_group_filter_service import (
    AssetGroupListingGroupFilterOperation,
    MutateAssetGroupListingGroupFiltersRequest,
    MutateAssetGroupListingGroupFiltersResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import (
    format_customer_id,
    get_logger,
    serialize_proto_message,
    set_request_options,
)

logger = get_logger(__name__)


class AssetGroupListingGroupFilterService:
    """Service for managing PMax listing group filters (product feed targeting)."""

    def __init__(self) -> None:
        self._client: Optional[AssetGroupListingGroupFilterServiceClient] = None

    @property
    def client(self) -> AssetGroupListingGroupFilterServiceClient:
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service(
                "AssetGroupListingGroupFilterService"
            )
        assert self._client is not None
        return self._client

    async def create_listing_group_filter(
        self,
        ctx: Context,
        customer_id: str,
        asset_group_resource_name: str,
        filter_type: str,
        parent_listing_group_filter: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a listing group filter for a Performance Max asset group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            asset_group_resource_name: Resource name of the asset group
            filter_type: Filter type (UNIT_INCLUDED, UNIT_EXCLUDED, SUBDIVISION)
            parent_listing_group_filter: Resource name of parent filter (for subdivisions)

        Returns:
            Created listing group filter details
        """
        try:
            customer_id = format_customer_id(customer_id)

            from google.ads.googleads.v23.enums.types.listing_group_filter_type_enum import (
                ListingGroupFilterTypeEnum,
            )

            lgf = AssetGroupListingGroupFilter()
            lgf.asset_group = asset_group_resource_name
            lgf.type_ = getattr(
                ListingGroupFilterTypeEnum.ListingGroupFilterType, filter_type
            )
            if parent_listing_group_filter:
                lgf.parent_listing_group_filter = parent_listing_group_filter

            operation = AssetGroupListingGroupFilterOperation()
            operation.create = lgf

            request = MutateAssetGroupListingGroupFiltersRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAssetGroupListingGroupFiltersResponse = (
                self.client.mutate_asset_group_listing_group_filters(request=request)
            )

            await ctx.log(level="info", message="Created listing group filter")

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create listing group filter: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_listing_group_filter(
        self,
        ctx: Context,
        customer_id: str,
        resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Remove a listing group filter.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            resource_name: Resource name of the listing group filter

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)

            operation = AssetGroupListingGroupFilterOperation()
            operation.remove = resource_name

            request = MutateAssetGroupListingGroupFiltersRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAssetGroupListingGroupFiltersResponse = (
                self.client.mutate_asset_group_listing_group_filters(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Removed listing group filter: {resource_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove listing group filter: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_asset_group_listing_group_filter_tools(
    service: AssetGroupListingGroupFilterService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the listing group filter service."""
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def create_listing_group_filter(
        ctx: Context,
        customer_id: str,
        asset_group_resource_name: str,
        filter_type: str,
        parent_listing_group_filter: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a listing group filter for PMax product feed targeting.

        Args:
            customer_id: The customer ID
            asset_group_resource_name: Resource name of the asset group
            filter_type: UNIT_INCLUDED, UNIT_EXCLUDED, or SUBDIVISION
            parent_listing_group_filter: Parent filter resource name (for subdivisions)

        Returns:
            Created filter details
        """
        return await service.create_listing_group_filter(
            ctx=ctx,
            customer_id=customer_id,
            asset_group_resource_name=asset_group_resource_name,
            filter_type=filter_type,
            parent_listing_group_filter=parent_listing_group_filter,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def remove_listing_group_filter(
        ctx: Context,
        customer_id: str,
        resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Remove a listing group filter.

        Args:
            customer_id: The customer ID
            resource_name: Resource name of the filter

        Returns:
            Removal result
        """
        return await service.remove_listing_group_filter(
            ctx=ctx,
            customer_id=customer_id,
            resource_name=resource_name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    tools.extend([create_listing_group_filter, remove_listing_group_filter])
    return tools


def register_asset_group_listing_group_filter_tools(
    mcp: FastMCP[Any],
) -> AssetGroupListingGroupFilterService:
    """Register listing group filter tools with the MCP server."""
    service = AssetGroupListingGroupFilterService()
    tools = create_asset_group_listing_group_filter_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
