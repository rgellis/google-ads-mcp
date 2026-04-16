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
    set_request_options,
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
        schema: Dict[str, Any],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Update the SKAdNetwork conversion value schema.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            schema: Schema data to update
        """
        try:
            customer_id = format_customer_id(customer_id)
            cvs = CustomerSkAdNetworkConversionValueSchema()
            if "app_id" in schema:
                cvs.schema.app_id = schema["app_id"]
            if "measurement_window_hours" in schema:
                cvs.schema.measurement_window_hours = schema["measurement_window_hours"]
            operation = CustomerSkAdNetworkConversionValueSchemaOperation()
            operation.update = cvs
            request = MutateCustomerSkAdNetworkConversionValueSchemaRequest()
            request.customer_id = customer_id
            request.operation = operation
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )
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
        schema: Dict[str, Any],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update the iOS SKAdNetwork conversion value schema.

        Args:
            customer_id: The customer ID
            schema: Schema data
        """
        return await service.mutate_schema(
            ctx=ctx,
            customer_id=customer_id,
            schema=schema,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
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
