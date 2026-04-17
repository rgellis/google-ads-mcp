"""Incentive service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.services.services.incentive_service import (
    IncentiveServiceClient,
)
from google.ads.googleads.v23.services.types.incentive_service import (
    FetchIncentiveRequest,
    FetchIncentiveResponse,
    ApplyIncentiveRequest,
    ApplyIncentiveResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class IncentiveService:
    def __init__(self) -> None:
        self._client: Optional[IncentiveServiceClient] = None

    @property
    def client(self) -> IncentiveServiceClient:
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("IncentiveService")
        assert self._client is not None
        return self._client

    async def fetch_incentive(
        self,
        ctx: Context,
        language_code: str,
        country_code: str,
        email: str,
        incentive_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        try:
            request = FetchIncentiveRequest()
            request.language_code = language_code
            request.country_code = country_code
            request.email = email
            if incentive_type:
                from google.ads.googleads.v23.services.types.incentive_service import (
                    FetchIncentiveRequest as _FIR,
                )

                # IncentiveType enum is accessible from the request's type_ field
                r_tmp = _FIR()
                enum_cls = type(r_tmp.type_)
                request.type_ = enum_cls[incentive_type]
            response: FetchIncentiveResponse = self.client.fetch_incentive(
                request=request
            )
            await ctx.log(level="info", message="Fetched incentive offer")
            return serialize_proto_message(response)
        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to fetch incentive: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def apply_incentive(
        self,
        ctx: Context,
        customer_id: str,
        selected_incentive_id: int,
        country_code: str,
    ) -> Dict[str, Any]:
        try:
            customer_id = format_customer_id(customer_id)
            request = ApplyIncentiveRequest()
            request.selected_incentive_id = selected_incentive_id
            request.customer_id = customer_id
            request.country_code = country_code
            response: ApplyIncentiveResponse = self.client.apply_incentive(
                request=request
            )
            await ctx.log(
                level="info", message=f"Applied incentive {selected_incentive_id}"
            )
            return serialize_proto_message(response)
        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to apply incentive: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_incentive_tools(
    service: IncentiveService,
) -> List[Callable[..., Awaitable[Any]]]:
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def fetch_incentive(
        ctx: Context,
        language_code: str,
        country_code: str,
        email: str,
        incentive_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Fetch available Google Ads promotional incentive offers (e.g. ad credit coupons).

        Args:
            language_code: Language code (e.g. "en")
            country_code: Country code (e.g. "US")
            email: Email address associated with the account
            incentive_type: Optional filter by type - ACQUISITION or WINBACK

        Returns:
            Available incentive offers with IDs, amounts, and eligibility details
        """
        return await service.fetch_incentive(
            ctx=ctx,
            language_code=language_code,
            country_code=country_code,
            email=email,
            incentive_type=incentive_type,
        )

    async def apply_incentive(
        ctx: Context, customer_id: str, selected_incentive_id: int, country_code: str
    ) -> Dict[str, Any]:
        """Apply a selected incentive (ad credit) to a customer account.

        Args:
            customer_id: The customer ID
            selected_incentive_id: ID of the incentive to apply (from fetch_incentive results)
            country_code: Country code (e.g. "US")

        Returns:
            Application result confirming the incentive was applied
        """
        return await service.apply_incentive(
            ctx=ctx,
            customer_id=customer_id,
            selected_incentive_id=selected_incentive_id,
            country_code=country_code,
        )

    tools.extend([fetch_incentive, apply_incentive])
    return tools


def register_incentive_tools(mcp: FastMCP[Any]) -> IncentiveService:
    service = IncentiveService()
    tools = create_incentive_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
