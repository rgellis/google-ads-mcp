"""Google Ads Product Link Service

This module provides functionality for managing product links in Google Ads.
Product links connect Google Ads accounts with other Google products like Merchant Center.
"""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.resources.types.product_link import (
    ProductLink,
    DataPartnerIdentifier,
    GoogleAdsIdentifier,
    MerchantCenterIdentifier,
)
from google.ads.googleads.v23.services.services.product_link_service import (
    ProductLinkServiceClient,
)
from google.ads.googleads.v23.services.types.product_link_service import (
    CreateProductLinkRequest,
    RemoveProductLinkRequest,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class ProductLinkService:
    """Service for managing Google Ads product links."""

    def __init__(self) -> None:
        """Initialize the product link service."""
        self._client: Optional[ProductLinkServiceClient] = None

    @property
    def client(self) -> ProductLinkServiceClient:
        """Get the product link service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("ProductLinkService")
        assert self._client is not None
        return self._client

    async def create_product_link(
        self,
        ctx: Context,
        customer_id: str,
        product_link: ProductLink,
    ) -> Dict[str, Any]:
        """Create a product link.

        Args:
            ctx: FastMCP context.
            customer_id: The customer ID.
            product_link: The product link to create.

        Returns:
            Serialized response dictionary.
        """
        try:
            customer_id = format_customer_id(customer_id)
            request = CreateProductLinkRequest(
                customer_id=customer_id,
                product_link=product_link,
            )
            response = self.client.create_product_link(request=request)
            await ctx.log(
                level="info",
                message=f"Created product link for customer {customer_id}: {response.resource_name}",
            )
            return serialize_proto_message(response)
        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create product link: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_product_link(
        self,
        ctx: Context,
        customer_id: str,
        resource_name: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Remove a product link.

        Args:
            ctx: FastMCP context.
            customer_id: The customer ID.
            resource_name: The product link resource name to remove.
            validate_only: Whether to only validate the request.

        Returns:
            Serialized response dictionary.
        """
        try:
            customer_id = format_customer_id(customer_id)
            request = RemoveProductLinkRequest(
                customer_id=customer_id,
                resource_name=resource_name,
            )
            if validate_only:
                request.validate_only = validate_only
            response = self.client.remove_product_link(request=request)
            await ctx.log(
                level="info",
                message=f"Removed product link for customer {customer_id}: {resource_name}",
            )
            return serialize_proto_message(response)
        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove product link: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_merchant_center_link(
        self,
        ctx: Context,
        customer_id: str,
        merchant_center_id: int,
    ) -> Dict[str, Any]:
        """Create a Merchant Center product link.

        Args:
            ctx: FastMCP context.
            customer_id: The customer ID.
            merchant_center_id: The Merchant Center account ID.

        Returns:
            Serialized response dictionary.
        """
        merchant_center_identifier = MerchantCenterIdentifier(
            merchant_center_id=merchant_center_id
        )

        product_link = ProductLink(merchant_center=merchant_center_identifier)

        return await self.create_product_link(
            ctx=ctx, customer_id=customer_id, product_link=product_link
        )

    async def create_google_ads_link(
        self,
        ctx: Context,
        customer_id: str,
        linked_customer_id: int,
    ) -> Dict[str, Any]:
        """Create a Google Ads product link.

        Args:
            ctx: FastMCP context.
            customer_id: The customer ID.
            linked_customer_id: The linked Google Ads customer ID.

        Returns:
            Serialized response dictionary.
        """
        google_ads_identifier = GoogleAdsIdentifier(
            customer=f"customers/{linked_customer_id}"
        )

        product_link = ProductLink(google_ads=google_ads_identifier)

        return await self.create_product_link(
            ctx=ctx, customer_id=customer_id, product_link=product_link
        )

    async def create_data_partner_link(
        self,
        ctx: Context,
        customer_id: str,
        data_partner_id: int,
    ) -> Dict[str, Any]:
        """Create a Data Partner product link.

        Args:
            ctx: FastMCP context.
            customer_id: The customer ID.
            data_partner_id: The data partner ID.

        Returns:
            Serialized response dictionary.
        """
        data_partner_identifier = DataPartnerIdentifier(data_partner_id=data_partner_id)

        product_link = ProductLink(data_partner=data_partner_identifier)

        return await self.create_product_link(
            ctx=ctx, customer_id=customer_id, product_link=product_link
        )


def create_product_link_tools(
    service: ProductLinkService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the product link service."""
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def create_merchant_center_link(
        ctx: Context,
        customer_id: str,
        merchant_center_id: int,
    ) -> Dict[str, Any]:
        """Create a Merchant Center product link.

        Args:
            customer_id: The customer ID
            merchant_center_id: The Merchant Center account ID

        Returns:
            Created product link details
        """
        return await service.create_merchant_center_link(
            ctx=ctx,
            customer_id=customer_id,
            merchant_center_id=merchant_center_id,
        )

    async def create_google_ads_link(
        ctx: Context,
        customer_id: str,
        linked_customer_id: int,
    ) -> Dict[str, Any]:
        """Create a Google Ads product link.

        Args:
            customer_id: The customer ID
            linked_customer_id: The linked Google Ads customer ID

        Returns:
            Created product link details
        """
        return await service.create_google_ads_link(
            ctx=ctx,
            customer_id=customer_id,
            linked_customer_id=linked_customer_id,
        )

    async def create_data_partner_link(
        ctx: Context,
        customer_id: str,
        data_partner_id: int,
    ) -> Dict[str, Any]:
        """Create a Data Partner product link.

        Args:
            customer_id: The customer ID
            data_partner_id: The data partner ID

        Returns:
            Created product link details
        """
        return await service.create_data_partner_link(
            ctx=ctx,
            customer_id=customer_id,
            data_partner_id=data_partner_id,
        )

    async def remove_product_link(
        ctx: Context,
        customer_id: str,
        resource_name: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Remove a product link.

        Args:
            customer_id: The customer ID
            resource_name: The product link resource name to remove
            validate_only: Whether to only validate the request

        Returns:
            Removal result details
        """
        return await service.remove_product_link(
            ctx=ctx,
            customer_id=customer_id,
            resource_name=resource_name,
            validate_only=validate_only,
        )

    tools.extend(
        [
            create_merchant_center_link,
            create_google_ads_link,
            create_data_partner_link,
            remove_product_link,
        ]
    )
    return tools


def register_product_link_tools(mcp: FastMCP[Any]) -> ProductLinkService:
    """Register product link tools with the MCP server."""
    service = ProductLinkService()
    tools = create_product_link_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
