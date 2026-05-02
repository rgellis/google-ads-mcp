"""User list service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.common.types.user_lists import (
    BasicUserListInfo,
    CrmBasedUserListInfo,
    LogicalUserListInfo,
    LogicalUserListOperandInfo,
    LookalikeUserListInfo,
    RuleBasedUserListInfo,
    UserListActionInfo,
    UserListLogicalRuleInfo,
)
from google.ads.googleads.v23.enums.types.user_list_logical_rule_operator import (
    UserListLogicalRuleOperatorEnum,
)
from google.ads.googleads.v23.enums.types.user_list_membership_status import (
    UserListMembershipStatusEnum,
)
from google.ads.googleads.v23.resources.types.user_list import UserList
from google.ads.googleads.v23.services.services.user_list_service import (
    UserListServiceClient,
)
from google.ads.googleads.v23.services.types.user_list_service import (
    MutateUserListsRequest,
    MutateUserListsResponse,
    UserListOperation,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import (
    format_customer_id,
    get_logger,
    serialize_proto_message,
    set_optional_submessage,
    set_request_options,
)

logger = get_logger(__name__)


class UserListService:
    """User list service for managing Google Ads remarketing lists."""

    def __init__(self) -> None:
        """Initialize the user list service."""
        self._client: Optional[UserListServiceClient] = None

    @property
    def client(self) -> UserListServiceClient:
        """Get the user list service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("UserListService")
        assert self._client is not None
        return self._client

    async def create_basic_user_list(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        actions: List[Dict[str, str]],
        description: Optional[str] = None,
        membership_life_span: Optional[int] = None,
        membership_status: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a basic remarketing user list.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: User list name
            actions: List of action dicts that build BasicUserListInfo.actions.
                Each dict must have exactly ONE of:
                  - "conversion_action": resource name of a ConversionAction
                  - "remarketing_action": resource name of a RemarketingAction
                A BasicUserList without actions is unusable, so this is required.
            description: Optional description
            membership_life_span: How long users remain in the list (days,
                0-540). Omit to use the API default.
            membership_status: OPEN or CLOSED. Omit to use the API default
                (OPEN). Proto-default rule: setting OPEN explicitly still
                marks the field on the wire.

        Returns:
            Created user list details
        """
        if not actions:
            raise ValueError(
                "create_basic_user_list requires at least one action; a "
                "BasicUserList with no actions is unusable."
            )

        try:
            customer_id = format_customer_id(customer_id)

            # Create user list
            user_list = UserList()
            user_list.name = name
            if description:
                user_list.description = description

            if membership_status is not None:
                user_list.membership_status = getattr(
                    UserListMembershipStatusEnum.UserListMembershipStatus,
                    membership_status,
                )
            if membership_life_span is not None:
                user_list.membership_life_span = membership_life_span

            # Create basic user list info with the caller-supplied actions.
            basic_user_list = BasicUserListInfo()
            for idx, action in enumerate(actions):
                action_info = UserListActionInfo()
                if "conversion_action" in action and "remarketing_action" in action:
                    raise ValueError(
                        f"actions[{idx}]: pass exactly one of conversion_action "
                        "or remarketing_action (they are members of the same oneof)."
                    )
                if "conversion_action" in action:
                    action_info.conversion_action = action["conversion_action"]
                elif "remarketing_action" in action:
                    action_info.remarketing_action = action["remarketing_action"]
                else:
                    raise ValueError(
                        f"actions[{idx}]: must contain conversion_action or "
                        "remarketing_action key."
                    )
                basic_user_list.actions.append(action_info)
            user_list.basic_user_list = basic_user_list

            # Create operation
            operation = UserListOperation()
            operation.create = user_list

            # Create request
            request = MutateUserListsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateUserListsResponse = self.client.mutate_user_lists(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created basic user list '{name}'",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create basic user list: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_crm_based_user_list(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        description: Optional[str] = None,
        membership_life_span: Optional[int] = None,
        upload_key_type: Optional[str] = None,
        data_source_type: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a CRM-based user list for customer match.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: User list name
            description: Optional description
            membership_life_span: How long users remain in the list (days,
                0-540). Omit to use the API default.
            upload_key_type: Optional CONTACT_INFO, CRM_ID, or
                MOBILE_ADVERTISING_ID. Omit to let the API default apply.
            data_source_type: Optional source. One of FIRST_PARTY,
                THIRD_PARTY_CREDIT_BUREAU, THIRD_PARTY_VOTER_FILE,
                THIRD_PARTY_PARTNER_DATA. Omit to let the API default apply.

        Returns:
            Created user list details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create user list. membership_status was hardcoded to OPEN —
            # OPEN is the proto default, so explicitly setting it just marks
            # the field on the wire (CLAUDE.md proto-default rule). Drop it.
            user_list = UserList()
            user_list.name = name
            if description:
                user_list.description = description

            if membership_life_span is not None:
                user_list.membership_life_span = membership_life_span

            # Create CRM-based user list info
            crm_user_list = CrmBasedUserListInfo()
            # Set upload key type only when supplied; otherwise let the
            # API default apply.
            if upload_key_type is not None:
                from google.ads.googleads.v23.enums.types.customer_match_upload_key_type import (
                    CustomerMatchUploadKeyTypeEnum,
                )

                crm_user_list.upload_key_type = getattr(
                    CustomerMatchUploadKeyTypeEnum.CustomerMatchUploadKeyType,
                    upload_key_type,
                )

            if data_source_type is not None:
                from google.ads.googleads.v23.enums.types.user_list_crm_data_source_type import (
                    UserListCrmDataSourceTypeEnum,
                )

                crm_user_list.data_source_type = getattr(
                    UserListCrmDataSourceTypeEnum.UserListCrmDataSourceType,
                    data_source_type,
                )

            user_list.crm_based_user_list = crm_user_list

            # Create operation
            operation = UserListOperation()
            operation.create = user_list

            # Create request
            request = MutateUserListsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateUserListsResponse = self.client.mutate_user_lists(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created CRM-based user list '{name}' for customer match",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create CRM-based user list: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_logical_user_list(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        rules: List[Dict[str, Any]],
        description: Optional[str] = None,
        membership_life_span: Optional[int] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a logical (combined) user list.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: User list name
            rules: List of rule dictionaries. Each dict has:
                - user_list_ids: list of user list IDs
                - operator: ALL, ANY, or NONE (per-rule; the proto has no
                  top-level operator)
            description: Optional description
            membership_life_span: How long users remain in the list (days,
                0-540). Omit to use the API default.

        Returns:
            Created user list details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create user list. membership_status hardcoded to OPEN was
            # redundant — OPEN is the proto default; setting it explicitly
            # marks the field on the wire (CLAUDE.md proto-default rule).
            user_list = UserList()
            user_list.name = name
            if description:
                user_list.description = description

            if membership_life_span is not None:
                user_list.membership_life_span = membership_life_span

            # Create logical user list info
            logical_user_list = LogicalUserListInfo()

            # Create user list logical rule info
            for rule in rules:
                user_list_logical_rule_info = UserListLogicalRuleInfo()
                user_list_logical_rule_info.operator = getattr(
                    UserListLogicalRuleOperatorEnum.UserListLogicalRuleOperator,
                    rule.get("operator", "ALL"),
                )

                # Add user lists to the rule
                for user_list_id in rule.get("user_list_ids", []):
                    user_list_resource = (
                        f"customers/{customer_id}/userLists/{user_list_id}"
                    )
                    operand = LogicalUserListOperandInfo()
                    operand.user_list = user_list_resource
                    user_list_logical_rule_info.rule_operands.append(operand)

                logical_user_list.rules.append(user_list_logical_rule_info)

            user_list.logical_user_list = logical_user_list

            # Create operation
            operation = UserListOperation()
            operation.create = user_list

            # Create request
            request = MutateUserListsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateUserListsResponse = self.client.mutate_user_lists(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created logical user list '{name}' with {len(rules)} rules",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create logical user list: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_lookalike_user_list(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        lookalike_user_list: Dict[str, Any],
        description: Optional[str] = None,
        membership_life_span: Optional[int] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a lookalike user list (Immutable on the resource).

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: User list name
            lookalike_user_list: Dict that builds a ``LookalikeUserListInfo``
                submessage. See the v23 reference for fields:
                ``seed_user_list_ids`` (list of seed list IDs),
                ``expansion_level`` (NARROW / BALANCED / BROAD),
                ``country_codes``.
            description: Optional description
            membership_life_span: How long users remain in the list (days,
                0-540). Omit to use the API default.

        Returns:
            Created user list details
        """
        try:
            customer_id = format_customer_id(customer_id)

            user_list = UserList()
            user_list.name = name
            if description:
                user_list.description = description
            if membership_life_span is not None:
                user_list.membership_life_span = membership_life_span

            set_optional_submessage(
                user_list,
                "lookalike_user_list",
                lookalike_user_list,
                LookalikeUserListInfo,
            )

            operation = UserListOperation()
            operation.create = user_list

            request = MutateUserListsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateUserListsResponse = self.client.mutate_user_lists(
                request=request
            )
            await ctx.log(
                level="info",
                message=f"Created lookalike user list '{name}'",
            )
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create lookalike user list: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def create_rule_based_user_list(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        rule_based_user_list: Dict[str, Any],
        description: Optional[str] = None,
        membership_life_span: Optional[int] = None,
        membership_status: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a rule-based user list.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: User list name
            rule_based_user_list: Dict that builds a
                ``RuleBasedUserListInfo`` submessage. See the v23
                reference for fields: ``prepopulation_status`` (REQUESTED
                / FINISHED / FAILED),
                ``flexible_rule_user_list``/``rule_event_filters`` etc.
            description: Optional description
            membership_life_span: How long users remain in the list
                (days, 0-540). Omit to use the API default.
            membership_status: OPEN or CLOSED. Omit to use the API
                default (OPEN).

        Returns:
            Created user list details
        """
        try:
            customer_id = format_customer_id(customer_id)

            user_list = UserList()
            user_list.name = name
            if description:
                user_list.description = description
            if membership_life_span is not None:
                user_list.membership_life_span = membership_life_span
            if membership_status is not None:
                user_list.membership_status = getattr(
                    UserListMembershipStatusEnum.UserListMembershipStatus,
                    membership_status,
                )

            set_optional_submessage(
                user_list,
                "rule_based_user_list",
                rule_based_user_list,
                RuleBasedUserListInfo,
            )

            operation = UserListOperation()
            operation.create = user_list

            request = MutateUserListsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: MutateUserListsResponse = self.client.mutate_user_lists(
                request=request
            )
            await ctx.log(
                level="info",
                message=f"Created rule-based user list '{name}'",
            )
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create rule-based user list: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_user_list(
        self,
        ctx: Context,
        customer_id: str,
        user_list_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        membership_status: Optional[str] = None,
        membership_life_span: Optional[int] = None,
        account_user_list_status: Optional[str] = None,
        closing_reason: Optional[str] = None,
        eligible_for_search: Optional[bool] = None,
        integration_code: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Update an existing user list.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            user_list_id: The user list ID to update
            name: New name (optional)
            description: New description (optional)
            membership_status: New status - OPEN or CLOSED (optional)
            membership_life_span: New membership life span in days (optional)
            account_user_list_status: Account-level user-list status
                (ENABLED or REMOVED). Whether the list is shared with
                this account.
            closing_reason: Reason this list is closed if it is closed —
                e.g. UNUSED.
            eligible_for_search: Whether the list is eligible for the
                Search network.
            integration_code: Free-text integration code stored on the
                list.

        Returns:
            Updated user list details
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/userLists/{user_list_id}"

            # Create user list with resource name
            user_list = UserList()
            user_list.resource_name = resource_name

            # Create update mask
            update_mask_fields = []

            if name is not None:
                user_list.name = name
                update_mask_fields.append("name")

            if description is not None:
                user_list.description = description
                update_mask_fields.append("description")

            if membership_status is not None:
                user_list.membership_status = getattr(
                    UserListMembershipStatusEnum.UserListMembershipStatus,
                    membership_status,
                )
                update_mask_fields.append("membership_status")

            if membership_life_span is not None:
                user_list.membership_life_span = membership_life_span
                update_mask_fields.append("membership_life_span")

            if account_user_list_status is not None:
                from google.ads.googleads.v23.enums.types.user_list_access_status import (
                    UserListAccessStatusEnum,
                )

                user_list.account_user_list_status = getattr(
                    UserListAccessStatusEnum.UserListAccessStatus,
                    account_user_list_status,
                )
                update_mask_fields.append("account_user_list_status")

            if closing_reason is not None:
                from google.ads.googleads.v23.enums.types.user_list_closing_reason import (
                    UserListClosingReasonEnum,
                )

                user_list.closing_reason = getattr(
                    UserListClosingReasonEnum.UserListClosingReason, closing_reason
                )
                update_mask_fields.append("closing_reason")

            if eligible_for_search is not None:
                user_list.eligible_for_search = eligible_for_search
                update_mask_fields.append("eligible_for_search")

            if integration_code is not None:
                user_list.integration_code = integration_code
                update_mask_fields.append("integration_code")

            if not update_mask_fields:
                raise ValueError("at least one updatable field must be provided")

            # Create the operation
            operation = UserListOperation()
            operation.update = user_list
            operation.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_fields)
            )

            # Create the request
            request = MutateUserListsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response = self.client.mutate_user_lists(request=request)

            await ctx.log(
                level="info",
                message=f"Updated user list {user_list_id}",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update user list: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_user_list(
        self,
        ctx: Context,
        customer_id: str,
        user_list_id: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Remove a user list permanently.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            user_list_id: The user list ID to remove

        Returns:
            Removal result details
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/userLists/{user_list_id}"

            # Create the operation
            operation = UserListOperation()
            operation.remove = resource_name

            # Create the request
            request = MutateUserListsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response = self.client.mutate_user_lists(request=request)

            await ctx.log(
                level="info",
                message=f"Removed user list {user_list_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove user list: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_user_list_tools(
    service: UserListService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the user list service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_basic_user_list(
        ctx: Context,
        customer_id: str,
        name: str,
        actions: List[Dict[str, str]],
        description: Optional[str] = None,
        membership_life_span: Optional[int] = None,
        membership_status: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a basic remarketing user list.

        Args:
            customer_id: The customer ID
            name: User list name
            actions: List of action dicts populating BasicUserListInfo.actions.
                Each dict must have exactly ONE of "conversion_action" or
                "remarketing_action" (resource name). Required — a list with
                no actions is unusable.
            description: Optional description
            membership_life_span: How long users remain in the list (days,
                0-540). Omit to use API default.
            membership_status: OPEN (can add users) or CLOSED. Omit to use
                API default (OPEN).
            partial_failure: If True, valid operations succeed when others fail in the same request.
            validate_only: If True, validate the request without executing it.
            response_content_type: Optional response-content-type override (e.g. 'MUTABLE_RESOURCE').


        """
        return await service.create_basic_user_list(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            actions=actions,
            description=description,
            membership_life_span=membership_life_span,
            membership_status=membership_status,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_crm_based_user_list(
        ctx: Context,
        customer_id: str,
        name: str,
        description: Optional[str] = None,
        membership_life_span: Optional[int] = None,
        upload_key_type: Optional[str] = None,
        data_source_type: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a CRM-based user list for customer match.

        Args:
            customer_id: The customer ID
            name: User list name
            description: Optional description
            membership_life_span: How long users remain in the list (days,
                0-540). Omit to use API default.
            upload_key_type: Optional - CONTACT_INFO, CRM_ID, or
                MOBILE_ADVERTISING_ID. Omit to use API default.
            data_source_type: Optional CRM data source. One of FIRST_PARTY,
                THIRD_PARTY_CREDIT_BUREAU, THIRD_PARTY_VOTER_FILE,
                THIRD_PARTY_PARTNER_DATA. Omit to use API default.
            partial_failure: If True, valid operations succeed when others fail in the same request.
            validate_only: If True, validate the request without executing it.
            response_content_type: Optional response-content-type override (e.g. 'MUTABLE_RESOURCE').


        """
        return await service.create_crm_based_user_list(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            description=description,
            membership_life_span=membership_life_span,
            upload_key_type=upload_key_type,
            data_source_type=data_source_type,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_logical_user_list(
        ctx: Context,
        customer_id: str,
        name: str,
        rules: List[Dict[str, Any]],
        description: Optional[str] = None,
        membership_life_span: Optional[int] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a logical (combined) user list.

        Args:
            customer_id: The customer ID
            name: User list name
            rules: List of rule dictionaries, each with:
                - user_list_ids: List of user list IDs
                - operator: ALL, ANY, or NONE (per-rule; the proto has no
                  top-level operator field)
            description: Optional description
            membership_life_span: How long users remain in the list (days,
                0-540). Omit to use API default.
            partial_failure: If True, valid operations succeed when others fail in the same request.
            validate_only: If True, validate the request without executing it.
            response_content_type: Optional response-content-type override (e.g. 'MUTABLE_RESOURCE').


        """
        return await service.create_logical_user_list(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            rules=rules,
            description=description,
            membership_life_span=membership_life_span,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_lookalike_user_list(
        ctx: Context,
        customer_id: str,
        name: str,
        lookalike_user_list: Dict[str, Any],
        description: Optional[str] = None,
        membership_life_span: Optional[int] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a lookalike user list (Immutable on the resource).

        Args:
            customer_id: The customer ID
            name: User list name
            lookalike_user_list: Dict that builds a LookalikeUserListInfo submessage. See v23 reference for fields (seed_user_list_ids, expansion_level, country_codes).
            description: Optional description
            membership_life_span: Membership lifespan in days (0-540).
            partial_failure: If True, valid operations succeed when others fail in the same request.
            validate_only: If True, validate the request without executing it.
            response_content_type: Optional response-content-type override (e.g. 'MUTABLE_RESOURCE').
        """
        return await service.create_lookalike_user_list(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            lookalike_user_list=lookalike_user_list,
            description=description,
            membership_life_span=membership_life_span,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def create_rule_based_user_list(
        ctx: Context,
        customer_id: str,
        name: str,
        rule_based_user_list: Dict[str, Any],
        description: Optional[str] = None,
        membership_life_span: Optional[int] = None,
        membership_status: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a rule-based user list.

        Args:
            customer_id: The customer ID
            name: User list name
            rule_based_user_list: Dict that builds a RuleBasedUserListInfo submessage. See v23 reference for fields (prepopulation_status, flexible_rule_user_list, rule_event_filters).
            description: Optional description
            membership_life_span: Membership lifespan in days (0-540).
            membership_status: OPEN or CLOSED. Omit to use API default.
            partial_failure: If True, valid operations succeed when others fail in the same request.
            validate_only: If True, validate the request without executing it.
            response_content_type: Optional response-content-type override (e.g. 'MUTABLE_RESOURCE').
        """
        return await service.create_rule_based_user_list(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            rule_based_user_list=rule_based_user_list,
            description=description,
            membership_life_span=membership_life_span,
            membership_status=membership_status,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def update_user_list(
        ctx: Context,
        customer_id: str,
        user_list_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        membership_status: Optional[str] = None,
        membership_life_span: Optional[int] = None,
        account_user_list_status: Optional[str] = None,
        closing_reason: Optional[str] = None,
        eligible_for_search: Optional[bool] = None,
        integration_code: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing user list.

        Args:
            customer_id: The customer ID
            user_list_id: The user list ID to update
            name: New name (optional)
            description: New description (optional)
            membership_status: New status - OPEN or CLOSED (optional)
            membership_life_span: New membership life span in days (optional)
            account_user_list_status: ENABLED or REMOVED — whether the
                list is shared with this account.
            closing_reason: Reason the list is closed (e.g. UNUSED).
            eligible_for_search: Whether the list is eligible for Search
                network usage.
            integration_code: Optional integration code stored on the list.
            partial_failure: If True, valid operations succeed when others fail in the same request.
            validate_only: If True, validate the request without executing it.
            response_content_type: Optional response-content-type override (e.g. 'MUTABLE_RESOURCE').


        """
        return await service.update_user_list(
            ctx=ctx,
            customer_id=customer_id,
            user_list_id=user_list_id,
            name=name,
            description=description,
            membership_status=membership_status,
            membership_life_span=membership_life_span,
            account_user_list_status=account_user_list_status,
            closing_reason=closing_reason,
            eligible_for_search=eligible_for_search,
            integration_code=integration_code,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def remove_user_list(
        ctx: Context,
        customer_id: str,
        user_list_id: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Remove a user list permanently. This action is irreversible.

        Args:
            customer_id: The customer ID
            user_list_id: The user list ID to remove

        Returns:
            Removal result details
        """
        return await service.remove_user_list(
            ctx=ctx,
            customer_id=customer_id,
            user_list_id=user_list_id,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    tools.extend(
        [
            create_basic_user_list,
            create_crm_based_user_list,
            create_logical_user_list,
            create_lookalike_user_list,
            create_rule_based_user_list,
            update_user_list,
            remove_user_list,
        ]
    )
    return tools


def register_user_list_tools(mcp: FastMCP[Any]) -> UserListService:
    """Register user list tools with the MCP server.

    Returns the UserListService instance for testing purposes.
    """
    service = UserListService()
    tools = create_user_list_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
