"""Google Ads Keyword Plan Ad Group Service

This module provides functionality for managing keyword plan ad groups in Google Ads.
Keyword plan ad groups organize keywords within keyword plan campaigns for planning purposes.
"""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.resources.types.keyword_plan_ad_group import (
    KeywordPlanAdGroup,
)
from google.ads.googleads.v23.services.services.keyword_plan_ad_group_service import (
    KeywordPlanAdGroupServiceClient,
)
from google.ads.googleads.v23.services.types.keyword_plan_ad_group_service import (
    KeywordPlanAdGroupOperation,
    MutateKeywordPlanAdGroupsRequest,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class KeywordPlanAdGroupService:
    """Service for managing Google Ads keyword plan ad groups."""

    def __init__(self) -> None:
        """Initialize the keyword plan ad group service."""
        self._client: Optional[KeywordPlanAdGroupServiceClient] = None

    @property
    def client(self) -> KeywordPlanAdGroupServiceClient:
        """Get the keyword plan ad group service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("KeywordPlanAdGroupService")
        assert self._client is not None
        return self._client

    async def mutate_keyword_plan_ad_groups(
        self,
        ctx: Context,
        customer_id: str,
        operations: List[KeywordPlanAdGroupOperation],
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Mutate keyword plan ad groups.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            operations: List of keyword plan ad group operations
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate the request

        Returns:
            Serialized response containing results
        """
        try:
            customer_id = format_customer_id(customer_id)
            request = MutateKeywordPlanAdGroupsRequest(
                customer_id=customer_id,
                operations=operations,
                partial_failure=partial_failure,
                validate_only=validate_only,
            )
            response = self.client.mutate_keyword_plan_ad_groups(request=request)
            await ctx.log(
                level="info",
                message=f"Successfully mutated {len(response.results)} keyword plan ad groups",
            )
            return serialize_proto_message(response)
        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to mutate keyword plan ad groups: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    def create_keyword_plan_ad_group_operation(
        self,
        keyword_plan_campaign: str,
        name: str,
        cpc_bid_micros: Optional[int] = None,
    ) -> KeywordPlanAdGroupOperation:
        """Create a keyword plan ad group operation for creation.

        Args:
            keyword_plan_campaign: The keyword plan campaign resource name
            name: The name of the keyword plan ad group
            cpc_bid_micros: Default CPC bid in micros

        Returns:
            KeywordPlanAdGroupOperation: The operation to create the keyword plan ad group
        """
        keyword_plan_ad_group = KeywordPlanAdGroup(
            keyword_plan_campaign=keyword_plan_campaign,
            name=name,
        )

        if cpc_bid_micros is not None:
            keyword_plan_ad_group.cpc_bid_micros = cpc_bid_micros

        return KeywordPlanAdGroupOperation(create=keyword_plan_ad_group)

    def update_keyword_plan_ad_group_operation(
        self,
        resource_name: str,
        name: Optional[str] = None,
        cpc_bid_micros: Optional[int] = None,
    ) -> KeywordPlanAdGroupOperation:
        """Create a keyword plan ad group operation for update.

        Args:
            resource_name: The keyword plan ad group resource name
            name: The name of the keyword plan ad group
            cpc_bid_micros: Default CPC bid in micros

        Returns:
            KeywordPlanAdGroupOperation: The operation to update the keyword plan ad group
        """
        keyword_plan_ad_group = KeywordPlanAdGroup(resource_name=resource_name)

        update_mask = []
        if name is not None:
            keyword_plan_ad_group.name = name
            update_mask.append("name")
        if cpc_bid_micros is not None:
            keyword_plan_ad_group.cpc_bid_micros = cpc_bid_micros
            update_mask.append("cpc_bid_micros")

        return KeywordPlanAdGroupOperation(
            update=keyword_plan_ad_group,
            update_mask={"paths": update_mask},
        )

    def remove_keyword_plan_ad_group_operation(
        self, resource_name: str
    ) -> KeywordPlanAdGroupOperation:
        """Create a keyword plan ad group operation for removal.

        Args:
            resource_name: The keyword plan ad group resource name

        Returns:
            KeywordPlanAdGroupOperation: The operation to remove the keyword plan ad group
        """
        return KeywordPlanAdGroupOperation(remove=resource_name)


def create_keyword_plan_ad_group_tools(
    service: KeywordPlanAdGroupService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create keyword plan ad group tools for MCP."""
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def mutate_keyword_plan_ad_groups(
        ctx: Context,
        customer_id: str,
        operations: list[dict[str, Any]],
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Create, update, or remove keyword plan ad groups.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            operations: List of keyword plan ad group operations
            partial_failure: Enable partial failure
            validate_only: Only validate the request

        Returns:
            Serialized response with operation results
        """
        ops = []
        for op_data in operations:
            op_type = op_data["operation_type"]

            if op_type == "create":
                operation = service.create_keyword_plan_ad_group_operation(
                    keyword_plan_campaign=op_data["keyword_plan_campaign"],
                    name=op_data["name"],
                    cpc_bid_micros=op_data.get("cpc_bid_micros"),
                )
            elif op_type == "update":
                operation = service.update_keyword_plan_ad_group_operation(
                    resource_name=op_data["resource_name"],
                    name=op_data.get("name"),
                    cpc_bid_micros=op_data.get("cpc_bid_micros"),
                )
            elif op_type == "remove":
                operation = service.remove_keyword_plan_ad_group_operation(
                    resource_name=op_data["resource_name"]
                )
            else:
                raise ValueError(f"Invalid operation type: {op_type}")

            ops.append(operation)

        return await service.mutate_keyword_plan_ad_groups(
            ctx=ctx,
            customer_id=customer_id,
            operations=ops,
            partial_failure=partial_failure,
            validate_only=validate_only,
        )

    tools.append(mutate_keyword_plan_ad_groups)

    async def create_keyword_plan_ad_group(
        ctx: Context,
        customer_id: str,
        keyword_plan_campaign: str,
        name: str,
        cpc_bid_micros: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a new keyword plan ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            keyword_plan_campaign: The keyword plan campaign resource name
            name: Name of the keyword plan ad group
            cpc_bid_micros: Default CPC bid in micros

        Returns:
            Serialized response with created keyword plan ad group details
        """
        operation = service.create_keyword_plan_ad_group_operation(
            keyword_plan_campaign=keyword_plan_campaign,
            name=name,
            cpc_bid_micros=cpc_bid_micros,
        )

        return await service.mutate_keyword_plan_ad_groups(
            ctx=ctx, customer_id=customer_id, operations=[operation]
        )

    tools.append(create_keyword_plan_ad_group)

    async def update_keyword_plan_ad_group(
        ctx: Context,
        customer_id: str,
        resource_name: str,
        name: Optional[str] = None,
        cpc_bid_micros: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Update an existing keyword plan ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            resource_name: The keyword plan ad group resource name
            name: Name of the keyword plan ad group
            cpc_bid_micros: Default CPC bid in micros

        Returns:
            Serialized response with updated keyword plan ad group details
        """
        operation = service.update_keyword_plan_ad_group_operation(
            resource_name=resource_name,
            name=name,
            cpc_bid_micros=cpc_bid_micros,
        )

        return await service.mutate_keyword_plan_ad_groups(
            ctx=ctx, customer_id=customer_id, operations=[operation]
        )

    tools.append(update_keyword_plan_ad_group)

    async def remove_keyword_plan_ad_group(
        ctx: Context,
        customer_id: str,
        resource_name: str,
    ) -> Dict[str, Any]:
        """Remove a keyword plan ad group.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            resource_name: The keyword plan ad group resource name

        Returns:
            Serialized response confirming removal
        """
        operation = service.remove_keyword_plan_ad_group_operation(
            resource_name=resource_name
        )

        return await service.mutate_keyword_plan_ad_groups(
            ctx=ctx, customer_id=customer_id, operations=[operation]
        )

    tools.append(remove_keyword_plan_ad_group)

    return tools


def register_keyword_plan_ad_group_tools(
    mcp: FastMCP[Any],
) -> KeywordPlanAdGroupService:
    """Register keyword plan ad group tools with the MCP server."""
    service = KeywordPlanAdGroupService()
    tools = create_keyword_plan_ad_group_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
