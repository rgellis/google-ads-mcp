"""Bidding strategy service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.common.types.bidding import (
    EnhancedCpc,
    MaximizeConversionValue,
    MaximizeConversions,
    TargetCpa,
    TargetImpressionShare,
    TargetRoas,
    TargetSpend,
)
from google.ads.googleads.v23.enums.types.bidding_strategy_status import (
    BiddingStrategyStatusEnum,
)
from google.ads.googleads.v23.enums.types.bidding_strategy_type import (
    BiddingStrategyTypeEnum,
)
from google.ads.googleads.v23.enums.types.target_impression_share_location import (
    TargetImpressionShareLocationEnum,
)
from google.ads.googleads.v23.resources.types.bidding_strategy import BiddingStrategy
from google.ads.googleads.v23.services.services.bidding_strategy_service import (
    BiddingStrategyServiceClient,
)
from google.ads.googleads.v23.services.types.bidding_strategy_service import (
    BiddingStrategyOperation,
    MutateBiddingStrategiesRequest,
    MutateBiddingStrategiesResponse,
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


class BiddingStrategyService:
    """Bidding strategy service for managing Google Ads automated bidding strategies."""

    def __init__(self) -> None:
        """Initialize the bidding strategy service."""
        self._client: Optional[BiddingStrategyServiceClient] = None

    @property
    def client(self) -> BiddingStrategyServiceClient:
        """Get the bidding strategy service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("BiddingStrategyService")
        assert self._client is not None
        return self._client

    async def create_target_cpa_strategy(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        target_cpa_micros: int,
        status: str = "ENABLED",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a Target CPA bidding strategy.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: Strategy name
            target_cpa_micros: Target cost per acquisition in micros
            status: Strategy status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created bidding strategy details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create bidding strategy
            bidding_strategy = BiddingStrategy()
            bidding_strategy.name = name
            bidding_strategy.status = getattr(
                BiddingStrategyStatusEnum.BiddingStrategyStatus, status
            )
            bidding_strategy.type_ = (
                BiddingStrategyTypeEnum.BiddingStrategyType.TARGET_CPA
            )

            # Configure Target CPA
            target_cpa = TargetCpa()
            target_cpa.target_cpa_micros = target_cpa_micros
            bidding_strategy.target_cpa = target_cpa

            # Create operation
            operation = BiddingStrategyOperation()
            operation.create = bidding_strategy

            # Create request
            request = MutateBiddingStrategiesRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateBiddingStrategiesResponse = (
                self.client.mutate_bidding_strategies(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created Target CPA strategy '{name}' with target {target_cpa_micros} micros",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create Target CPA strategy: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_target_roas_strategy(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        target_roas: float,
        status: str = "ENABLED",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a Target ROAS (Return on Ad Spend) bidding strategy.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: Strategy name
            target_roas: Target return on ad spend (e.g., 4.0 for 400% ROAS)
            status: Strategy status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created bidding strategy details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create bidding strategy
            bidding_strategy = BiddingStrategy()
            bidding_strategy.name = name
            bidding_strategy.status = getattr(
                BiddingStrategyStatusEnum.BiddingStrategyStatus, status
            )
            bidding_strategy.type_ = (
                BiddingStrategyTypeEnum.BiddingStrategyType.TARGET_ROAS
            )

            # Configure Target ROAS
            target_roas_strategy = TargetRoas()
            target_roas_strategy.target_roas = target_roas
            bidding_strategy.target_roas = target_roas_strategy

            # Create operation
            operation = BiddingStrategyOperation()
            operation.create = bidding_strategy

            # Create request
            request = MutateBiddingStrategiesRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateBiddingStrategiesResponse = (
                self.client.mutate_bidding_strategies(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created Target ROAS strategy '{name}' with target {target_roas}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create Target ROAS strategy: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_maximize_conversions_strategy(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        target_cpa_micros: Optional[int] = None,
        status: str = "ENABLED",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a Maximize Conversions bidding strategy.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: Strategy name
            target_cpa_micros: Optional target CPA constraint
            status: Strategy status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created bidding strategy details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create bidding strategy
            bidding_strategy = BiddingStrategy()
            bidding_strategy.name = name
            bidding_strategy.status = getattr(
                BiddingStrategyStatusEnum.BiddingStrategyStatus, status
            )
            bidding_strategy.type_ = (
                BiddingStrategyTypeEnum.BiddingStrategyType.MAXIMIZE_CONVERSIONS
            )

            # Configure Maximize Conversions
            maximize_conversions = MaximizeConversions()
            if target_cpa_micros is not None:
                maximize_conversions.target_cpa_micros = target_cpa_micros
            bidding_strategy.maximize_conversions = maximize_conversions

            # Create operation
            operation = BiddingStrategyOperation()
            operation.create = bidding_strategy

            # Create request
            request = MutateBiddingStrategiesRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateBiddingStrategiesResponse = (
                self.client.mutate_bidding_strategies(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created Maximize Conversions strategy '{name}'",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create Maximize Conversions strategy: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_enhanced_cpc_strategy(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        status: str = "ENABLED",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create an Enhanced CPC bidding strategy that adjusts manual bids to maximize conversions.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: Strategy name
            status: Strategy status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created bidding strategy details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create bidding strategy
            bidding_strategy = BiddingStrategy()
            bidding_strategy.name = name
            bidding_strategy.status = getattr(
                BiddingStrategyStatusEnum.BiddingStrategyStatus, status
            )
            bidding_strategy.type_ = (
                BiddingStrategyTypeEnum.BiddingStrategyType.ENHANCED_CPC
            )

            # Configure Enhanced CPC
            bidding_strategy.enhanced_cpc = EnhancedCpc()

            # Create operation
            operation = BiddingStrategyOperation()
            operation.create = bidding_strategy

            # Create request
            request = MutateBiddingStrategiesRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateBiddingStrategiesResponse = (
                self.client.mutate_bidding_strategies(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created Enhanced CPC strategy '{name}'",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create Enhanced CPC strategy: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_maximize_conversion_value_strategy(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        target_roas: Optional[float] = None,
        status: str = "ENABLED",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a Maximize Conversion Value strategy. Optionally set target_roas (e.g. 2.0 for 200% return).

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: Strategy name
            target_roas: Optional target return on ad spend
            status: Strategy status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created bidding strategy details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create bidding strategy
            bidding_strategy = BiddingStrategy()
            bidding_strategy.name = name
            bidding_strategy.status = getattr(
                BiddingStrategyStatusEnum.BiddingStrategyStatus, status
            )
            bidding_strategy.type_ = (
                BiddingStrategyTypeEnum.BiddingStrategyType.MAXIMIZE_CONVERSION_VALUE
            )

            # Configure Maximize Conversion Value
            mcv = MaximizeConversionValue()
            if target_roas is not None:
                mcv.target_roas = target_roas
            bidding_strategy.maximize_conversion_value = mcv

            # Create operation
            operation = BiddingStrategyOperation()
            operation.create = bidding_strategy

            # Create request
            request = MutateBiddingStrategiesRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateBiddingStrategiesResponse = (
                self.client.mutate_bidding_strategies(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created Maximize Conversion Value strategy '{name}'",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create Maximize Conversion Value strategy: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_target_spend_strategy(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        target_spend_micros: Optional[int] = None,
        status: str = "ENABLED",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a Target Spend (Maximize Clicks) strategy. Optionally set a spending target in micros.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: Strategy name
            target_spend_micros: Optional spending target in micros
            status: Strategy status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created bidding strategy details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create bidding strategy
            bidding_strategy = BiddingStrategy()
            bidding_strategy.name = name
            bidding_strategy.status = getattr(
                BiddingStrategyStatusEnum.BiddingStrategyStatus, status
            )
            bidding_strategy.type_ = (
                BiddingStrategyTypeEnum.BiddingStrategyType.TARGET_SPEND
            )

            # Configure Target Spend
            ts = TargetSpend()
            if target_spend_micros is not None:
                ts.target_spend_micros = target_spend_micros
            bidding_strategy.target_spend = ts

            # Create operation
            operation = BiddingStrategyOperation()
            operation.create = bidding_strategy

            # Create request
            request = MutateBiddingStrategiesRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateBiddingStrategiesResponse = (
                self.client.mutate_bidding_strategies(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created Target Spend strategy '{name}'",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create Target Spend strategy: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_target_impression_share_strategy(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        location: str,
        location_fraction_micros: int,
        max_cpc_bid_ceiling_micros: Optional[int] = None,
        status: str = "ENABLED",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a Target Impression Share bidding strategy.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: Strategy name
            location: Where to show ads (ABSOLUTE_TOP_OF_PAGE, TOP_OF_PAGE, ANYWHERE_ON_PAGE)
            location_fraction_micros: Target impression share (e.g., 650000 for 65%)
            max_cpc_bid_ceiling_micros: Optional max CPC bid limit
            status: Strategy status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created bidding strategy details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create bidding strategy
            bidding_strategy = BiddingStrategy()
            bidding_strategy.name = name
            bidding_strategy.status = getattr(
                BiddingStrategyStatusEnum.BiddingStrategyStatus, status
            )
            bidding_strategy.type_ = (
                BiddingStrategyTypeEnum.BiddingStrategyType.TARGET_IMPRESSION_SHARE
            )

            # Configure Target Impression Share
            target_impression_share = TargetImpressionShare()
            target_impression_share.location = getattr(
                TargetImpressionShareLocationEnum.TargetImpressionShareLocation,
                location,
            )
            target_impression_share.location_fraction_micros = location_fraction_micros

            if max_cpc_bid_ceiling_micros is not None:
                target_impression_share.cpc_bid_ceiling_micros = (
                    max_cpc_bid_ceiling_micros
                )

            bidding_strategy.target_impression_share = target_impression_share

            # Create operation
            operation = BiddingStrategyOperation()
            operation.create = bidding_strategy

            # Create request
            request = MutateBiddingStrategiesRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateBiddingStrategiesResponse = (
                self.client.mutate_bidding_strategies(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Created Target Impression Share strategy '{name}'",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create Target Impression Share strategy: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_bidding_strategy(
        self,
        ctx: Context,
        customer_id: str,
        bidding_strategy_id: str,
        name: Optional[str] = None,
        status: Optional[str] = None,
        target_cpa_micros: Optional[int] = None,
        target_roas: Optional[float] = None,
        maximize_conversions_target_cpa_micros: Optional[int] = None,
        target_impression_share_location: Optional[str] = None,
        target_impression_share_location_fraction_micros: Optional[int] = None,
        target_impression_share_cpc_bid_ceiling_micros: Optional[int] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Update an existing bidding strategy.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            bidding_strategy_id: The bidding strategy ID to update
            name: New strategy name
            status: New status (ENABLED, PAUSED, REMOVED)
            target_cpa_micros: New target CPA in micros (for TARGET_CPA strategies)
            target_roas: New target ROAS (for TARGET_ROAS strategies)
            maximize_conversions_target_cpa_micros: New target CPA constraint for MAXIMIZE_CONVERSIONS
            target_impression_share_location: New location for TARGET_IMPRESSION_SHARE
            target_impression_share_location_fraction_micros: New location fraction for TARGET_IMPRESSION_SHARE
            target_impression_share_cpc_bid_ceiling_micros: New CPC bid ceiling for TARGET_IMPRESSION_SHARE

        Returns:
            Updated bidding strategy details
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = (
                f"customers/{customer_id}/biddingStrategies/{bidding_strategy_id}"
            )

            bidding_strategy = BiddingStrategy()
            bidding_strategy.resource_name = resource_name

            update_mask_fields: List[str] = []

            if name is not None:
                bidding_strategy.name = name
                update_mask_fields.append("name")

            if status is not None:
                bidding_strategy.status = getattr(
                    BiddingStrategyStatusEnum.BiddingStrategyStatus, status
                )
                update_mask_fields.append("status")

            if target_cpa_micros is not None:
                target_cpa = TargetCpa()
                target_cpa.target_cpa_micros = target_cpa_micros
                bidding_strategy.target_cpa = target_cpa
                update_mask_fields.append("target_cpa.target_cpa_micros")

            if target_roas is not None:
                target_roas_strategy = TargetRoas()
                target_roas_strategy.target_roas = target_roas
                bidding_strategy.target_roas = target_roas_strategy
                update_mask_fields.append("target_roas.target_roas")

            if maximize_conversions_target_cpa_micros is not None:
                maximize_conversions = MaximizeConversions()
                maximize_conversions.target_cpa_micros = (
                    maximize_conversions_target_cpa_micros
                )
                bidding_strategy.maximize_conversions = maximize_conversions
                update_mask_fields.append("maximize_conversions.target_cpa_micros")

            if target_impression_share_location is not None:
                tis = TargetImpressionShare()
                tis.location = getattr(
                    TargetImpressionShareLocationEnum.TargetImpressionShareLocation,
                    target_impression_share_location,
                )
                bidding_strategy.target_impression_share = tis
                update_mask_fields.append("target_impression_share.location")

            if target_impression_share_location_fraction_micros is not None:
                if not bidding_strategy.target_impression_share.location_fraction_micros:
                    bidding_strategy.target_impression_share = (
                        bidding_strategy.target_impression_share
                        or TargetImpressionShare()
                    )
                bidding_strategy.target_impression_share.location_fraction_micros = (
                    target_impression_share_location_fraction_micros
                )
                update_mask_fields.append(
                    "target_impression_share.location_fraction_micros"
                )

            if target_impression_share_cpc_bid_ceiling_micros is not None:
                bidding_strategy.target_impression_share.cpc_bid_ceiling_micros = (
                    target_impression_share_cpc_bid_ceiling_micros
                )
                update_mask_fields.append(
                    "target_impression_share.cpc_bid_ceiling_micros"
                )

            if not update_mask_fields:
                raise ValueError("At least one field must be provided for update")

            # Create operation
            operation = BiddingStrategyOperation()
            operation.update = bidding_strategy
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_fields)
            )

            # Create request
            request = MutateBiddingStrategiesRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateBiddingStrategiesResponse = (
                self.client.mutate_bidding_strategies(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Updated bidding strategy {bidding_strategy_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update bidding strategy: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_bidding_strategy(
        self,
        ctx: Context,
        customer_id: str,
        bidding_strategy_id: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Remove a bidding strategy permanently.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            bidding_strategy_id: The bidding strategy ID to remove

        Returns:
            Removal result details
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = (
                f"customers/{customer_id}/biddingStrategies/{bidding_strategy_id}"
            )

            # Create operation
            operation = BiddingStrategyOperation()
            operation.remove = resource_name

            # Create request
            request = MutateBiddingStrategiesRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response = self.client.mutate_bidding_strategies(request=request)

            await ctx.log(
                level="info",
                message=f"Removed bidding strategy {bidding_strategy_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove bidding strategy: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_bidding_strategy_tools(
    service: BiddingStrategyService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the bidding strategy service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_target_cpa_strategy(
        ctx: Context,
        customer_id: str,
        name: str,
        target_cpa_micros: int,
        status: str = "ENABLED",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a Target CPA bidding strategy.

        Args:
            customer_id: The customer ID
            name: Strategy name
            target_cpa_micros: Target cost per acquisition in micros (1 million micros = 1 unit)
            status: Strategy status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created bidding strategy details
        """
        return await service.create_target_cpa_strategy(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            target_cpa_micros=target_cpa_micros,
            status=status,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_target_roas_strategy(
        ctx: Context,
        customer_id: str,
        name: str,
        target_roas: float,
        status: str = "ENABLED",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a Target ROAS (Return on Ad Spend) bidding strategy.

        Args:
            customer_id: The customer ID
            name: Strategy name
            target_roas: Target return on ad spend (e.g., 4.0 for 400% ROAS)
            status: Strategy status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created bidding strategy details
        """
        return await service.create_target_roas_strategy(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            target_roas=target_roas,
            status=status,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_maximize_conversions_strategy(
        ctx: Context,
        customer_id: str,
        name: str,
        target_cpa_micros: Optional[int] = None,
        status: str = "ENABLED",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a Maximize Conversions bidding strategy.

        Args:
            customer_id: The customer ID
            name: Strategy name
            target_cpa_micros: Optional target CPA constraint in micros
            status: Strategy status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created bidding strategy details
        """
        return await service.create_maximize_conversions_strategy(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            target_cpa_micros=target_cpa_micros,
            status=status,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_target_impression_share_strategy(
        ctx: Context,
        customer_id: str,
        name: str,
        location: str,
        location_fraction_micros: int,
        max_cpc_bid_ceiling_micros: Optional[int] = None,
        status: str = "ENABLED",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a Target Impression Share bidding strategy.

        Args:
            customer_id: The customer ID
            name: Strategy name
            location: Where to show ads - ABSOLUTE_TOP_OF_PAGE, TOP_OF_PAGE, ANYWHERE_ON_PAGE
            location_fraction_micros: Target impression share in micros (e.g., 650000 for 65%)
            max_cpc_bid_ceiling_micros: Optional max CPC bid limit in micros
            status: Strategy status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created bidding strategy details
        """
        return await service.create_target_impression_share_strategy(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            location=location,
            location_fraction_micros=location_fraction_micros,
            max_cpc_bid_ceiling_micros=max_cpc_bid_ceiling_micros,
            status=status,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_enhanced_cpc_strategy(
        ctx: Context,
        customer_id: str,
        name: str,
        status: str = "ENABLED",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create an Enhanced CPC bidding strategy that adjusts manual bids to maximize conversions.

        Args:
            customer_id: The customer ID
            name: Strategy name
            status: Strategy status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created bidding strategy details
        """
        return await service.create_enhanced_cpc_strategy(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            status=status,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_maximize_conversion_value_strategy(
        ctx: Context,
        customer_id: str,
        name: str,
        target_roas: Optional[float] = None,
        status: str = "ENABLED",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a Maximize Conversion Value strategy. Optionally set target_roas (e.g. 2.0 for 200% return).

        Args:
            customer_id: The customer ID
            name: Strategy name
            target_roas: Optional target return on ad spend (e.g., 2.0 for 200% return)
            status: Strategy status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created bidding strategy details
        """
        return await service.create_maximize_conversion_value_strategy(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            target_roas=target_roas,
            status=status,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_target_spend_strategy(
        ctx: Context,
        customer_id: str,
        name: str,
        target_spend_micros: Optional[int] = None,
        status: str = "ENABLED",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a Target Spend (Maximize Clicks) strategy. Optionally set a spending target in micros.

        Args:
            customer_id: The customer ID
            name: Strategy name
            target_spend_micros: Optional spending target in micros
            status: Strategy status (ENABLED, PAUSED, REMOVED)

        Returns:
            Created bidding strategy details
        """
        return await service.create_target_spend_strategy(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            target_spend_micros=target_spend_micros,
            status=status,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def remove_bidding_strategy(
        ctx: Context,
        customer_id: str,
        bidding_strategy_id: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Remove a bidding strategy permanently. This action is irreversible.

        Args:
            customer_id: The customer ID
            bidding_strategy_id: The bidding strategy ID to remove

        Returns:
            Removal result details
        """
        return await service.remove_bidding_strategy(
            ctx=ctx,
            customer_id=customer_id,
            bidding_strategy_id=bidding_strategy_id,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def update_bidding_strategy(
        ctx: Context,
        customer_id: str,
        bidding_strategy_id: str,
        name: Optional[str] = None,
        status: Optional[str] = None,
        target_cpa_micros: Optional[int] = None,
        target_roas: Optional[float] = None,
        maximize_conversions_target_cpa_micros: Optional[int] = None,
        target_impression_share_location: Optional[str] = None,
        target_impression_share_location_fraction_micros: Optional[int] = None,
        target_impression_share_cpc_bid_ceiling_micros: Optional[int] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing bidding strategy using partial update with field mask.

        Updatable fields:
            - name (str): Strategy name
            - status (str): Strategy status - ENABLED, PAUSED, REMOVED
            - target_cpa_micros (int): Target CPA in micros for TARGET_CPA strategies (1000000 = $1)
            - target_roas (float): Target ROAS for TARGET_ROAS strategies (e.g., 4.0 for 400%)
            - maximize_conversions_target_cpa_micros (int): Target CPA constraint for MAXIMIZE_CONVERSIONS
            - target_impression_share_location (str): Location for TARGET_IMPRESSION_SHARE -
                ABSOLUTE_TOP_OF_PAGE, TOP_OF_PAGE, ANYWHERE_ON_PAGE
            - target_impression_share_location_fraction_micros (int): Target impression share in micros
                (e.g., 650000 for 65%)
            - target_impression_share_cpc_bid_ceiling_micros (int): Max CPC bid ceiling in micros

        Args:
            customer_id: The customer ID
            bidding_strategy_id: The bidding strategy ID to update

        Returns:
            Updated bidding strategy details
        """
        return await service.update_bidding_strategy(
            ctx=ctx,
            customer_id=customer_id,
            bidding_strategy_id=bidding_strategy_id,
            name=name,
            status=status,
            target_cpa_micros=target_cpa_micros,
            target_roas=target_roas,
            maximize_conversions_target_cpa_micros=maximize_conversions_target_cpa_micros,
            target_impression_share_location=target_impression_share_location,
            target_impression_share_location_fraction_micros=target_impression_share_location_fraction_micros,
            target_impression_share_cpc_bid_ceiling_micros=target_impression_share_cpc_bid_ceiling_micros,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    tools.extend(
        [
            create_target_cpa_strategy,
            create_target_roas_strategy,
            create_maximize_conversions_strategy,
            create_enhanced_cpc_strategy,
            create_maximize_conversion_value_strategy,
            create_target_spend_strategy,
            create_target_impression_share_strategy,
            update_bidding_strategy,
            remove_bidding_strategy,
        ]
    )
    return tools


def register_bidding_strategy_tools(mcp: FastMCP[Any]) -> BiddingStrategyService:
    """Register bidding strategy tools with the MCP server.

    Returns the BiddingStrategyService instance for testing purposes.
    """
    service = BiddingStrategyService()
    tools = create_bidding_strategy_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
