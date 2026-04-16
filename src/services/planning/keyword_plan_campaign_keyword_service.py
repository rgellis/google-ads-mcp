"""Google Ads Keyword Plan Campaign Keyword Service

This module provides functionality for managing keyword plan campaign keywords in Google Ads.
Note: Only negative keywords are supported for campaign-level keywords in keyword plans.
"""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.enums.types.keyword_match_type import KeywordMatchTypeEnum
from google.ads.googleads.v23.resources.types.keyword_plan_campaign_keyword import (
    KeywordPlanCampaignKeyword,
)
from google.ads.googleads.v23.services.services.keyword_plan_campaign_keyword_service import (
    KeywordPlanCampaignKeywordServiceClient,
)
from google.ads.googleads.v23.services.types.keyword_plan_campaign_keyword_service import (
    KeywordPlanCampaignKeywordOperation,
    MutateKeywordPlanCampaignKeywordsRequest,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class KeywordPlanCampaignKeywordService:
    """Service for managing Google Ads keyword plan campaign keywords (negative keywords only)."""

    def __init__(self) -> None:
        """Initialize the keyword plan campaign keyword service."""
        self._client: Optional[KeywordPlanCampaignKeywordServiceClient] = None

    @property
    def client(self) -> KeywordPlanCampaignKeywordServiceClient:
        """Get the keyword plan campaign keyword service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service(
                "KeywordPlanCampaignKeywordService"
            )
        assert self._client is not None
        return self._client

    async def mutate_keyword_plan_campaign_keywords(
        self,
        ctx: Context,
        customer_id: str,
        operations: List[KeywordPlanCampaignKeywordOperation],
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Mutate keyword plan campaign keywords.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            operations: List of keyword plan campaign keyword operations
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate the request

        Returns:
            Serialized response containing results
        """
        try:
            customer_id = format_customer_id(customer_id)
            request = MutateKeywordPlanCampaignKeywordsRequest(
                customer_id=customer_id,
                operations=operations,
                partial_failure=partial_failure,
                validate_only=validate_only,
            )
            response = self.client.mutate_keyword_plan_campaign_keywords(
                request=request
            )
            await ctx.log(
                level="info",
                message=f"Successfully mutated {len(response.results)} keyword plan campaign keywords",
            )
            return serialize_proto_message(response)
        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to mutate keyword plan campaign keywords: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    def create_keyword_plan_campaign_keyword_operation(
        self,
        keyword_plan_campaign: str,
        text: str,
        match_type: KeywordMatchTypeEnum.KeywordMatchType,
    ) -> KeywordPlanCampaignKeywordOperation:
        """Create a keyword plan campaign keyword operation for creation.

        Note: Only negative keywords are supported at the campaign level.

        Args:
            keyword_plan_campaign: The keyword plan campaign resource name
            text: The keyword text
            match_type: The keyword match type

        Returns:
            KeywordPlanCampaignKeywordOperation: The operation to create the keyword plan campaign keyword
        """
        keyword_plan_campaign_keyword = KeywordPlanCampaignKeyword(
            keyword_plan_campaign=keyword_plan_campaign,
            text=text,
            match_type=match_type,
            negative=True,  # Only negative keywords are supported
        )

        return KeywordPlanCampaignKeywordOperation(create=keyword_plan_campaign_keyword)

    def update_keyword_plan_campaign_keyword_operation(
        self,
        resource_name: str,
        text: Optional[str] = None,
        match_type: Optional[KeywordMatchTypeEnum.KeywordMatchType] = None,
    ) -> KeywordPlanCampaignKeywordOperation:
        """Create a keyword plan campaign keyword operation for update.

        Args:
            resource_name: The keyword plan campaign keyword resource name
            text: The keyword text
            match_type: The keyword match type

        Returns:
            KeywordPlanCampaignKeywordOperation: The operation to update the keyword plan campaign keyword
        """
        keyword_plan_campaign_keyword = KeywordPlanCampaignKeyword(
            resource_name=resource_name
        )

        update_mask = []
        if text is not None:
            keyword_plan_campaign_keyword.text = text
            update_mask.append("text")
        if match_type is not None:
            keyword_plan_campaign_keyword.match_type = match_type
            update_mask.append("match_type")

        return KeywordPlanCampaignKeywordOperation(
            update=keyword_plan_campaign_keyword,
            update_mask={"paths": update_mask},
        )

    def remove_keyword_plan_campaign_keyword_operation(
        self, resource_name: str
    ) -> KeywordPlanCampaignKeywordOperation:
        """Create a keyword plan campaign keyword operation for removal.

        Args:
            resource_name: The keyword plan campaign keyword resource name

        Returns:
            KeywordPlanCampaignKeywordOperation: The operation to remove the keyword plan campaign keyword
        """
        return KeywordPlanCampaignKeywordOperation(remove=resource_name)


def create_keyword_plan_campaign_keyword_tools(
    service: KeywordPlanCampaignKeywordService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create keyword plan campaign keyword tools for MCP."""
    tools: List[Callable[..., Awaitable[Any]]] = []

    def _get_match_type_enum(
        match_type_str: str,
    ) -> KeywordMatchTypeEnum.KeywordMatchType:
        """Convert string to match type enum."""
        if match_type_str == "EXACT":
            return KeywordMatchTypeEnum.KeywordMatchType.EXACT
        elif match_type_str == "PHRASE":
            return KeywordMatchTypeEnum.KeywordMatchType.PHRASE
        elif match_type_str == "BROAD":
            return KeywordMatchTypeEnum.KeywordMatchType.BROAD
        else:
            raise ValueError(f"Invalid match type: {match_type_str}")

    async def mutate_keyword_plan_campaign_keywords(
        ctx: Context,
        customer_id: str,
        operations: list[dict[str, Any]],
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Create, update, or remove keyword plan campaign keywords (negative keywords only).

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            operations: List of keyword plan campaign keyword operations
            partial_failure: Enable partial failure
            validate_only: Only validate the request

        Returns:
            Serialized response with operation results
        """
        ops = []
        for op_data in operations:
            op_type = op_data["operation_type"]

            if op_type == "create":
                operation = service.create_keyword_plan_campaign_keyword_operation(
                    keyword_plan_campaign=op_data["keyword_plan_campaign"],
                    text=op_data["text"],
                    match_type=_get_match_type_enum(op_data["match_type"]),
                )
            elif op_type == "update":
                match_type = None
                if "match_type" in op_data:
                    match_type = _get_match_type_enum(op_data["match_type"])

                operation = service.update_keyword_plan_campaign_keyword_operation(
                    resource_name=op_data["resource_name"],
                    text=op_data.get("text"),
                    match_type=match_type,
                )
            elif op_type == "remove":
                operation = service.remove_keyword_plan_campaign_keyword_operation(
                    resource_name=op_data["resource_name"]
                )
            else:
                raise ValueError(f"Invalid operation type: {op_type}")

            ops.append(operation)

        return await service.mutate_keyword_plan_campaign_keywords(
            ctx=ctx,
            customer_id=customer_id,
            operations=ops,
            partial_failure=partial_failure,
            validate_only=validate_only,
        )

    tools.append(mutate_keyword_plan_campaign_keywords)

    async def create_keyword_plan_campaign_keyword(
        ctx: Context,
        customer_id: str,
        keyword_plan_campaign: str,
        text: str,
        match_type: str,
    ) -> Dict[str, Any]:
        """Create a new keyword plan campaign keyword (negative keyword).

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            keyword_plan_campaign: The keyword plan campaign resource name
            text: The keyword text
            match_type: The keyword match type (EXACT, PHRASE, or BROAD)

        Returns:
            Serialized response with created keyword plan campaign keyword details
        """
        operation = service.create_keyword_plan_campaign_keyword_operation(
            keyword_plan_campaign=keyword_plan_campaign,
            text=text,
            match_type=_get_match_type_enum(match_type),
        )

        return await service.mutate_keyword_plan_campaign_keywords(
            ctx=ctx, customer_id=customer_id, operations=[operation]
        )

    tools.append(create_keyword_plan_campaign_keyword)

    async def update_keyword_plan_campaign_keyword(
        ctx: Context,
        customer_id: str,
        resource_name: str,
        text: Optional[str] = None,
        match_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing keyword plan campaign keyword.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            resource_name: The keyword plan campaign keyword resource name
            text: The keyword text
            match_type: The keyword match type (EXACT, PHRASE, or BROAD)

        Returns:
            Serialized response with updated keyword plan campaign keyword details
        """
        match_type_enum = None
        if match_type is not None:
            match_type_enum = _get_match_type_enum(match_type)

        operation = service.update_keyword_plan_campaign_keyword_operation(
            resource_name=resource_name,
            text=text,
            match_type=match_type_enum,
        )

        return await service.mutate_keyword_plan_campaign_keywords(
            ctx=ctx, customer_id=customer_id, operations=[operation]
        )

    tools.append(update_keyword_plan_campaign_keyword)

    async def remove_keyword_plan_campaign_keyword(
        ctx: Context,
        customer_id: str,
        resource_name: str,
    ) -> Dict[str, Any]:
        """Remove a keyword plan campaign keyword.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            resource_name: The keyword plan campaign keyword resource name

        Returns:
            Serialized response confirming removal
        """
        operation = service.remove_keyword_plan_campaign_keyword_operation(
            resource_name=resource_name
        )

        return await service.mutate_keyword_plan_campaign_keywords(
            ctx=ctx, customer_id=customer_id, operations=[operation]
        )

    tools.append(remove_keyword_plan_campaign_keyword)

    return tools


def register_keyword_plan_campaign_keyword_tools(
    mcp: FastMCP[Any],
) -> KeywordPlanCampaignKeywordService:
    """Register keyword plan campaign keyword tools with the MCP server."""
    service = KeywordPlanCampaignKeywordService()
    tools = create_keyword_plan_campaign_keyword_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
