"""Ad Group Customizer Service for Google Ads API v23.

This service manages customizer values at the ad group level, allowing dynamic
content insertion in ads based on ad group-specific data.
"""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.services.services.ad_group_customizer_service import (
    AdGroupCustomizerServiceClient,
)
from google.ads.googleads.v23.services.types.ad_group_customizer_service import (
    AdGroupCustomizerOperation,
    MutateAdGroupCustomizersRequest,
)
from google.ads.googleads.v23.resources.types.ad_group_customizer import (
    AdGroupCustomizer,
)
from google.ads.googleads.v23.enums.types.customizer_attribute_type import (
    CustomizerAttributeTypeEnum,
)
from google.ads.googleads.v23.common.types.customizer_value import CustomizerValue

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class AdGroupCustomizerService:
    """Service for managing ad group customizers in Google Ads.

    Ad group customizers allow you to insert dynamic content into ads based on
    ad group-specific customizer values.
    """

    def __init__(self) -> None:
        """Initialize the ad group customizer service."""
        self._client: Optional[AdGroupCustomizerServiceClient] = None

    @property
    def client(self) -> AdGroupCustomizerServiceClient:
        """Get the ad group customizer service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("AdGroupCustomizerService")
        assert self._client is not None
        return self._client

    async def mutate_ad_group_customizers(
        self,
        ctx: Context,
        customer_id: str,
        operations: List[AdGroupCustomizerOperation],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create or remove ad group customizers.

        Args:
            ctx: FastMCP context.
            customer_id: The customer ID.
            operations: List of operations to perform.
            partial_failure: If true, successful operations will be carried out and invalid
                operations will return errors.
            validate_only: If true, the request is validated but not executed.
            response_content_type: The response content type setting.

        Returns:
            Serialized response dictionary.
        """
        try:
            customer_id = format_customer_id(customer_id)
            request = MutateAdGroupCustomizersRequest(
                customer_id=customer_id,
                operations=operations,
                partial_failure=partial_failure,
                validate_only=validate_only,
            )
            if response_content_type is not None:
                request.response_content_type = response_content_type
            response = self.client.mutate_ad_group_customizers(request=request)
            await ctx.log(
                level="info",
                message=f"Successfully mutated {len(operations)} ad group customizer(s) for customer {customer_id}",
            )
            return serialize_proto_message(response)
        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to mutate ad group customizers: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    def create_ad_group_customizer_operation(
        self,
        ad_group: str,
        customizer_attribute: str,
        value_type: CustomizerAttributeTypeEnum.CustomizerAttributeType,
        string_value: str,
    ) -> AdGroupCustomizerOperation:
        """Create an ad group customizer operation for creation.

        Args:
            ad_group: The ad group resource name.
            customizer_attribute: The customizer attribute resource name.
            value_type: The type of the customizer value.
            string_value: The string representation of the value.

        Returns:
            AdGroupCustomizerOperation: The operation to create the ad group customizer.
        """
        customizer_value = CustomizerValue(
            type_=value_type,
            string_value=string_value,
        )

        ad_group_customizer = AdGroupCustomizer(
            ad_group=ad_group,
            customizer_attribute=customizer_attribute,
            value=customizer_value,
        )

        return AdGroupCustomizerOperation(create=ad_group_customizer)

    def create_remove_operation(self, resource_name: str) -> AdGroupCustomizerOperation:
        """Create an ad group customizer operation for removal.

        Args:
            resource_name: The resource name of the ad group customizer to remove.
                Format: customers/{customer_id}/adGroupCustomizers/{ad_group_id}~{customizer_attribute_id}

        Returns:
            AdGroupCustomizerOperation: The operation to remove the ad group customizer.
        """
        return AdGroupCustomizerOperation(remove=resource_name)

    async def create_ad_group_customizer(
        self,
        ctx: Context,
        customer_id: str,
        ad_group: str,
        customizer_attribute: str,
        value_type: CustomizerAttributeTypeEnum.CustomizerAttributeType,
        string_value: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Create a single ad group customizer.

        Args:
            ctx: FastMCP context.
            customer_id: The customer ID.
            ad_group: The ad group resource name.
            customizer_attribute: The customizer attribute resource name.
            value_type: The type of the customizer value.
            string_value: The string representation of the value.
            validate_only: If true, the request is validated but not executed.

        Returns:
            Serialized response dictionary.
        """
        operation = self.create_ad_group_customizer_operation(
            ad_group=ad_group,
            customizer_attribute=customizer_attribute,
            value_type=value_type,
            string_value=string_value,
        )

        return await self.mutate_ad_group_customizers(
            ctx=ctx,
            customer_id=customer_id,
            operations=[operation],
            validate_only=validate_only,
        )

    async def remove_ad_group_customizer(
        self,
        ctx: Context,
        customer_id: str,
        resource_name: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Remove an ad group customizer.

        Args:
            ctx: FastMCP context.
            customer_id: The customer ID.
            resource_name: The resource name of the ad group customizer to remove.
            validate_only: If true, the request is validated but not executed.

        Returns:
            Serialized response dictionary.
        """
        operation = self.create_remove_operation(resource_name=resource_name)

        return await self.mutate_ad_group_customizers(
            ctx=ctx,
            customer_id=customer_id,
            operations=[operation],
            validate_only=validate_only,
        )

    async def create_text_customizer(
        self,
        ctx: Context,
        customer_id: str,
        ad_group: str,
        customizer_attribute: str,
        text_value: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Create a text ad group customizer.

        Args:
            ctx: FastMCP context.
            customer_id: The customer ID.
            ad_group: The ad group resource name.
            customizer_attribute: The customizer attribute resource name.
            text_value: The text value.
            validate_only: If true, the request is validated but not executed.

        Returns:
            Serialized response dictionary.
        """
        return await self.create_ad_group_customizer(
            ctx=ctx,
            customer_id=customer_id,
            ad_group=ad_group,
            customizer_attribute=customizer_attribute,
            value_type=CustomizerAttributeTypeEnum.CustomizerAttributeType.TEXT,
            string_value=text_value,
            validate_only=validate_only,
        )

    async def create_number_customizer(
        self,
        ctx: Context,
        customer_id: str,
        ad_group: str,
        customizer_attribute: str,
        number_value: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Create a number ad group customizer.

        Args:
            ctx: FastMCP context.
            customer_id: The customer ID.
            ad_group: The ad group resource name.
            customizer_attribute: The customizer attribute resource name.
            number_value: The number value as a string.
            validate_only: If true, the request is validated but not executed.

        Returns:
            Serialized response dictionary.
        """
        return await self.create_ad_group_customizer(
            ctx=ctx,
            customer_id=customer_id,
            ad_group=ad_group,
            customizer_attribute=customizer_attribute,
            value_type=CustomizerAttributeTypeEnum.CustomizerAttributeType.NUMBER,
            string_value=number_value,
            validate_only=validate_only,
        )

    async def create_price_customizer(
        self,
        ctx: Context,
        customer_id: str,
        ad_group: str,
        customizer_attribute: str,
        price_value: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Create a price ad group customizer.

        Args:
            ctx: FastMCP context.
            customer_id: The customer ID.
            ad_group: The ad group resource name.
            customizer_attribute: The customizer attribute resource name.
            price_value: The price value as a string (e.g., "19.99").
            validate_only: If true, the request is validated but not executed.

        Returns:
            Serialized response dictionary.
        """
        return await self.create_ad_group_customizer(
            ctx=ctx,
            customer_id=customer_id,
            ad_group=ad_group,
            customizer_attribute=customizer_attribute,
            value_type=CustomizerAttributeTypeEnum.CustomizerAttributeType.PRICE,
            string_value=price_value,
            validate_only=validate_only,
        )

    async def create_percent_customizer(
        self,
        ctx: Context,
        customer_id: str,
        ad_group: str,
        customizer_attribute: str,
        percent_value: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Create a percent ad group customizer.

        Args:
            ctx: FastMCP context.
            customer_id: The customer ID.
            ad_group: The ad group resource name.
            customizer_attribute: The customizer attribute resource name.
            percent_value: The percent value as a string (e.g., "25").
            validate_only: If true, the request is validated but not executed.

        Returns:
            Serialized response dictionary.
        """
        return await self.create_ad_group_customizer(
            ctx=ctx,
            customer_id=customer_id,
            ad_group=ad_group,
            customizer_attribute=customizer_attribute,
            value_type=CustomizerAttributeTypeEnum.CustomizerAttributeType.PERCENT,
            string_value=percent_value,
            validate_only=validate_only,
        )


def create_ad_group_customizer_tools(
    service: AdGroupCustomizerService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the ad group customizer service."""
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def mutate_ad_group_customizers(
        ctx: Context,
        customer_id: str,
        operations: list[dict[str, Any]],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create or remove ad group customizers.

        Args:
            customer_id: The customer ID
            operations: List of ad group customizer operations
            partial_failure: Enable partial failure
            validate_only: Only validate the request
            response_content_type: Response content type (RESOURCE_NAME_ONLY, MUTABLE_RESOURCE)

        Returns:
            Response with results and any partial failure errors
        """
        ops = []
        for op_data in operations:
            op_type = op_data["operation_type"]

            if op_type == "create":
                value_type = getattr(
                    CustomizerAttributeTypeEnum.CustomizerAttributeType,
                    op_data["value_type"],
                )

                operation = service.create_ad_group_customizer_operation(
                    ad_group=op_data["ad_group"],
                    customizer_attribute=op_data["customizer_attribute"],
                    value_type=value_type,
                    string_value=op_data["string_value"],
                )
            elif op_type == "remove":
                operation = service.create_remove_operation(
                    resource_name=op_data["resource_name"]
                )
            else:
                raise ValueError(f"Invalid operation type: {op_type}")

            ops.append(operation)

        rct = None
        if response_content_type is not None:
            from google.ads.googleads.v23.enums.types.response_content_type import (
                ResponseContentTypeEnum,
            )

            rct = getattr(
                ResponseContentTypeEnum.ResponseContentType, response_content_type
            )

        return await service.mutate_ad_group_customizers(
            ctx=ctx,
            customer_id=customer_id,
            operations=ops,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=rct,
        )

    async def create_ad_group_customizer(
        ctx: Context,
        customer_id: str,
        ad_group: str,
        customizer_attribute: str,
        value_type: str,
        string_value: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Create an ad group customizer.

        Args:
            customer_id: The customer ID
            ad_group: The ad group resource name
            customizer_attribute: The customizer attribute resource name
            value_type: Type of customizer value (TEXT, NUMBER, PRICE, PERCENT)
            string_value: String representation of the value
            validate_only: Only validate the request

        Returns:
            Created customizer details
        """
        value_type_enum = getattr(
            CustomizerAttributeTypeEnum.CustomizerAttributeType, value_type
        )

        return await service.create_ad_group_customizer(
            ctx=ctx,
            customer_id=customer_id,
            ad_group=ad_group,
            customizer_attribute=customizer_attribute,
            value_type=value_type_enum,
            string_value=string_value,
            validate_only=validate_only,
        )

    async def create_text_customizer(
        ctx: Context,
        customer_id: str,
        ad_group: str,
        customizer_attribute: str,
        text_value: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Create a text ad group customizer.

        Args:
            customer_id: The customer ID
            ad_group: The ad group resource name
            customizer_attribute: The customizer attribute resource name
            text_value: The text value
            validate_only: Only validate the request

        Returns:
            Created customizer details
        """
        return await service.create_text_customizer(
            ctx=ctx,
            customer_id=customer_id,
            ad_group=ad_group,
            customizer_attribute=customizer_attribute,
            text_value=text_value,
            validate_only=validate_only,
        )

    async def create_number_customizer(
        ctx: Context,
        customer_id: str,
        ad_group: str,
        customizer_attribute: str,
        number_value: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Create a number ad group customizer.

        Args:
            customer_id: The customer ID
            ad_group: The ad group resource name
            customizer_attribute: The customizer attribute resource name
            number_value: The number value as a string
            validate_only: Only validate the request

        Returns:
            Created customizer details
        """
        return await service.create_number_customizer(
            ctx=ctx,
            customer_id=customer_id,
            ad_group=ad_group,
            customizer_attribute=customizer_attribute,
            number_value=number_value,
            validate_only=validate_only,
        )

    async def create_price_customizer(
        ctx: Context,
        customer_id: str,
        ad_group: str,
        customizer_attribute: str,
        price_value: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Create a price ad group customizer.

        Args:
            customer_id: The customer ID
            ad_group: The ad group resource name
            customizer_attribute: The customizer attribute resource name
            price_value: The price value as a string (e.g., '19.99')
            validate_only: Only validate the request

        Returns:
            Created customizer details
        """
        return await service.create_price_customizer(
            ctx=ctx,
            customer_id=customer_id,
            ad_group=ad_group,
            customizer_attribute=customizer_attribute,
            price_value=price_value,
            validate_only=validate_only,
        )

    async def remove_ad_group_customizer(
        ctx: Context,
        customer_id: str,
        resource_name: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Remove an ad group customizer.

        Args:
            customer_id: The customer ID
            resource_name: The ad group customizer resource name to remove
            validate_only: Only validate the request

        Returns:
            Removal result details
        """
        return await service.remove_ad_group_customizer(
            ctx=ctx,
            customer_id=customer_id,
            resource_name=resource_name,
            validate_only=validate_only,
        )

    tools.extend(
        [
            mutate_ad_group_customizers,
            create_ad_group_customizer,
            create_text_customizer,
            create_number_customizer,
            create_price_customizer,
            remove_ad_group_customizer,
        ]
    )
    return tools


def register_ad_group_customizer_tools(mcp: FastMCP[Any]) -> AdGroupCustomizerService:
    """Register ad group customizer tools with the MCP server."""
    service = AdGroupCustomizerService()
    tools = create_ad_group_customizer_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
