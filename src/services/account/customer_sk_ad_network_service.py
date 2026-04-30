"""Customer SK Ad Network conversion value schema service using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.resources.types.customer_sk_ad_network_conversion_value_schema import (
    CustomerSkAdNetworkConversionValueSchema,
)
from google.ads.googleads.v23.services.services.customer_sk_ad_network_conversion_value_schema_service import (
    CustomerSkAdNetworkConversionValueSchemaServiceClient,
)
from google.ads.googleads.v23.services.types.customer_sk_ad_network_conversion_value_schema_service import (
    CustomerSkAdNetworkConversionValueSchemaOperation,
    MutateCustomerSkAdNetworkConversionValueSchemaRequest,
    MutateCustomerSkAdNetworkConversionValueSchemaResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import (
    format_customer_id,
    get_logger,
    serialize_proto_message,
)

logger = get_logger(__name__)


class CustomerSkAdNetworkService:
    def __init__(self) -> None:
        self._client: Optional[
            CustomerSkAdNetworkConversionValueSchemaServiceClient
        ] = None

    @property
    def client(self) -> CustomerSkAdNetworkConversionValueSchemaServiceClient:
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service(
                "CustomerSkAdNetworkConversionValueSchemaService"
            )
        assert self._client is not None
        return self._client

    async def mutate_schema(
        self,
        ctx: Context,
        customer_id: str,
        resource_name: str,
        schema: Dict[str, Any],
        validate_only: bool = False,
        enable_warnings: bool = False,
    ) -> Dict[str, Any]:
        """Update the SKAdNetwork conversion value schema.

        Per the v23 proto, the operation requires a valid ``resource_name``
        to target the existing schema; the wrapper now requires the
        caller to supply it.

        Note: MutateCustomerSkAdNetworkConversionValueSchemaRequest does
        not support partial_failure or response_content_type — those
        parameters were removed because passing them was a silent no-op.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            resource_name: Required. CustomerSkAdNetworkConversionValueSchema
                resource name (e.g.
                customers/{customer_id}/customerSkAdNetworkConversionValueSchemas/{account_link_id}).
            schema: Schema data to update
            validate_only: If true, the request is validated but not executed
            enable_warnings: Whether to return warnings about schema issues
        """
        try:
            customer_id = format_customer_id(customer_id)
            cvs = CustomerSkAdNetworkConversionValueSchema()
            cvs.resource_name = resource_name
            if "app_id" in schema:
                cvs.schema.app_id = schema["app_id"]
            if "measurement_window_hours" in schema:
                cvs.schema.measurement_window_hours = schema["measurement_window_hours"]
            operation = CustomerSkAdNetworkConversionValueSchemaOperation()
            operation.update = cvs
            request = MutateCustomerSkAdNetworkConversionValueSchemaRequest()
            request.customer_id = customer_id
            request.operation = operation
            if enable_warnings:
                request.enable_warnings = enable_warnings
            if validate_only:
                request.validate_only = validate_only
            response: MutateCustomerSkAdNetworkConversionValueSchemaResponse = (
                self.client.mutate_customer_sk_ad_network_conversion_value_schema(
                    request=request
                )
            )
            await ctx.log(
                level="info", message=f"Updated SKAdNetwork schema for {customer_id}"
            )
            return serialize_proto_message(response)
        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to mutate SKAdNetwork schema: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_customer_sk_ad_network_tools(
    service: CustomerSkAdNetworkService,
) -> List[Callable[..., Awaitable[Any]]]:
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def mutate_sk_ad_network_schema(
        ctx: Context,
        customer_id: str,
        resource_name: str,
        schema: Dict[str, Any],
        validate_only: bool = False,
        enable_warnings: bool = False,
    ) -> Dict[str, Any]:
        """Update the iOS SKAdNetwork conversion value schema for iOS app campaign measurement.

        SKAdNetwork is Apple's privacy-preserving attribution framework. This tool configures
        how conversion values map to your app events for iOS campaign reporting.

        Args:
            customer_id: The customer ID
            resource_name: Required. CustomerSkAdNetworkConversionValueSchema
                resource name targeting the existing schema to update.
            schema: Schema configuration dict with:
                - app_id: The iOS app ID
                - measurement_window_hours: Hours after install to measure conversions
            validate_only: If true, validate the request without executing it
            enable_warnings: Whether to return warnings about schema issues

        Returns:
            Updated schema details
        """
        return await service.mutate_schema(
            ctx=ctx,
            customer_id=customer_id,
            resource_name=resource_name,
            schema=schema,
            validate_only=validate_only,
            enable_warnings=enable_warnings,
        )

    tools.append(mutate_sk_ad_network_schema)
    return tools


def register_customer_sk_ad_network_tools(
    mcp: FastMCP[Any],
) -> CustomerSkAdNetworkService:
    service = CustomerSkAdNetworkService()
    tools = create_customer_sk_ad_network_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
