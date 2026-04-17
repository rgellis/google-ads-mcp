"""Reservation service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.actions.types.book_campaigns import (
    BookCampaignsOperation,
)
from google.ads.googleads.v23.actions.types.quote_campaigns import (
    QuoteCampaignsOperation,
)
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

    async def quote_campaigns(
        self,
        ctx: Context,
        customer_id: str,
        operation: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        try:
            customer_id = format_customer_id(customer_id)
            request = QuoteCampaignsRequest()
            request.customer_id = customer_id
            if operation:
                op = QuoteCampaignsOperation()
                if "campaigns" in operation:
                    for c_data in operation["campaigns"]:
                        if isinstance(c_data, str):
                            op.campaigns.append(
                                QuoteCampaignsOperation.Campaign(campaign=c_data)
                            )
                        elif isinstance(c_data, dict):
                            op.campaigns.append(
                                QuoteCampaignsOperation.Campaign(**c_data)
                            )
                if "quote_signature" in operation:
                    op.quote_signature = operation["quote_signature"]
                request.operation = op
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

    async def book_campaigns(
        self,
        ctx: Context,
        customer_id: str,
        operation: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        try:
            customer_id = format_customer_id(customer_id)
            request = BookCampaignsRequest()
            request.customer_id = customer_id
            if operation:
                op = BookCampaignsOperation()
                if "campaigns" in operation:
                    for c_data in operation["campaigns"]:
                        if isinstance(c_data, str):
                            op.campaigns.append(
                                BookCampaignsOperation.Campaign(campaign=c_data)
                            )
                        elif isinstance(c_data, dict):
                            op.campaigns.append(
                                BookCampaignsOperation.Campaign(**c_data)
                            )
                if "quote_signature" in operation:
                    op.quote_signature = operation["quote_signature"]
                request.operation = op
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
        ctx: Context,
        customer_id: str,
        operation: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Get a price quote for reservation (guaranteed reach) campaigns before booking.

        Args:
            customer_id: The customer ID
            operation: Dict with:
                - campaigns: List of campaign resource names or dicts with campaign details
                - quote_signature: Optional signature from a previous quote (for re-quoting)

        Returns:
            Quote details including estimated costs and reach
        """
        return await service.quote_campaigns(
            ctx=ctx, customer_id=customer_id, operation=operation
        )

    async def book_reservation_campaigns(
        ctx: Context,
        customer_id: str,
        operation: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Book reservation (guaranteed reach) campaigns to lock in inventory and pricing.

        Args:
            customer_id: The customer ID
            operation: Dict with:
                - campaigns: List of campaign resource names or dicts with campaign details
                - quote_signature: Signature from a previous quote (recommended to lock quoted price)

        Returns:
            Booking confirmation with reserved campaign details
        """
        return await service.book_campaigns(
            ctx=ctx, customer_id=customer_id, operation=operation
        )

    tools.extend([quote_reservation_campaigns, book_reservation_campaigns])
    return tools


def register_reservation_tools(mcp: FastMCP[Any]) -> ReservationService:
    service = ReservationService()
    tools = create_reservation_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
