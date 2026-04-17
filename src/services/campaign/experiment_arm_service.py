"""Google Ads Experiment Arm Service

This module provides functionality for managing experiment arms (variants) in Google Ads.
Experiment arms allow you to test different campaign configurations and compare performance.
"""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.resources.types.experiment_arm import ExperimentArm
from google.ads.googleads.v23.services.services.experiment_arm_service import (
    ExperimentArmServiceClient,
)
from google.ads.googleads.v23.services.types.experiment_arm_service import (
    ExperimentArmOperation,
    MutateExperimentArmsRequest,
)

from src.sdk_client import get_sdk_client
from src.utils import (
    format_customer_id,
    get_logger,
    serialize_proto_message,
    set_request_options,
)

logger = get_logger(__name__)


class ExperimentArmService:
    """Service for managing Google Ads experiment arms."""

    def __init__(self) -> None:
        """Initialize the experiment arm service."""
        self._client: Optional[ExperimentArmServiceClient] = None

    @property
    def client(self) -> ExperimentArmServiceClient:
        """Get the experiment arm service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("ExperimentArmService")
        assert self._client is not None
        return self._client

    async def mutate_experiment_arms(
        self,
        ctx: Context,
        customer_id: str,
        operations: List[ExperimentArmOperation],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Mutate experiment arms.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            operations: List of experiment arm operations
            partial_failure: Whether to enable partial failure
            validate_only: Whether to only validate the request
            response_content_type: Response content type enum value

        Returns:
            Serialized response containing results
        """
        try:
            customer_id = format_customer_id(customer_id)
            request = MutateExperimentArmsRequest(
                customer_id=customer_id,
                operations=operations,
            )
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )
            response = self.client.mutate_experiment_arms(request=request)
            await ctx.log(
                level="info",
                message=f"Successfully mutated {len(response.results)} experiment arms",
            )
            return serialize_proto_message(response)
        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to mutate experiment arms: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    def create_experiment_arm_operation(
        self,
        experiment: str,
        name: str,
        control: bool,
        traffic_split: int,
        campaigns: Optional[List[str]] = None,
    ) -> ExperimentArmOperation:
        """Create an experiment arm operation for creation.

        Args:
            experiment: The experiment resource name
            name: The name of the experiment arm
            control: Whether this is a control arm
            traffic_split: Traffic split percentage (1-100)
            campaigns: List of campaign resource names

        Returns:
            ExperimentArmOperation: The operation to create the experiment arm
        """
        experiment_arm = ExperimentArm(
            experiment=experiment,
            name=name,
            control=control,
            traffic_split=traffic_split,
            campaigns=campaigns or [],
        )

        return ExperimentArmOperation(create=experiment_arm)

    def update_experiment_arm_operation(
        self,
        resource_name: str,
        name: Optional[str] = None,
        traffic_split: Optional[int] = None,
        campaigns: Optional[List[str]] = None,
    ) -> ExperimentArmOperation:
        """Create an experiment arm operation for update.

        Args:
            resource_name: The experiment arm resource name
            name: The name of the experiment arm
            traffic_split: Traffic split percentage (1-100)
            campaigns: List of campaign resource names

        Returns:
            ExperimentArmOperation: The operation to update the experiment arm
        """
        experiment_arm = ExperimentArm(resource_name=resource_name)

        update_mask = []
        if name is not None:
            experiment_arm.name = name
            update_mask.append("name")
        if traffic_split is not None:
            experiment_arm.traffic_split = traffic_split
            update_mask.append("traffic_split")
        if campaigns is not None:
            experiment_arm.campaigns = campaigns
            update_mask.append("campaigns")

        return ExperimentArmOperation(
            update=experiment_arm,
            update_mask={"paths": update_mask},
        )

    def remove_experiment_arm_operation(
        self, resource_name: str
    ) -> ExperimentArmOperation:
        """Create an experiment arm operation for removal.

        Args:
            resource_name: The experiment arm resource name

        Returns:
            ExperimentArmOperation: The operation to remove the experiment arm
        """
        return ExperimentArmOperation(remove=resource_name)


