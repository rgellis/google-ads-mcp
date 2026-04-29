"""Asset group listing group filter service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.enums.types.listing_group_filter_product_channel import (
    ListingGroupFilterProductChannelEnum,
)
from google.ads.googleads.v23.enums.types.listing_group_filter_product_condition import (
    ListingGroupFilterProductConditionEnum,
)
from google.ads.googleads.v23.enums.types.listing_group_filter_custom_attribute_index import (
    ListingGroupFilterCustomAttributeIndexEnum,
)
from google.ads.googleads.v23.enums.types.listing_group_filter_product_type_level import (
    ListingGroupFilterProductTypeLevelEnum,
)
from google.ads.googleads.v23.resources.types.asset_group_listing_group_filter import (
    AssetGroupListingGroupFilter,
    ListingGroupFilterDimension,
)
from google.ads.googleads.v23.services.services.asset_group_listing_group_filter_service import (
    AssetGroupListingGroupFilterServiceClient,
)
from google.ads.googleads.v23.services.types.asset_group_listing_group_filter_service import (
    AssetGroupListingGroupFilterOperation,
    MutateAssetGroupListingGroupFiltersRequest,
    MutateAssetGroupListingGroupFiltersResponse,
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


def _build_listing_dimension(
    case_value: Dict[str, Any],
) -> ListingGroupFilterDimension:
    """Build a ListingGroupFilterDimension from a single-key dict.

    Supported keys (each maps to one oneof member):
      - "product_brand": str
      - "product_item_id": str
      - "product_type": {"value": str, "level": str}
      - "product_channel": str (enum like "ONLINE")
      - "product_condition": str (enum like "NEW")
      - "product_custom_attribute": {"value": str, "index": str}

    product_category and webpage are not yet supported by this helper.
    """
    if len(case_value) != 1:
        raise ValueError(
            "case_value must contain exactly one dimension key; got "
            f"{sorted(case_value.keys())}"
        )
    [(dim_key, dim_value)] = case_value.items()
    dim = ListingGroupFilterDimension()
    if dim_key == "product_brand":
        dim.product_brand = ListingGroupFilterDimension.ProductBrand(value=dim_value)
    elif dim_key == "product_item_id":
        dim.product_item_id = ListingGroupFilterDimension.ProductItemId(value=dim_value)
    elif dim_key == "product_type":
        pt = ListingGroupFilterDimension.ProductType(value=dim_value["value"])
        pt.level = getattr(
            ListingGroupFilterProductTypeLevelEnum.ListingGroupFilterProductTypeLevel,
            dim_value["level"],
        )
        dim.product_type = pt
    elif dim_key == "product_channel":
        dim.product_channel = ListingGroupFilterDimension.ProductChannel(
            channel=getattr(
                ListingGroupFilterProductChannelEnum.ListingGroupFilterProductChannel,
                dim_value,
            )
        )
    elif dim_key == "product_condition":
        dim.product_condition = ListingGroupFilterDimension.ProductCondition(
            condition=getattr(
                ListingGroupFilterProductConditionEnum.ListingGroupFilterProductCondition,
                dim_value,
            )
        )
    elif dim_key == "product_custom_attribute":
        pca = ListingGroupFilterDimension.ProductCustomAttribute(
            value=dim_value["value"]
        )
        pca.index = getattr(
            ListingGroupFilterCustomAttributeIndexEnum.ListingGroupFilterCustomAttributeIndex,
            dim_value["index"],
        )
        dim.product_custom_attribute = pca
    else:
        raise ValueError(
            f"Unsupported case_value dimension: {dim_key!r}. Supported: "
            "product_brand, product_item_id, product_type, product_channel, "
            "product_condition, product_custom_attribute."
        )
    return dim


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
        case_value: Optional[Dict[str, Any]] = None,
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
            parent_listing_group_filter: Resource name of parent filter
                (for subdivisions). Required for non-root nodes.
            case_value: Optional dict with one key naming the dimension type
                and its value. Required for non-root nodes. Supported keys:
                "product_brand" (str), "product_item_id" (str),
                "product_type" ({"value": str, "level": str}),
                "product_channel" (str enum: ONLINE, LOCAL, ...),
                "product_condition" (str enum: NEW, USED, REFURBISHED),
                "product_custom_attribute" ({"value": str, "index": str enum}).

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
            if case_value is not None:
                lgf.case_value = _build_listing_dimension(case_value)

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

    async def update_listing_group_filter(
        self,
        ctx: Context,
        customer_id: str,
        listing_group_filter_resource_name: str,
        case_value: Dict[str, Any],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Update a listing group filter's case_value.

        Per the v23 proto, ``type_``, ``listing_source``, ``asset_group``,
        and ``parent_listing_group_filter`` are all Immutable. The only
        mutable field on this resource is ``case_value``. To change a
        node's type or parent, remove and recreate it.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            listing_group_filter_resource_name: Resource name of the listing
                group filter
            case_value: New dimension value (see create_listing_group_filter
                docstring for the dict format)

        Returns:
            Updated listing group filter details
        """
        try:
            customer_id = format_customer_id(customer_id)

            lgf = AssetGroupListingGroupFilter()
            lgf.resource_name = listing_group_filter_resource_name
            lgf.case_value = _build_listing_dimension(case_value)
            update_mask_fields: list[str] = ["case_value"]

            operation = AssetGroupListingGroupFilterOperation()
            operation.update = lgf
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_fields)
            )

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
                message=f"Updated listing group filter: {listing_group_filter_resource_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update listing group filter: {str(e)}"
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
        case_value: Optional[Dict[str, Any]] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a listing group filter for PMax product feed targeting.

        Args:
            customer_id: The customer ID
            asset_group_resource_name: Resource name of the asset group
            filter_type: UNIT_INCLUDED, UNIT_EXCLUDED, or SUBDIVISION
            parent_listing_group_filter: Parent filter resource name
                (for subdivisions). Required for non-root nodes.
            case_value: Dict with one dimension key. Required for non-root
                nodes. Supported keys: product_brand (str),
                product_item_id (str),
                product_type ({"value": str, "level": str}),
                product_channel (str enum: ONLINE, LOCAL, ...),
                product_condition (str enum: NEW, USED, REFURBISHED),
                product_custom_attribute ({"value": str, "index": str enum}).

        Returns:
            Created filter details
        """
        return await service.create_listing_group_filter(
            ctx=ctx,
            customer_id=customer_id,
            asset_group_resource_name=asset_group_resource_name,
            filter_type=filter_type,
            parent_listing_group_filter=parent_listing_group_filter,
            case_value=case_value,
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

    async def update_listing_group_filter(
        ctx: Context,
        customer_id: str,
        listing_group_filter_resource_name: str,
        case_value: Dict[str, Any],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a listing group filter's case_value (the only mutable field).

        Per the v23 proto, the type, parent, listing_source, and asset_group
        are all Immutable. Only case_value can be updated. To change the
        type or parent, remove and recreate the node.

        Args:
            customer_id: The customer ID
            listing_group_filter_resource_name: Resource name of the filter
            case_value: New dimension value (see create_listing_group_filter
                for the dict format)

        Returns:
            Updated filter details
        """
        return await service.update_listing_group_filter(
            ctx=ctx,
            customer_id=customer_id,
            listing_group_filter_resource_name=listing_group_filter_resource_name,
            case_value=case_value,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    tools.extend(
        [
            create_listing_group_filter,
            remove_listing_group_filter,
            update_listing_group_filter,
        ]
    )
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
