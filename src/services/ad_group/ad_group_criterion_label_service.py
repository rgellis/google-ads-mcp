"""Ad Group Criterion Label Service for Google Ads API v23.

This service manages label assignments to ad group criteria, allowing for better
organization and management of targeting criteria.
"""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.resources.types.ad_group_criterion_label import (
    AdGroupCriterionLabel,
)
from google.ads.googleads.v23.services.services.ad_group_criterion_label_service import (
    AdGroupCriterionLabelServiceClient,
)
from google.ads.googleads.v23.services.types.ad_group_criterion_label_service import (
    AdGroupCriterionLabelOperation,
    MutateAdGroupCriterionLabelsRequest,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class AdGroupCriterionLabelService:
    """Service for managing ad group criterion labels in Google Ads.

    Ad group criterion labels allow you to organize and categorize targeting criteria
    within ad groups for better management and reporting.
    """

    def __init__(self) -> None:
        """Initialize the ad group criterion label service."""
        self._client: Optional[AdGroupCriterionLabelServiceClient] = None

    @property
    def client(self) -> AdGroupCriterionLabelServiceClient:
        """Get the ad group criterion label service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("AdGroupCriterionLabelService")
        assert self._client is not None
        return self._client

    async def mutate_ad_group_criterion_labels(
        self,
        ctx: Context,
        customer_id: str,
        operations: List[AdGroupCriterionLabelOperation],
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Create or remove ad group criterion labels.

        Args:
            ctx: FastMCP context.
            customer_id: The customer ID.
            operations: List of operations to perform.
            partial_failure: If true, successful operations will be carried out and invalid
                operations will return errors.
            validate_only: If true, the request is validated but not executed.

        Returns:
            Serialized response dictionary.
        """
        try:
            customer_id = format_customer_id(customer_id)
            request = MutateAdGroupCriterionLabelsRequest(
                customer_id=customer_id,
                operations=operations,
                partial_failure=partial_failure,
                validate_only=validate_only,
            )
            response = self.client.mutate_ad_group_criterion_labels(request=request)
            await ctx.log(
                level="info",
                message=f"Successfully mutated {len(operations)} ad group criterion label(s) for customer {customer_id}",
            )
            return serialize_proto_message(response)
        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to mutate ad group criterion labels: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    def create_ad_group_criterion_label_operation(
        self,
        ad_group_criterion: str,
        label: str,
    ) -> AdGroupCriterionLabelOperation:
        """Create an ad group criterion label operation for creation.

        Args:
            ad_group_criterion: The ad group criterion resource name.
            label: The label resource name.

        Returns:
            AdGroupCriterionLabelOperation: The operation to create the label assignment.
        """
        ad_group_criterion_label = AdGroupCriterionLabel(
            ad_group_criterion=ad_group_criterion,
            label=label,
        )

        return AdGroupCriterionLabelOperation(create=ad_group_criterion_label)

    def create_remove_operation(
        self, resource_name: str
    ) -> AdGroupCriterionLabelOperation:
        """Create an ad group criterion label operation for removal.

        Args:
            resource_name: The resource name of the label assignment to remove.
                Format: customers/{customer_id}/adGroupCriterionLabels/{ad_group_id}~{criterion_id}~{label_id}

        Returns:
            AdGroupCriterionLabelOperation: The operation to remove the label assignment.
        """
        return AdGroupCriterionLabelOperation(remove=resource_name)

    async def assign_label_to_criterion(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_criterion: str,
        label: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Assign a label to an ad group criterion.

        Args:
            ctx: FastMCP context.
            customer_id: The customer ID.
            ad_group_criterion: The ad group criterion resource name.
            label: The label resource name.
            validate_only: If true, the request is validated but not executed.

        Returns:
            Serialized response dictionary.
        """
        operation = self.create_ad_group_criterion_label_operation(
            ad_group_criterion=ad_group_criterion,
            label=label,
        )

        return await self.mutate_ad_group_criterion_labels(
            ctx=ctx,
            customer_id=customer_id,
            operations=[operation],
            validate_only=validate_only,
        )

    async def remove_label_from_criterion(
        self,
        ctx: Context,
        customer_id: str,
        resource_name: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Remove a label assignment from an ad group criterion.

        Args:
            ctx: FastMCP context.
            customer_id: The customer ID.
            resource_name: The resource name of the label assignment to remove.
            validate_only: If true, the request is validated but not executed.

        Returns:
            Serialized response dictionary.
        """
        operation = self.create_remove_operation(resource_name=resource_name)

        return await self.mutate_ad_group_criterion_labels(
            ctx=ctx,
            customer_id=customer_id,
            operations=[operation],
            validate_only=validate_only,
        )

    async def assign_multiple_labels_to_criterion(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_criterion: str,
        labels: List[str],
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Assign multiple labels to an ad group criterion.

        Args:
            ctx: FastMCP context.
            customer_id: The customer ID.
            ad_group_criterion: The ad group criterion resource name.
            labels: List of label resource names.
            validate_only: If true, the request is validated but not executed.

        Returns:
            Serialized response dictionary.
        """
        operations = []
        for label in labels:
            operation = self.create_ad_group_criterion_label_operation(
                ad_group_criterion=ad_group_criterion,
                label=label,
            )
            operations.append(operation)

        return await self.mutate_ad_group_criterion_labels(
            ctx=ctx,
            customer_id=customer_id,
            operations=operations,
            validate_only=validate_only,
        )

    async def assign_label_to_multiple_criteria(
        self,
        ctx: Context,
        customer_id: str,
        ad_group_criteria: List[str],
        label: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Assign a label to multiple ad group criteria.

        Args:
            ctx: FastMCP context.
            customer_id: The customer ID.
            ad_group_criteria: List of ad group criterion resource names.
            label: The label resource name.
            validate_only: If true, the request is validated but not executed.

        Returns:
            Serialized response dictionary.
        """
        operations = []
        for ad_group_criterion in ad_group_criteria:
            operation = self.create_ad_group_criterion_label_operation(
                ad_group_criterion=ad_group_criterion,
                label=label,
            )
            operations.append(operation)

        return await self.mutate_ad_group_criterion_labels(
            ctx=ctx,
            customer_id=customer_id,
            operations=operations,
            validate_only=validate_only,
        )


def create_ad_group_criterion_label_tools(
    service: AdGroupCriterionLabelService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the ad group criterion label service."""
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def mutate_ad_group_criterion_labels(
        ctx: Context,
        customer_id: str,
        operations: list[dict[str, Any]],
        partial_failure: bool = False,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Create or remove ad group criterion labels.

        Args:
            customer_id: The customer ID
            operations: List of ad group criterion label operations
            partial_failure: Enable partial failure
            validate_only: Only validate the request

        Returns:
            Response with results
        """
        ops = []
        for op_data in operations:
            op_type = op_data["operation_type"]

            if op_type == "create":
                operation = service.create_ad_group_criterion_label_operation(
                    ad_group_criterion=op_data["ad_group_criterion"],
                    label=op_data["label"],
                )
            elif op_type == "remove":
                operation = service.create_remove_operation(
                    resource_name=op_data["resource_name"]
                )
            else:
                raise ValueError(f"Invalid operation type: {op_type}")

            ops.append(operation)

        return await service.mutate_ad_group_criterion_labels(
            ctx=ctx,
            customer_id=customer_id,
            operations=ops,
            partial_failure=partial_failure,
            validate_only=validate_only,
        )

    async def assign_label_to_criterion(
        ctx: Context,
        customer_id: str,
        ad_group_criterion: str,
        label: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Assign a label to an ad group criterion.

        Args:
            customer_id: The customer ID
            ad_group_criterion: The ad group criterion resource name
            label: The label resource name
            validate_only: Only validate the request

        Returns:
            Response with results
        """
        return await service.assign_label_to_criterion(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_criterion=ad_group_criterion,
            label=label,
            validate_only=validate_only,
        )

    async def remove_label_from_criterion(
        ctx: Context,
        customer_id: str,
        resource_name: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Remove a label from an ad group criterion.

        Args:
            customer_id: The customer ID
            resource_name: The ad group criterion label resource name
            validate_only: Only validate the request

        Returns:
            Response with results
        """
        return await service.remove_label_from_criterion(
            ctx=ctx,
            customer_id=customer_id,
            resource_name=resource_name,
            validate_only=validate_only,
        )

    async def assign_multiple_labels_to_criterion(
        ctx: Context,
        customer_id: str,
        ad_group_criterion: str,
        labels: list[str],
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Assign multiple labels to an ad group criterion.

        Args:
            customer_id: The customer ID
            ad_group_criterion: The ad group criterion resource name
            labels: List of label resource names
            validate_only: Only validate the request

        Returns:
            Response with results
        """
        return await service.assign_multiple_labels_to_criterion(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_criterion=ad_group_criterion,
            labels=labels,
            validate_only=validate_only,
        )

    async def assign_label_to_multiple_criteria(
        ctx: Context,
        customer_id: str,
        ad_group_criteria: list[str],
        label: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Assign a label to multiple ad group criteria.

        Args:
            customer_id: The customer ID
            ad_group_criteria: List of ad group criterion resource names
            label: The label resource name
            validate_only: Only validate the request

        Returns:
            Response with results
        """
        return await service.assign_label_to_multiple_criteria(
            ctx=ctx,
            customer_id=customer_id,
            ad_group_criteria=ad_group_criteria,
            label=label,
            validate_only=validate_only,
        )

    tools.extend(
        [
            mutate_ad_group_criterion_labels,
            assign_label_to_criterion,
            remove_label_from_criterion,
            assign_multiple_labels_to_criterion,
            assign_label_to_multiple_criteria,
        ]
    )
    return tools


def register_ad_group_criterion_label_tools(
    mcp: FastMCP[Any],
) -> AdGroupCriterionLabelService:
    """Register ad group criterion label tools with the MCP server."""
    service = AdGroupCriterionLabelService()
    tools = create_ad_group_criterion_label_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