def create_experiment_arm_tools(
    service: ExperimentArmService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create experiment arm tools for MCP."""
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def mutate_experiment_arms(
        ctx: Context,
        customer_id: str,
        operations: list[dict[str, Any]],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create, update, or remove experiment arms (variants in an A/B test).

        Args:
            customer_id: The customer ID
            operations: List of experiment arm operations. Each dict must have:
                - operation_type: "create", "update", or "remove"
                For create:
                    - experiment: Experiment resource name (e.g. customers/123/experiments/456)
                    - name: Name of the arm (e.g. "Control" or "Treatment")
                    - control: true for the control arm, false for treatment
                    - traffic_split: Percentage of traffic for this arm (1-100)
                    - campaigns: List of campaign resource names (optional)
                For update:
                    - resource_name: The experiment arm resource name
                    - name, traffic_split, campaigns: Fields to update (all optional)
                For remove:
                    - resource_name: The experiment arm resource name

        Returns:
            Mutation results with created/updated/removed resource names
        """
        ops = []
        for op_data in operations:
            op_type = op_data["operation_type"]

            if op_type == "create":
                operation = service.create_experiment_arm_operation(
                    experiment=op_data["experiment"],
                    name=op_data["name"],
                    control=op_data["control"],
                    traffic_split=op_data["traffic_split"],
                    campaigns=op_data.get("campaigns", []),
                )
            elif op_type == "update":
                operation = service.update_experiment_arm_operation(
                    resource_name=op_data["resource_name"],
                    name=op_data.get("name"),
                    traffic_split=op_data.get("traffic_split"),
                    campaigns=op_data.get("campaigns"),
                )
            elif op_type == "remove":
                operation = service.remove_experiment_arm_operation(
                    resource_name=op_data["resource_name"]
                )
            else:
                raise ValueError(f"Invalid operation type: {op_type}")

            ops.append(operation)

        return await service.mutate_experiment_arms(
            ctx=ctx,
            customer_id=customer_id,
            operations=ops,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    tools.append(mutate_experiment_arms)

    async def create_experiment_arm(
        ctx: Context,
        customer_id: str,
        experiment: str,
        name: str,
        control: bool,
        traffic_split: int,
        campaigns: list[str] = [],
    ) -> Dict[str, Any]:
        """Create a new experiment arm (variant in an A/B test).

        Args:
            customer_id: The customer ID
            experiment: The experiment resource name (e.g. customers/123/experiments/456)
            name: Name of the arm (e.g. "Control" or "Treatment")
            control: true if this is the control arm (baseline), false for treatment (test variant)
            traffic_split: Percentage of traffic routed to this arm (1-100, all arms must sum to 100)
            campaigns: List of campaign resource names to include in this arm

        Returns:
            Created experiment arm details with resource name
        """
        operation = service.create_experiment_arm_operation(
            experiment=experiment,
            name=name,
            control=control,
            traffic_split=traffic_split,
            campaigns=campaigns,
        )

        return await service.mutate_experiment_arms(
            ctx=ctx, customer_id=customer_id, operations=[operation]
        )

    tools.append(create_experiment_arm)

    async def update_experiment_arm(
        ctx: Context,
        customer_id: str,
        resource_name: str,
        name: Optional[str] = None,
        traffic_split: Optional[int] = None,
        campaigns: Optional[list[str]] = None,
    ) -> Dict[str, Any]:
        """Update an existing experiment arm.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            resource_name: The experiment arm resource name
            name: Name of the experiment arm
            traffic_split: Traffic split percentage (1-100)
            campaigns: List of campaign resource names

        Returns:
            Serialized response with updated experiment arm details
        """
        operation = service.update_experiment_arm_operation(
            resource_name=resource_name,
            name=name,
            traffic_split=traffic_split,
            campaigns=campaigns,
        )

        return await service.mutate_experiment_arms(
            ctx=ctx, customer_id=customer_id, operations=[operation]
        )

    tools.append(update_experiment_arm)

    async def remove_experiment_arm(
        ctx: Context,
        customer_id: str,
        resource_name: str,
    ) -> Dict[str, Any]:
        """Remove an experiment arm.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            resource_name: The experiment arm resource name

        Returns:
            Serialized response confirming removal
        """
        operation = service.remove_experiment_arm_operation(resource_name=resource_name)

        return await service.mutate_experiment_arms(
            ctx=ctx, customer_id=customer_id, operations=[operation]
        )

    tools.append(remove_experiment_arm)

    return tools


def register_experiment_arm_tools(mcp: FastMCP[Any]) -> ExperimentArmService:
    """Register experiment arm tools with the MCP server."""
    service = ExperimentArmService()
    tools = create_experiment_arm_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
