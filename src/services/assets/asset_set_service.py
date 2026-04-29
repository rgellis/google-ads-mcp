"""Asset set service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.enums.types.asset_set_status import AssetSetStatusEnum
from google.ads.googleads.v23.enums.types.asset_set_type import AssetSetTypeEnum
from google.ads.googleads.v23.resources.types.asset_set import AssetSet
from google.ads.googleads.v23.services.services.asset_set_service import (
    AssetSetServiceClient,
)
from google.ads.googleads.v23.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v23.services.types.asset_set_service import (
    AssetSetOperation,
    MutateAssetSetsRequest,
    MutateAssetSetsResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import (
    format_customer_id,
    get_logger,
    serialize_proto_message,
    set_request_options,
)

logger = get_logger(__name__)


class AssetSetService:
    """Asset set service for managing collections of assets."""

    def __init__(self) -> None:
        """Initialize the asset set service."""
        self._client: Optional[AssetSetServiceClient] = None

    @property
    def client(self) -> AssetSetServiceClient:
        """Get the asset set service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("AssetSetService")
        assert self._client is not None
        return self._client

    async def create_asset_set(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        asset_set_type: AssetSetTypeEnum.AssetSetType,
        status: AssetSetStatusEnum.AssetSetStatus = AssetSetStatusEnum.AssetSetStatus.ENABLED,
        merchant_id: Optional[int] = None,
        feed_label: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a new asset set.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: Asset set name
            asset_set_type: Type of asset set. Supported by this wrapper:
                MERCHANT_CENTER_FEED (requires merchant_id) and the
                "dynamic" types (DYNAMIC_EDUCATION, DYNAMIC_REAL_ESTATE,
                DYNAMIC_FLIGHTS, DYNAMIC_HOTELS_AND_RENTALS, DYNAMIC_TRAVEL,
                DYNAMIC_LOCAL, DYNAMIC_JOBS, DYNAMIC_CUSTOM, PAGE_FEED,
                STATIC_LOCATION_GROUP). Location-sync, business-profile, and
                chain-location types need their own submessages and are not
                supported by this wrapper yet.
            status: Asset set status (ENABLED, REMOVED)
            merchant_id: Merchant Center merchant ID. Required when
                asset_set_type is MERCHANT_CENTER_FEED.
            feed_label: Optional Merchant Center feed label
                (only used when asset_set_type is MERCHANT_CENTER_FEED).

        Returns:
            Created asset set details
        """
        # Restrict to types this wrapper can actually populate. The
        # unsupported types require submessage builders we haven't written.
        unsupported_types = {
            AssetSetTypeEnum.AssetSetType.LOCATION_SYNC,
            AssetSetTypeEnum.AssetSetType.BUSINESS_PROFILE_DYNAMIC_LOCATION_GROUP,
            AssetSetTypeEnum.AssetSetType.CHAIN_DYNAMIC_LOCATION_GROUP,
            AssetSetTypeEnum.AssetSetType.STATIC_LOCATION_GROUP,
            AssetSetTypeEnum.AssetSetType.HOTEL_PROPERTY,
        }
        if asset_set_type in unsupported_types:
            raise NotImplementedError(
                f"asset_set_type={asset_set_type.name} requires a source "
                "submessage (location_set / business_profile_location_group / "
                "chain_location_group / hotel_property_data) that this wrapper "
                "does not yet expose."
            )

        merchant_center_type = AssetSetTypeEnum.AssetSetType.MERCHANT_CENTER_FEED
        if asset_set_type == merchant_center_type and merchant_id is None:
            raise ValueError(
                "merchant_id is required when asset_set_type is MERCHANT_CENTER_FEED."
            )
        if asset_set_type != merchant_center_type and (
            merchant_id is not None or feed_label is not None
        ):
            raise ValueError(
                "merchant_id and feed_label are only valid for "
                "MERCHANT_CENTER_FEED asset sets."
            )

        try:
            customer_id = format_customer_id(customer_id)

            # Create asset set
            asset_set = AssetSet()
            asset_set.name = name
            asset_set.type_ = asset_set_type
            asset_set.status = status

            if asset_set_type == merchant_center_type:
                asset_set.merchant_center_feed.merchant_id = merchant_id  # type: ignore[arg-type]
                if feed_label is not None:
                    asset_set.merchant_center_feed.feed_label = feed_label

            # Create operation
            operation = AssetSetOperation()
            operation.create = asset_set

            # Create request
            request = MutateAssetSetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateAssetSetsResponse = self.client.mutate_asset_sets(
                request=request
            )

            await ctx.log(level="info", message=f"Created asset set '{name}'")

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create asset set: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_asset_set(
        self,
        ctx: Context,
        customer_id: str,
        asset_set_id: str,
        name: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Update an asset set.

        Per the v23 AssetSet proto, ``status`` is ``Output only.
        Read-only`` and cannot be updated. Use ``remove_asset_set`` to
        remove an asset set.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            asset_set_id: The asset set ID to update
            name: Optional new name

        Returns:
            Updated asset set details
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/assetSets/{asset_set_id}"

            # Create asset set with resource name
            asset_set = AssetSet()
            asset_set.resource_name = resource_name

            # Build update mask
            update_mask_paths = []

            if name is not None:
                asset_set.name = name
                update_mask_paths.append("name")

            if not update_mask_paths:
                raise ValueError("name must be provided to update.")

            # Create operation
            operation = AssetSetOperation()
            operation.update = asset_set
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_paths)
            )

            # Create request
            request = MutateAssetSetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response = self.client.mutate_asset_sets(request=request)

            await ctx.log(
                level="info",
                message=f"Updated asset set {asset_set_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update asset set: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_asset_sets(
        self,
        ctx: Context,
        customer_id: str,
        asset_set_type: Optional[str] = None,
        include_removed: bool = False,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """List asset sets.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            asset_set_type: Optional asset set type to filter by
            include_removed: Whether to include removed asset sets
            limit: Maximum number of results

        Returns:
            List of asset sets
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
                    asset_set.id,
                    asset_set.name,
                    asset_set.type,
                    asset_set.status,
                    asset_set.resource_name
                FROM asset_set
            """

            conditions = []
            if not include_removed:
                conditions.append("asset_set.status != 'REMOVED'")
            if asset_set_type:
                conditions.append(f"asset_set.type = '{asset_set_type}'")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += f" ORDER BY asset_set.id DESC LIMIT {limit}"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            asset_sets = []
            for row in response:
                asset_set = row.asset_set

                asset_set_dict = {
                    "asset_set_id": str(asset_set.id),
                    "name": asset_set.name,
                    "type": asset_set.type_.name if asset_set.type_ else "UNKNOWN",
                    "status": asset_set.status.name if asset_set.status else "UNKNOWN",
                    "resource_name": asset_set.resource_name,
                }

                asset_sets.append(asset_set_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(asset_sets)} asset sets",
            )

            return asset_sets

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to list asset sets: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_asset_set(
        self,
        ctx: Context,
        customer_id: str,
        asset_set_id: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Remove an asset set.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            asset_set_id: The asset set ID to remove

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/assetSets/{asset_set_id}"

            # Create operation
            operation = AssetSetOperation()
            operation.remove = resource_name

            # Create request
            request = MutateAssetSetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response = self.client.mutate_asset_sets(request=request)

            await ctx.log(
                level="info",
                message=f"Removed asset set {asset_set_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove asset set: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_asset_set_tools(
    service: AssetSetService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the asset set service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_asset_set(
        ctx: Context,
        customer_id: str,
        name: str,
        asset_set_type: str,
        status: str = "ENABLED",
        merchant_id: Optional[int] = None,
        feed_label: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new asset set.

        Args:
            customer_id: The customer ID
            name: Asset set name
            asset_set_type: Type of asset set. Supported values:
                - MERCHANT_CENTER_FEED (requires merchant_id)
                - DYNAMIC_EDUCATION
                - DYNAMIC_FLIGHTS
                - DYNAMIC_HOTELS_AND_RENTALS
                - DYNAMIC_JOBS
                - DYNAMIC_LOCAL
                - DYNAMIC_REAL_ESTATE
                - DYNAMIC_CUSTOM
                - DYNAMIC_TRAVEL
                - PAGE_FEED
                Location-sync, business-profile, chain, hotel-property, and
                static-location-group types require source submessages this
                wrapper does not yet expose; pass them and the wrapper
                raises NotImplementedError.
            status: Asset set status - ENABLED or REMOVED
            merchant_id: Required when asset_set_type=MERCHANT_CENTER_FEED.
                Merchant Center merchant ID.
            feed_label: Optional Merchant Center feed label (only valid for
                MERCHANT_CENTER_FEED).

        Returns:
            Created asset set details including resource_name and asset_set_id
        """
        # Convert string enums to proper enum types
        asset_set_type_enum = getattr(AssetSetTypeEnum.AssetSetType, asset_set_type)
        status_enum = getattr(AssetSetStatusEnum.AssetSetStatus, status)

        return await service.create_asset_set(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            asset_set_type=asset_set_type_enum,
            status=status_enum,
            merchant_id=merchant_id,
            feed_label=feed_label,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def update_asset_set(
        ctx: Context,
        customer_id: str,
        asset_set_id: str,
        name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an asset set.

        Per the v23 proto, ``status`` is Output-only and cannot be
        updated. To remove an asset set, call ``remove_asset_set``.

        Args:
            customer_id: The customer ID
            asset_set_id: The asset set ID to update
            name: New name. Required (only mutable field on AssetSet).

        Returns:
            Updated asset set details with list of updated fields
        """
        return await service.update_asset_set(
            ctx=ctx,
            customer_id=customer_id,
            asset_set_id=asset_set_id,
            name=name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def list_asset_sets(
        ctx: Context,
        customer_id: str,
        asset_set_type: Optional[str] = None,
        include_removed: bool = False,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """List asset sets.

        Args:
            customer_id: The customer ID
            asset_set_type: Optional asset set type to filter by
            include_removed: Whether to include removed asset sets
            limit: Maximum number of results

        Returns:
            List of asset sets with details
        """
        return await service.list_asset_sets(
            ctx=ctx,
            customer_id=customer_id,
            asset_set_type=asset_set_type,
            include_removed=include_removed,
            limit=limit,
        )

    async def remove_asset_set(
        ctx: Context,
        customer_id: str,
        asset_set_id: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Remove an asset set.

        Args:
            customer_id: The customer ID
            asset_set_id: The asset set ID to remove

        Returns:
            Removal result with status
        """
        return await service.remove_asset_set(
            ctx=ctx,
            customer_id=customer_id,
            asset_set_id=asset_set_id,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    tools.extend(
        [
            create_asset_set,
            update_asset_set,
            list_asset_sets,
            remove_asset_set,
        ]
    )
    return tools


def register_asset_set_tools(mcp: FastMCP[Any]) -> AssetSetService:
    """Register asset set tools with the MCP server.

    Returns the AssetSetService instance for testing purposes.
    """
    service = AssetSetService()
    tools = create_asset_set_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
