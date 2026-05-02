"""Asset set service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
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
    gaql_enum_name,
    gaql_int,
    get_logger,
    serialize_proto_message,
    set_optional_submessage,
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
        merchant_id: Optional[int] = None,
        feed_label: Optional[str] = None,
        location_group_parent_asset_set_id: Optional[int] = None,
        location_set: Optional[Dict[str, Any]] = None,
        business_profile_location_group: Optional[Dict[str, Any]] = None,
        chain_location_group: Optional[Dict[str, Any]] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a new asset set.

        Note: ``AssetSet.status`` is Output-only per the v23 ref. The
        wrapper does not expose it on create.

        ``location_set``, ``business_profile_location_group``, and
        ``chain_location_group`` are members of the AssetSet
        ``asset_set_source`` oneof. Pass at most one of them, and only
        when ``asset_set_type`` is the matching location source.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: Asset set name
            asset_set_type: Type of asset set. Supported by this wrapper:
                MERCHANT_CENTER_FEED (requires merchant_id), all "dynamic"
                types (DYNAMIC_EDUCATION, DYNAMIC_REAL_ESTATE,
                DYNAMIC_FLIGHTS, DYNAMIC_HOTELS_AND_RENTALS, DYNAMIC_TRAVEL,
                DYNAMIC_LOCAL, DYNAMIC_JOBS, DYNAMIC_CUSTOM, PAGE_FEED,
                STATIC_LOCATION_GROUP), and the location-source types
                (LOCATION_SYNC, BUSINESS_PROFILE_DYNAMIC_LOCATION_GROUP,
                CHAIN_DYNAMIC_LOCATION_GROUP) when the matching source dict
                is supplied. HOTEL_PROPERTY is API-managed and remains
                unsupported by create.
            merchant_id: Merchant Center merchant ID. Required when
                asset_set_type is MERCHANT_CENTER_FEED.
            feed_label: Optional Merchant Center feed label
                (only used when asset_set_type is MERCHANT_CENTER_FEED).
            location_group_parent_asset_set_id: Immutable. Required for
                Location Group typed AssetSets — the sync-level location
                AssetSet ID this LocationGroup AssetSet derives from.
            location_set: Immutable. Dict that builds a ``LocationSet``
                submessage. Required when asset_set_type is LOCATION_SYNC.
                See the v23 ``LocationSet`` proto reference for the schema.
            business_profile_location_group: Immutable. Dict that builds
                a ``BusinessProfileLocationGroup`` submessage. Required
                when asset_set_type is BUSINESS_PROFILE_DYNAMIC_LOCATION_GROUP.
            chain_location_group: Immutable. Dict that builds a
                ``ChainLocationGroup`` submessage. Required when
                asset_set_type is CHAIN_DYNAMIC_LOCATION_GROUP.

        Returns:
            Created asset set details
        """
        if asset_set_type == AssetSetTypeEnum.AssetSetType.HOTEL_PROPERTY:
            raise NotImplementedError(
                "asset_set_type=HOTEL_PROPERTY is API-managed (created by "
                "linking a Hotel Center account); the wrapper does not "
                "support direct creation."
            )

        # Mutually exclusive source dicts; at most one
        sources_supplied = sum(
            1
            for v in (
                location_set,
                business_profile_location_group,
                chain_location_group,
            )
            if v is not None
        )
        if sources_supplied > 1:
            raise ValueError(
                "location_set, business_profile_location_group, and "
                "chain_location_group are members of the AssetSet "
                "asset_set_source oneof — pass at most one."
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

            if asset_set_type == merchant_center_type:
                asset_set.merchant_center_feed.merchant_id = merchant_id  # type: ignore[arg-type]
                if feed_label is not None:
                    asset_set.merchant_center_feed.feed_label = feed_label

            if location_group_parent_asset_set_id is not None:
                asset_set.location_group_parent_asset_set_id = (
                    location_group_parent_asset_set_id
                )

            if location_set is not None:
                from google.ads.googleads.v23.common.types.asset_set_types import (
                    LocationSet,
                )

                set_optional_submessage(
                    asset_set, "location_set", location_set, LocationSet
                )
            if business_profile_location_group is not None:
                from google.ads.googleads.v23.common.types.asset_set_types import (
                    BusinessProfileLocationGroup,
                )

                set_optional_submessage(
                    asset_set,
                    "business_profile_location_group",
                    business_profile_location_group,
                    BusinessProfileLocationGroup,
                )
            if chain_location_group is not None:
                from google.ads.googleads.v23.common.types.asset_set_types import (
                    ChainLocationGroup,
                )

                set_optional_submessage(
                    asset_set,
                    "chain_location_group",
                    chain_location_group,
                    ChainLocationGroup,
                )

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
        """List asset sets on a customer, optionally filtered by type or status. Asset sets group related assets (locations, hotel properties, dynamic feeds) for linking to campaigns or ad groups; this returns each set's resource_name, id, name, type, status, and any business-profile / location-group / hotel-property submessage. For substring-on-name, date ranges, metric thresholds, custom SELECT/ORDER BY, or multi-condition filters, use ``search_google_ads`` with a free-form GAQL query.

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
                conditions.append(
                    f"asset_set.type = '{gaql_enum_name(asset_set_type, 'asset_set_type')}'"
                )

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += f" ORDER BY asset_set.id DESC LIMIT {gaql_int(limit, 'limit')}"

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
        merchant_id: Optional[int] = None,
        feed_label: Optional[str] = None,
        location_group_parent_asset_set_id: Optional[int] = None,
        location_set: Optional[Dict[str, Any]] = None,
        business_profile_location_group: Optional[Dict[str, Any]] = None,
        chain_location_group: Optional[Dict[str, Any]] = None,
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
                - DYNAMIC_EDUCATION / DYNAMIC_FLIGHTS / DYNAMIC_HOTELS_AND_RENTALS /
                  DYNAMIC_JOBS / DYNAMIC_LOCAL / DYNAMIC_REAL_ESTATE /
                  DYNAMIC_CUSTOM / DYNAMIC_TRAVEL / PAGE_FEED /
                  STATIC_LOCATION_GROUP
                - LOCATION_SYNC (requires ``location_set``)
                - BUSINESS_PROFILE_DYNAMIC_LOCATION_GROUP (requires
                  ``business_profile_location_group``)
                - CHAIN_DYNAMIC_LOCATION_GROUP (requires
                  ``chain_location_group``)
                HOTEL_PROPERTY is API-managed and not supported by create.
            merchant_id: Required when asset_set_type=MERCHANT_CENTER_FEED.
                Merchant Center merchant ID.
            feed_label: Optional Merchant Center feed label (only valid for
                MERCHANT_CENTER_FEED).
            location_group_parent_asset_set_id: Immutable. Required for
                Location Group typed AssetSets — the sync-level location
                AssetSet ID that this LocationGroup AssetSet derives from.
            location_set: Immutable. Dict that builds a ``LocationSet``
                submessage. Required when asset_set_type=LOCATION_SYNC.
                See the v23 LocationSet proto reference.
            business_profile_location_group: Immutable. Dict that builds
                a ``BusinessProfileLocationGroup`` submessage. Required
                when asset_set_type=BUSINESS_PROFILE_DYNAMIC_LOCATION_GROUP.
            chain_location_group: Immutable. Dict that builds a
                ``ChainLocationGroup`` submessage. Required when
                asset_set_type=CHAIN_DYNAMIC_LOCATION_GROUP.
            partial_failure: If True, valid operations succeed when others fail in the same request.
            validate_only: If True, validate the request without executing it.
            response_content_type: Optional response-content-type override (e.g. 'MUTABLE_RESOURCE').


        """
        # Convert string enums to proper enum types
        asset_set_type_enum = getattr(AssetSetTypeEnum.AssetSetType, asset_set_type)

        return await service.create_asset_set(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            asset_set_type=asset_set_type_enum,
            merchant_id=merchant_id,
            feed_label=feed_label,
            location_group_parent_asset_set_id=location_group_parent_asset_set_id,
            location_set=location_set,
            business_profile_location_group=business_profile_location_group,
            chain_location_group=chain_location_group,
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
            partial_failure: If True, valid operations succeed when others fail in the same request.
            validate_only: If True, validate the request without executing it.
            response_content_type: Optional response-content-type override (e.g. 'MUTABLE_RESOURCE').


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
        """List asset sets on a customer, optionally filtered by type or status. Asset sets group related assets (locations, hotel properties, dynamic feeds) for linking to campaigns or ad groups; this returns each set's resource_name, id, name, type, status, and any business-profile / location-group / hotel-property submessage. For substring-on-name, date ranges, metric thresholds, custom SELECT/ORDER BY, or multi-condition filters, use ``search_google_ads`` with a free-form GAQL query.

        For filters beyond the structured params here (substring-on-name,
        date ranges, metric thresholds, custom SELECT/ORDER BY,
        multi-condition AND/OR), use ``search_google_ads`` with a
        free-form GAQL query.

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
