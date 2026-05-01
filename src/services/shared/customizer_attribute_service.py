"""Customizer attribute service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.enums.types.customizer_attribute_type import (
    CustomizerAttributeTypeEnum,
)
from google.ads.googleads.v23.resources.types.customizer_attribute import (
    CustomizerAttribute,
)
from google.ads.googleads.v23.services.services.customizer_attribute_service import (
    CustomizerAttributeServiceClient,
)
from google.ads.googleads.v23.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v23.services.types.customizer_attribute_service import (
    CustomizerAttributeOperation,
    MutateCustomizerAttributesRequest,
    MutateCustomizerAttributesResponse,
)
from src.sdk_client import get_sdk_client
from src.utils import (
    format_customer_id,
    get_logger,
    serialize_proto_message,
    set_request_options,
)

logger = get_logger(__name__)


class CustomizerAttributeService:
    """Customizer attribute service for managing ad customizers."""

    def __init__(self) -> None:
        """Initialize the customizer attribute service."""
        self._client: Optional[CustomizerAttributeServiceClient] = None

    @property
    def client(self) -> CustomizerAttributeServiceClient:
        """Get the customizer attribute service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("CustomizerAttributeService")
        assert self._client is not None
        return self._client

    async def create_customizer_attribute(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        attribute_type: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a customizer attribute.

        Note: ``CustomizerAttribute.status`` is Output-only per the v23
        ref. ``name`` and ``type`` are both Immutable, so once created
        the attribute has no mutable fields.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: Name of the customizer attribute
            attribute_type: Type of attribute (TEXT, NUMBER, PRICE, PERCENT)

        Returns:
            Created customizer attribute details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create customizer attribute
            attribute = CustomizerAttribute()
            attribute.name = name
            attribute.type_ = getattr(
                CustomizerAttributeTypeEnum.CustomizerAttributeType, attribute_type
            )

            # Create operation
            operation = CustomizerAttributeOperation()
            operation.create = attribute

            # Create request
            request = MutateCustomizerAttributesRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateCustomizerAttributesResponse = (
                self.client.mutate_customizer_attributes(request=request)
            )

            await ctx.log(
                level="info", message=f"Created customizer attribute '{name}'"
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create customizer attribute: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    # update_customizer_attribute was removed — CustomizerAttribute has
    # no mutable fields per the v23 ref: ``name`` and ``type`` are
    # Immutable, ``status`` is Output-only, ``id``/``resource_name`` are
    # server-managed. The previous wrapper accepted ``status``, added
    # "status" to the update_mask without ever assigning a value, and
    # would either fail or no-op. Use ``remove_customizer_attribute`` to
    # delete an attribute; create a new one to change anything.

    async def list_customizer_attributes(
        self,
        ctx: Context,
        customer_id: str,
        include_removed: bool = False,
    ) -> List[Dict[str, Any]]:
        """List customizer attributes.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            include_removed: Whether to include removed attributes

        Returns:
            List of customizer attributes
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
                    customizer_attribute.resource_name,
                    customizer_attribute.id,
                    customizer_attribute.name,
                    customizer_attribute.type,
                    customizer_attribute.status
                FROM customizer_attribute
            """

            conditions: List[str] = []
            if not include_removed:
                conditions.append("customizer_attribute.status != 'REMOVED'")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY customizer_attribute.name"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            attributes = []
            for row in response:
                attribute = row.customizer_attribute

                attribute_dict = {
                    "resource_name": attribute.resource_name,
                    "id": str(attribute.id),
                    "name": attribute.name,
                    "type": attribute.type_.name if attribute.type_ else "UNKNOWN",
                    "status": attribute.status.name if attribute.status else "UNKNOWN",
                }

                attributes.append(attribute_dict)

            await ctx.log(
                level="info",
                message=f"Found {len(attributes)} customizer attributes",
            )

            return attributes

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to list customizer attributes: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_customizer_attribute(
        self,
        ctx: Context,
        customer_id: str,
        attribute_resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Remove a customizer attribute.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            attribute_resource_name: Resource name of the attribute to remove

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create operation
            operation = CustomizerAttributeOperation()
            operation.remove = attribute_resource_name

            # Create request
            request = MutateCustomizerAttributesRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response = self.client.mutate_customizer_attributes(request=request)

            await ctx.log(
                level="info",
                message="Removed customizer attribute",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove customizer attribute: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_customizer_attribute_tools(
    service: CustomizerAttributeService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the customizer attribute service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_customizer_attribute(
        ctx: Context,
        customer_id: str,
        name: str,
        attribute_type: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a customizer attribute for ad customization.

        Note: ``CustomizerAttribute.status`` is Output-only per the v23
        ref. There is no update tool — name and type are Immutable, so
        once created the attribute has no mutable fields.

        Args:
            customer_id: The customer ID
            name: Name of the customizer attribute (will be used in ad text placeholders)
            attribute_type: Type of attribute - TEXT, NUMBER, PRICE, or PERCENT
            partial_failure: If True, valid operations succeed when others fail in the same request.
            validate_only: If True, validate the request without executing it.
            response_content_type: Optional response-content-type override (e.g. 'MUTABLE_RESOURCE').


        """
        return await service.create_customizer_attribute(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            attribute_type=attribute_type,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def list_customizer_attributes(
        ctx: Context,
        customer_id: str,
        include_removed: bool = False,
    ) -> List[Dict[str, Any]]:
        """List customizer attributes.

        For filters beyond the structured params here (substring-on-name,
        date ranges, metric thresholds, custom SELECT/ORDER BY,
        multi-condition AND/OR), use ``search_google_ads`` with a
        free-form GAQL query.

        Args:
            customer_id: The customer ID
            include_removed: Whether to include removed attributes

        Returns:
            List of customizer attributes with details
        """
        return await service.list_customizer_attributes(
            ctx=ctx,
            customer_id=customer_id,
            include_removed=include_removed,
        )

    async def remove_customizer_attribute(
        ctx: Context,
        customer_id: str,
        attribute_resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Remove a customizer attribute.

        Args:
            customer_id: The customer ID
            attribute_resource_name: Resource name of the attribute to remove

        Returns:
            Removal result with status
        """
        return await service.remove_customizer_attribute(
            ctx=ctx,
            customer_id=customer_id,
            attribute_resource_name=attribute_resource_name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    tools.extend(
        [
            create_customizer_attribute,
            list_customizer_attributes,
            remove_customizer_attribute,
        ]
    )
    return tools


def register_customizer_attribute_tools(
    mcp: FastMCP[Any],
) -> CustomizerAttributeService:
    """Register customizer attribute tools with the MCP server.

    Returns the CustomizerAttributeService instance for testing purposes.
    """
    service = CustomizerAttributeService()
    tools = create_customizer_attribute_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
