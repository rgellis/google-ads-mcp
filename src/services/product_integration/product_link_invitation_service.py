"""Product link invitation service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.resources.types.product_link_invitation import (
    ProductLinkInvitation,
)
from google.ads.googleads.v23.services.services.product_link_invitation_service import (
    ProductLinkInvitationServiceClient,
)
from google.ads.googleads.v23.services.types.product_link_invitation_service import (
    CreateProductLinkInvitationRequest,
    CreateProductLinkInvitationResponse,
    RemoveProductLinkInvitationRequest,
    RemoveProductLinkInvitationResponse,
    UpdateProductLinkInvitationRequest,
    UpdateProductLinkInvitationResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class ProductLinkInvitationService:
    def __init__(self) -> None:
        self._client: Optional[ProductLinkInvitationServiceClient] = None

    @property
    def client(self) -> ProductLinkInvitationServiceClient:
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("ProductLinkInvitationService")
        assert self._client is not None
        return self._client

    async def create_invitation(self, ctx: Context, customer_id: str) -> Dict[str, Any]:
        try:
            customer_id = format_customer_id(customer_id)
            invitation = ProductLinkInvitation()
            request = CreateProductLinkInvitationRequest()
            request.customer_id = customer_id
            request.product_link_invitation = invitation
            response: CreateProductLinkInvitationResponse = (
                self.client.create_product_link_invitation(request=request)
            )
            await ctx.log(level="info", message="Created product link invitation")
            return serialize_proto_message(response)
        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create product link invitation: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_invitation(
        self, ctx: Context, customer_id: str, resource_name: str, status: str
    ) -> Dict[str, Any]:
        try:
            customer_id = format_customer_id(customer_id)
            from google.ads.googleads.v23.enums.types.product_link_invitation_status import (
                ProductLinkInvitationStatusEnum,
            )

            request = UpdateProductLinkInvitationRequest()
            request.customer_id = customer_id
            request.resource_name = resource_name
            request.product_link_invitation_status = getattr(
                ProductLinkInvitationStatusEnum.ProductLinkInvitationStatus, status
            )
            response: UpdateProductLinkInvitationResponse = (
                self.client.update_product_link_invitation(request=request)
            )
            await ctx.log(
                level="info",
                message=f"Updated product link invitation {resource_name} to {status}",
            )
            return serialize_proto_message(response)
        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update product link invitation: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_invitation(
        self, ctx: Context, customer_id: str, resource_name: str
    ) -> Dict[str, Any]:
        try:
            customer_id = format_customer_id(customer_id)
            request = RemoveProductLinkInvitationRequest()
            request.customer_id = customer_id
            request.resource_name = resource_name
            response: RemoveProductLinkInvitationResponse = (
                self.client.remove_product_link_invitation(request=request)
            )
            await ctx.log(
                level="info",
                message=f"Removed product link invitation: {resource_name}",
            )
            return serialize_proto_message(response)
        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove product link invitation: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_product_link_invitation_tools(
    service: ProductLinkInvitationService,
) -> List[Callable[..., Awaitable[Any]]]:
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def create_product_link_invitation(
        ctx: Context, customer_id: str
    ) -> Dict[str, Any]:
        """Create a product link invitation.

        Args:
            customer_id: The customer ID
        """
        return await service.create_invitation(ctx=ctx, customer_id=customer_id)

    async def update_product_link_invitation(
        ctx: Context, customer_id: str, resource_name: str, status: str
    ) -> Dict[str, Any]:
        """Update a product link invitation status.

        Args:
            customer_id: The customer ID
            resource_name: Invitation resource name
            status: New status (ACCEPTED, DECLINED, etc.)
        """
        return await service.update_invitation(
            ctx=ctx, customer_id=customer_id, resource_name=resource_name, status=status
        )

    async def remove_product_link_invitation(
        ctx: Context, customer_id: str, resource_name: str
    ) -> Dict[str, Any]:
        """Remove a product link invitation.

        Args:
            customer_id: The customer ID
            resource_name: Invitation resource name
        """
        return await service.remove_invitation(
            ctx=ctx, customer_id=customer_id, resource_name=resource_name
        )

    tools.extend(
        [
            create_product_link_invitation,
            update_product_link_invitation,
            remove_product_link_invitation,
        ]
    )
    return tools


def register_product_link_invitation_tools(
    mcp: FastMCP[Any],
) -> ProductLinkInvitationService:
    service = ProductLinkInvitationService()
    tools = create_product_link_invitation_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
