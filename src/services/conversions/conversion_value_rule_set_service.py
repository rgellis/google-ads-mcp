"""Conversion value rule set service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.resources.types.conversion_value_rule_set import (
    ConversionValueRuleSet,
)
from google.ads.googleads.v23.services.services.conversion_value_rule_set_service import (
    ConversionValueRuleSetServiceClient,
)
from google.ads.googleads.v23.services.types.conversion_value_rule_set_service import (
    ConversionValueRuleSetOperation,
    MutateConversionValueRuleSetsRequest,
    MutateConversionValueRuleSetsResponse,
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


class ConversionValueRuleSetService:
    """Service for managing conversion value rule sets."""

    def __init__(self) -> None:
        self._client: Optional[ConversionValueRuleSetServiceClient] = None

    @property
    def client(self) -> ConversionValueRuleSetServiceClient:
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service(
                "ConversionValueRuleSetService"
            )
        assert self._client is not None
        return self._client

    async def create_conversion_value_rule_set(
        self,
        ctx: Context,
        customer_id: str,
        dimensions: List[str],
        conversion_value_rules: List[str],
        attachment_type: str,
        campaign: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a conversion value rule set.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            dimensions: List of dimensions (GEO_LOCATION, DEVICE, AUDIENCE, NO_CONDITION)
            conversion_value_rules: List of conversion value rule resource names
            attachment_type: Attachment type (CUSTOMER, CAMPAIGN)
            campaign: Campaign resource name (required if attachment_type is CAMPAIGN)

        Returns:
            Created conversion value rule set details
        """
        try:
            customer_id = format_customer_id(customer_id)

            from google.ads.googleads.v23.enums.types.value_rule_set_attachment_type import (
                ValueRuleSetAttachmentTypeEnum,
            )
            from google.ads.googleads.v23.enums.types.value_rule_set_dimension import (
                ValueRuleSetDimensionEnum,
            )

            rule_set = ConversionValueRuleSet()
            rule_set.dimensions = [
                getattr(ValueRuleSetDimensionEnum.ValueRuleSetDimension, d)
                for d in dimensions
            ]
            rule_set.conversion_value_rules = conversion_value_rules
            rule_set.attachment_type = getattr(
                ValueRuleSetAttachmentTypeEnum.ValueRuleSetAttachmentType,
                attachment_type,
            )
            if campaign:
                rule_set.campaign = campaign

            operation = ConversionValueRuleSetOperation()
            operation.create = rule_set

            request = MutateConversionValueRuleSetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateConversionValueRuleSetsResponse = (
                self.client.mutate_conversion_value_rule_sets(request=request)
            )

            await ctx.log(level="info", message="Created conversion value rule set")

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create conversion value rule set: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_conversion_value_rule_set(
        self,
        ctx: Context,
        customer_id: str,
        resource_name: str,
        conversion_value_rules: Optional[List[str]] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Update a conversion value rule set.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            resource_name: Resource name of the rule set
            conversion_value_rules: New list of rule resource names

        Returns:
            Updated conversion value rule set details
        """
        try:
            customer_id = format_customer_id(customer_id)

            rule_set = ConversionValueRuleSet()
            rule_set.resource_name = resource_name

            update_mask_fields = []
            if conversion_value_rules is not None:
                rule_set.conversion_value_rules = conversion_value_rules
                update_mask_fields.append("conversion_value_rules")

            operation = ConversionValueRuleSetOperation()
            operation.update = rule_set
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_fields)
            )

            request = MutateConversionValueRuleSetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateConversionValueRuleSetsResponse = (
                self.client.mutate_conversion_value_rule_sets(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Updated conversion value rule set {resource_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update conversion value rule set: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_conversion_value_rule_set(
        self,
        ctx: Context,
        customer_id: str,
        resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Remove a conversion value rule set.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            resource_name: Resource name of the rule set

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)

            operation = ConversionValueRuleSetOperation()
            operation.remove = resource_name

            request = MutateConversionValueRuleSetsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateConversionValueRuleSetsResponse = (
                self.client.mutate_conversion_value_rule_sets(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Removed conversion value rule set: {resource_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove conversion value rule set: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_conversion_value_rule_set_tools(
    service: ConversionValueRuleSetService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the conversion value rule set service."""
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def create_conversion_value_rule_set(
        ctx: Context,
        customer_id: str,
        dimensions: List[str],
        conversion_value_rules: List[str],
        attachment_type: str,
        campaign: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a conversion value rule set to group value rules.

        Args:
            customer_id: The customer ID
            dimensions: Dimensions - GEO_LOCATION, DEVICE, AUDIENCE, NO_CONDITION
            conversion_value_rules: List of conversion value rule resource names
            attachment_type: CUSTOMER or CAMPAIGN
            campaign: Campaign resource name (required for CAMPAIGN attachment)

        Returns:
            Created rule set details
        """
        return await service.create_conversion_value_rule_set(
            ctx=ctx,
            customer_id=customer_id,
            dimensions=dimensions,
            conversion_value_rules=conversion_value_rules,
            attachment_type=attachment_type,
            campaign=campaign,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def update_conversion_value_rule_set(
        ctx: Context,
        customer_id: str,
        resource_name: str,
        conversion_value_rules: Optional[List[str]] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a conversion value rule set.

        Args:
            customer_id: The customer ID
            resource_name: Resource name of the rule set
            conversion_value_rules: New list of rule resource names

        Returns:
            Updated rule set details
        """
        return await service.update_conversion_value_rule_set(
            ctx=ctx,
            customer_id=customer_id,
            resource_name=resource_name,
            conversion_value_rules=conversion_value_rules,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def remove_conversion_value_rule_set(
        ctx: Context,
        customer_id: str,
        resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Remove a conversion value rule set.

        Args:
            customer_id: The customer ID
            resource_name: Resource name of the rule set

        Returns:
            Removal result
        """
        return await service.remove_conversion_value_rule_set(
            ctx=ctx,
            customer_id=customer_id,
            resource_name=resource_name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    tools.extend(
        [
            create_conversion_value_rule_set,
            update_conversion_value_rule_set,
            remove_conversion_value_rule_set,
        ]
    )
    return tools


def register_conversion_value_rule_set_tools(
    mcp: FastMCP[Any],
) -> ConversionValueRuleSetService:
    """Register conversion value rule set tools with the MCP server."""
    service = ConversionValueRuleSetService()
    tools = create_conversion_value_rule_set_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
