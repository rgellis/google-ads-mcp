"""User list customer type service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.resources.types.user_list_customer_type import (
    UserListCustomerType,
)
from google.ads.googleads.v23.services.services.user_list_customer_type_service import (
    UserListCustomerTypeServiceClient,
)
from google.ads.googleads.v23.services.types.user_list_customer_type_service import (
    MutateUserListCustomerTypesRequest,
    MutateUserListCustomerTypesResponse,
    UserListCustomerTypeOperation,
)

from src.sdk_client import get_sdk_client
from src.utils import (
    format_customer_id,
    get_logger,
    serialize_proto_message,
    set_request_options,
)

logger = get_logger(__name__)


class UserListCustomerTypeService:
    """Service for managing customer type classifications on user lists."""

    def __init__(self) -> None:
        self._client: Optional[UserListCustomerTypeServiceClient] = None

    @property
    def client(self) -> UserListCustomerTypeServiceClient:
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("UserListCustomerTypeService")
        assert self._client is not None
        return self._client

    async def add_customer_type(
        self,
        ctx: Context,
        customer_id: str,
        user_list_resource_name: str,
        customer_type_category: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Add a customer type classification to a user list.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            user_list_resource_name: Resource name of the user list
            customer_type_category: Category (PURCHASERS, HIGH_VALUE_CUSTOMERS,
                DISENGAGED_CUSTOMERS, QUALIFIED_LEADS, CONVERTED_LEADS, etc.)

        Returns:
            Created user list customer type details
        """
        try:
            customer_id = format_customer_id(customer_id)

            from google.ads.googleads.v23.enums.types.user_list_customer_type_category import (
                UserListCustomerTypeCategoryEnum,
            )

            user_list_customer_type = UserListCustomerType()
            user_list_customer_type.user_list = user_list_resource_name
            user_list_customer_type.customer_type_category = getattr(
                UserListCustomerTypeCategoryEnum.UserListCustomerTypeCategory,
                customer_type_category,
            )

            operation = UserListCustomerTypeOperation()
            operation.create = user_list_customer_type

            request = MutateUserListCustomerTypesRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateUserListCustomerTypesResponse = (
                self.client.mutate_user_list_customer_types(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Added {customer_type_category} type to user list",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to add customer type: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_customer_type(
        self,
        ctx: Context,
        customer_id: str,
        user_list_customer_type_resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Remove a customer type classification from a user list.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            user_list_customer_type_resource_name: Resource name of the classification

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)

            operation = UserListCustomerTypeOperation()
            operation.remove = user_list_customer_type_resource_name

            request = MutateUserListCustomerTypesRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateUserListCustomerTypesResponse = (
                self.client.mutate_user_list_customer_types(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Removed customer type: {user_list_customer_type_resource_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove customer type: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_user_list_customer_type_tools(
    service: UserListCustomerTypeService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the user list customer type service."""
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def add_customer_type_to_user_list(
        ctx: Context,
        customer_id: str,
        user_list_resource_name: str,
        customer_type_category: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add a customer type classification to a user list.

        Args:
            customer_id: The customer ID
            user_list_resource_name: Resource name of the user list
            customer_type_category: Category - PURCHASERS, HIGH_VALUE_CUSTOMERS,
                DISENGAGED_CUSTOMERS, QUALIFIED_LEADS, CONVERTED_LEADS,
                PAID_SUBSCRIBERS, LOYALTY_SIGN_UPS, CART_ABANDONERS

        Returns:
            Created classification details
        """
        return await service.add_customer_type(
            ctx=ctx,
            customer_id=customer_id,
            user_list_resource_name=user_list_resource_name,
            customer_type_category=customer_type_category,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def remove_customer_type_from_user_list(
        ctx: Context,
        customer_id: str,
        user_list_customer_type_resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Remove a customer type classification from a user list.

        Args:
            customer_id: The customer ID
            user_list_customer_type_resource_name: Resource name of the classification

        Returns:
            Removal result
        """
        return await service.remove_customer_type(
            ctx=ctx,
            customer_id=customer_id,
            user_list_customer_type_resource_name=user_list_customer_type_resource_name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    tools.extend([add_customer_type_to_user_list, remove_customer_type_from_user_list])
    return tools


def register_user_list_customer_type_tools(
    mcp: FastMCP[Any],
) -> UserListCustomerTypeService:
    """Register user list customer type tools with the MCP server."""
    service = UserListCustomerTypeService()
    tools = create_user_list_customer_type_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
