"""Asset set asset service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.resources.types.asset_set_asset import AssetSetAsset
from google.ads.googleads.v23.services.services.asset_set_asset_service import (
    AssetSetAssetServiceClient,
)
from google.ads.googleads.v23.services.types.asset_set_asset_service import (
    AssetSetAssetOperation,
    MutateAssetSetAssetsRequest,
    MutateAssetSetAssetsResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import (
    format_customer_id,
    get_logger,
    serialize_proto_message,
    set_request_options,
)

logger = get_logger(__name__)


class AssetSetAssetService:
    """Service for linking assets to asset sets."""

    def __init__(self) -> None:
        self._client: Optional[AssetSetAssetServiceClient] = None

    @property
    def client(self) -> AssetSetAssetServiceClient:
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("AssetSetAssetService")
        assert self._client is not None
        return self._client

    async def add_asset_to_set(
        self,
        ctx: Context,
        customer_id: str,
        asset_resource_name: str,
        asset_set_resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add an asset to an asset set.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            asset_resource_name: Resource name of the asset
            asset_set_resource_name: Resource name of the asset set

        Returns:
            Created asset set asset details
        """
        try:
            customer_id = format_customer_id(customer_id)

            asset_set_asset = AssetSetAsset()
            asset_set_asset.asset = asset_resource_name
            asset_set_asset.asset_set = asset_set_resource_name

            operation = AssetSetAssetOperation()
            operation.create = asset_set_asset

            request = MutateAssetSetAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAssetSetAssetsResponse = (
                self.client.mutate_asset_set_assets(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added asset to asset set",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add asset to set: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_asset_from_set(
        self,
        ctx: Context,
        customer_id: str,
        asset_set_asset_resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Remove an asset from an asset set.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            asset_set_asset_resource_name: Resource name of the asset set asset link

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)

            operation = AssetSetAssetOperation()
            operation.remove = asset_set_asset_resource_name

            request = MutateAssetSetAssetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateAssetSetAssetsResponse = (
                self.client.mutate_asset_set_assets(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Removed asset from set: {asset_set_asset_resource_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove asset from set: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_asset_set_asset_tools(
    service: AssetSetAssetService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the asset set asset service."""
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def add_asset_to_set(
        ctx: Context,
        customer_id: str,
        asset_resource_name: str,
        asset_set_resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add an asset to an asset set.

        Args:
            customer_id: The customer ID
            asset_resource_name: Resource name of the asset
            asset_set_resource_name: Resource name of the asset set

        Returns:
            Created asset set asset link details
        """
        return await service.add_asset_to_set(
            ctx=ctx,
            customer_id=customer_id,
            asset_resource_name=asset_resource_name,
            asset_set_resource_name=asset_set_resource_name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def remove_asset_from_set(
        ctx: Context,
        customer_id: str,
        asset_set_asset_resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Remove an asset from an asset set.

        Args:
            customer_id: The customer ID
            asset_set_asset_resource_name: Resource name of the asset set asset link

        Returns:
            Removal result
        """
        return await service.remove_asset_from_set(
            ctx=ctx,
            customer_id=customer_id,
            asset_set_asset_resource_name=asset_set_asset_resource_name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    tools.extend([add_asset_to_set, remove_asset_from_set])
    return tools


def register_asset_set_asset_tools(mcp: FastMCP[Any]) -> AssetSetAssetService:
    """Register asset set asset tools with the MCP server."""
    service = AssetSetAssetService()
    tools = create_asset_set_asset_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
