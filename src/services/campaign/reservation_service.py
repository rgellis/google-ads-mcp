"""Reservation service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.services.services.reservation_service import (
    ReservationServiceClient,
)
from google.ads.googleads.v23.services.types.reservation_service import (
    QuoteCampaignsRequest,
    QuoteCampaignsResponse,
    BookCampaignsRequest,
    BookCampaignsResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class ReservationService:
    def __init__(self) -> None:
        self._client: Optional[ReservationServiceClient] = None

    @property
    def client(self) -> ReservationServiceClient:
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("ReservationService")
        assert self._client is not None
        return self._client

    async def quote_campaigns(self, ctx: Context, customer_id: str) -> Dict[str, Any]:
        try:
            customer_id = format_customer_id(customer_id)
            request = QuoteCampaignsRequest()
            request.customer_id = customer_id
            response: QuoteCampaignsResponse = self.client.quote_campaigns(
                request=request
            )
            await ctx.log(level="info", message="Generated reservation quote")
            return serialize_proto_message(response)
        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to quote campaigns: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def book_campaigns(self, ctx: Context, customer_id: str) -> Dict[str, Any]:
        try:
            customer_id = format_customer_id(customer_id)
            request = BookCampaignsRequest()
            request.customer_id = customer_id
            response: BookCampaignsResponse = self.client.book_campaigns(
                request=request
            )
            await ctx.log(level="info", message="Booked reservation campaigns")
            return serialize_proto_message(response)
        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to book campaigns: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_reservation_tools(
    service: ReservationService,
) -> List[Callable[..., Awaitable[Any]]]:
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def quote_reservation_campaigns(
        ctx: Context, customer_id: str
    ) -> Dict[str, Any]:
        """Get a quote for reservation (guaranteed) campaigns.

        Args:
            customer_id: The customer ID
        """
        return await service.quote_campaigns(ctx=ctx, customer_id=customer_id)

    async def book_reservation_campaigns(
        ctx: Context, customer_id: str
    ) -> Dict[str, Any]:
        """Book reservation (guaranteed) campaigns.

        Args:
            customer_id: The customer ID
        """
        return await service.book_campaigns(ctx=ctx, customer_id=customer_id)

    tools.extend([quote_reservation_campaigns, book_reservation_campaigns])
    return tools


def register_reservation_tools(mcp: FastMCP[Any]) -> ReservationService:
    service = ReservationService()
    tools = create_reservation_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
