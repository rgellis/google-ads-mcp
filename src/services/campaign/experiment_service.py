"""Experiment service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.enums.types.experiment_status import ExperimentStatusEnum
from google.ads.googleads.v23.enums.types.experiment_type import ExperimentTypeEnum
from google.ads.googleads.v23.resources.types.experiment import Experiment
from google.ads.googleads.v23.services.services.experiment_service import (
    ExperimentServiceClient,
)
from google.ads.googleads.v23.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v23.services.types.experiment_service import (
    CampaignBudgetMapping,
    EndExperimentRequest,
    ExperimentOperation,
    GraduateExperimentRequest,
    ListExperimentAsyncErrorsRequest,
    MutateExperimentsRequest,
    MutateExperimentsResponse,
    PromoteExperimentRequest,
    ScheduleExperimentRequest,
)

from src.sdk_client import get_sdk_client
from src.utils import (
    format_customer_id,
    get_logger,
    serialize_proto_message,
    set_request_options,
)

logger = get_logger(__name__)


class ExperimentService:
    """Experiment service for A/B testing campaigns."""

    def __init__(self) -> None:
        """Initialize the experiment service."""
        self._client: Optional[ExperimentServiceClient] = None

    @property
    def client(self) -> ExperimentServiceClient:
        """Get the experiment service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("ExperimentService")
        assert self._client is not None
        return self._client

    async def create_experiment(
        self,
        ctx: Context,
        customer_id: str,
        name: str,
        description: Optional[str] = None,
        suffix: Optional[str] = None,
        experiment_type: str = "SEARCH_CUSTOM",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a new experiment for A/B testing.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            name: The experiment name
            description: Optional description
            suffix: Optional suffix for experiment campaigns
            experiment_type: Type of experiment (SEARCH_CUSTOM, DISPLAY_CUSTOM, etc.)
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)

        Returns:
            Created experiment details
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Create experiment
            experiment = Experiment()
            experiment.name = name
            experiment.type_ = getattr(
                ExperimentTypeEnum.ExperimentType, experiment_type
            )
            experiment.status = getattr(ExperimentStatusEnum.ExperimentStatus, "SETUP")

            if description:
                experiment.description = description
            if suffix:
                experiment.suffix = suffix

            # Set dates if provided
            if start_date:
                experiment.start_date = start_date
            if end_date:
                experiment.end_date = end_date

            # Create operation
            operation = ExperimentOperation()
            operation.create = experiment

            # Create request
            request = MutateExperimentsRequest()
            request.customer_id = customer_id
            request.operations = [operation]
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            # Make the API call
            response: MutateExperimentsResponse = self.client.mutate_experiments(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created experiment '{name}'",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create experiment: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def schedule_experiment(
        self,
        ctx: Context,
        customer_id: str,
        experiment_id: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Schedule an experiment to start running.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            experiment_id: The experiment ID to schedule
            validate_only: Only validate without scheduling

        Returns:
            Operation status
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/experiments/{experiment_id}"

            # Create request
            request = ScheduleExperimentRequest()
            request.resource_name = resource_name
            request.validate_only = validate_only

            # Make the API call
            response = self.client.schedule_experiment(request=request)

            await ctx.log(
                level="info",
                message=f"{'Validated' if validate_only else 'Scheduled'} experiment {experiment_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to schedule experiment: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def end_experiment(
        self,
        ctx: Context,
        customer_id: str,
        experiment_id: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """End a running experiment.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            experiment_id: The experiment ID to end
            validate_only: Only validate without ending

        Returns:
            Operation status
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/experiments/{experiment_id}"

            # Create request
            request = EndExperimentRequest()
            request.experiment = resource_name
            request.validate_only = validate_only

            # Make the API call
            response = self.client.end_experiment(request=request)

            await ctx.log(
                level="info",
                message=f"{'Validated ending' if validate_only else 'Ended'} experiment {experiment_id}",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to end experiment: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def promote_experiment(
        self,
        ctx: Context,
        customer_id: str,
        experiment_id: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Promote experiment changes to the base campaign.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            experiment_id: The experiment ID to promote
            validate_only: Only validate without promoting

        Returns:
            Operation status
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/experiments/{experiment_id}"

            # Create request
            request = PromoteExperimentRequest()
            request.resource_name = resource_name
            request.validate_only = validate_only

            # Make the API call
            response = self.client.promote_experiment(request=request)

            await ctx.log(
                level="info",
                message=f"{'Validated promoting' if validate_only else 'Promoted'} experiment {experiment_id}",
            )

            # Return serialized response
            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to promote experiment: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_experiments(
        self,
        ctx: Context,
        customer_id: str,
        campaign_id: Optional[str] = None,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List all experiments in the account.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            campaign_id: Optional filter by campaign
            status_filter: Optional filter by status

        Returns:
            List of experiments
        """
        try:
            customer_id = format_customer_id(customer_id)

            # Use GoogleAdsService for search
            sdk_client = get_sdk_client()
            google_ads_service: GoogleAdsServiceClient = sdk_client.client.get_service(
                "GoogleAdsService"
            )

            # Build query
            query = """
                SELECT
                    experiment.id,
                    experiment.name,
                    experiment.description,
                    experiment.status,
                    experiment.type,
                    experiment.traffic_split_percent,
                    experiment.campaigns,
                    experiment.start_date,
                    experiment.end_date,
                    experiment.resource_name
                FROM experiment
            """

            conditions = []
            if campaign_id:
                conditions.append(
                    f"experiment.campaigns CONTAINS 'customers/{customer_id}/campaigns/{campaign_id}'"
                )
            if status_filter:
                conditions.append(f"experiment.status = '{status_filter}'")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY experiment.name"

            # Execute search
            response = google_ads_service.search(customer_id=customer_id, query=query)

            # Process results
            experiments = []
            for row in response:
                experiments.append(serialize_proto_message(row))

            await ctx.log(
                level="info",
                message=f"Found {len(experiments)} experiments",
            )

            return experiments

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to list experiments: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def graduate_experiment(
        self,
        ctx: Context,
        customer_id: str,
        experiment_id: str,
        experiment_campaign: str,
        campaign_budget: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Graduate an experiment, making the experiment campaign standalone with its own budget.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            experiment_id: The experiment ID to graduate
            experiment_campaign: Resource name of the experiment campaign to graduate
            campaign_budget: Resource name of the budget to assign to the graduated campaign
            validate_only: Only validate without graduating

        Returns:
            Graduation status
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/experiments/{experiment_id}"

            mapping = CampaignBudgetMapping()
            mapping.experiment_campaign = experiment_campaign
            mapping.campaign_budget = campaign_budget

            request = GraduateExperimentRequest()
            request.experiment = resource_name
            request.campaign_budget_mappings = [mapping]
            request.validate_only = validate_only

            self.client.graduate_experiment(request=request)

            await ctx.log(
                level="info",
                message=f"{'Validated graduating' if validate_only else 'Graduated'} experiment {experiment_id}",
            )

            return {
                "status": "success",
                "experiment": resource_name,
                "graduated_campaign": experiment_campaign,
                "assigned_budget": campaign_budget,
                "validate_only": validate_only,
            }

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to graduate experiment: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_experiment_async_errors(
        self,
        ctx: Context,
        customer_id: str,
        experiment_id: str,
        page_size: int = 100,
        page_token: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List async errors from the most recent operation on an experiment.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            experiment_id: The experiment ID
            page_size: Maximum results per page (max 1000)
            page_token: Token for pagination

        Returns:
            List of async error details
        """
        try:
            customer_id = format_customer_id(customer_id)
            resource_name = f"customers/{customer_id}/experiments/{experiment_id}"

            request = ListExperimentAsyncErrorsRequest()
            request.resource_name = resource_name
            request.page_size = page_size
            if page_token:
                request.page_token = page_token

            pager = self.client.list_experiment_async_errors(request=request)

            errors = []
            for error in pager:
                errors.append(serialize_proto_message(error))

            await ctx.log(
                level="info",
                message=f"Found {len(errors)} async errors for experiment {experiment_id}",
            )

            return errors

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to list experiment async errors: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_experiment_tools(
    service: ExperimentService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the experiment service.

    This returns a list of tool functions that can be registered with FastMCP.
    This approach makes the tools testable by allowing service injection.
    """
    tools = []

    async def create_experiment(
        ctx: Context,
        customer_id: str,
        name: str,
        description: Optional[str] = None,
        suffix: Optional[str] = None,
        experiment_type: str = "SEARCH_CUSTOM",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new experiment for A/B testing campaigns.

        Note: After creating an experiment, you need to create experiment arms
        to link it to campaigns. Use the ExperimentArm service for that.

        Args:
            customer_id: The customer ID
            name: The experiment name
            description: Optional description of the experiment
            suffix: Optional suffix to append to experiment campaign names
            experiment_type: Type of experiment:
                - SEARCH_CUSTOM: For search campaigns
                - DISPLAY_CUSTOM: For display campaigns
                - VIDEO_CUSTOM: For video campaigns
                - SHOPPING_COMPARISON_LISTING_ADS: For shopping campaigns
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional)

        Returns:
            Created experiment details with resource_name and experiment_id
        """
        return await service.create_experiment(
            ctx=ctx,
            customer_id=customer_id,
            name=name,
            description=description,
            suffix=suffix,
            experiment_type=experiment_type,
            start_date=start_date,
            end_date=end_date,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def schedule_experiment(
        ctx: Context,
        customer_id: str,
        experiment_id: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Schedule an experiment to start running.

        Args:
            customer_id: The customer ID
            experiment_id: The experiment ID to schedule
            validate_only: Only validate without actually scheduling

        Returns:
            Operation status with experiment_id and status
        """
        return await service.schedule_experiment(
            ctx=ctx,
            customer_id=customer_id,
            experiment_id=experiment_id,
            validate_only=validate_only,
        )

    async def end_experiment(
        ctx: Context,
        customer_id: str,
        experiment_id: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """End a running experiment.

        Args:
            customer_id: The customer ID
            experiment_id: The experiment ID to end
            validate_only: Only validate without actually ending

        Returns:
            Operation status with experiment_id and status
        """
        return await service.end_experiment(
            ctx=ctx,
            customer_id=customer_id,
            experiment_id=experiment_id,
            validate_only=validate_only,
        )

    async def promote_experiment(
        ctx: Context,
        customer_id: str,
        experiment_id: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Promote experiment changes to the base campaign.

        This applies the experiment's changes permanently to the base campaign.

        Args:
            customer_id: The customer ID
            experiment_id: The experiment ID to promote
            validate_only: Only validate without actually promoting

        Returns:
            Operation status with experiment_id and status
        """
        return await service.promote_experiment(
            ctx=ctx,
            customer_id=customer_id,
            experiment_id=experiment_id,
            validate_only=validate_only,
        )

    async def list_experiments(
        ctx: Context,
        customer_id: str,
        campaign_id: Optional[str] = None,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List all experiments in the account.

        Args:
            customer_id: The customer ID
            campaign_id: Optional filter by campaign ID
            status_filter: Optional filter by status:
                - SETUP: Not yet started
                - INITIATED: Starting
                - RUNNING: Currently active
                - GRADUATED: Successfully completed
                - HALTED: Stopped early
                - PROMOTED: Changes applied to base campaign

        Returns:
            List of experiments with details
        """
        return await service.list_experiments(
            ctx=ctx,
            customer_id=customer_id,
            campaign_id=campaign_id,
            status_filter=status_filter,
        )

    async def graduate_experiment(
        ctx: Context,
        customer_id: str,
        experiment_id: str,
        experiment_campaign: str,
        campaign_budget: str,
        validate_only: bool = False,
    ) -> Dict[str, Any]:
        """Graduate an experiment, making the experiment campaign standalone.

        This creates a standalone campaign from the experiment with its own budget.

        Args:
            customer_id: The customer ID
            experiment_id: The experiment ID to graduate
            experiment_campaign: Resource name of the experiment campaign
            campaign_budget: Resource name of the budget to assign
            validate_only: Only validate without graduating

        Returns:
            Graduation status
        """
        return await service.graduate_experiment(
            ctx=ctx,
            customer_id=customer_id,
            experiment_id=experiment_id,
            experiment_campaign=experiment_campaign,
            campaign_budget=campaign_budget,
            validate_only=validate_only,
        )

    async def list_experiment_async_errors(
        ctx: Context,
        customer_id: str,
        experiment_id: str,
        page_size: int = 100,
        page_token: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List async errors from the most recent operation on an experiment.

        Use this to check for errors after scheduling or promoting an experiment.

        Args:
            customer_id: The customer ID
            experiment_id: The experiment ID
            page_size: Maximum results per page (max 1000)
            page_token: Token for pagination

        Returns:
            List of async error details
        """
        return await service.list_experiment_async_errors(
            ctx=ctx,
            customer_id=customer_id,
            experiment_id=experiment_id,
            page_size=page_size,
            page_token=page_token,
        )

    tools.extend(
        [
            create_experiment,
            schedule_experiment,
            end_experiment,
            promote_experiment,
            list_experiments,
            graduate_experiment,
            list_experiment_async_errors,
        ]
    )
    return tools


def register_experiment_tools(mcp: FastMCP[Any]) -> ExperimentService:
    """Register experiment tools with the MCP server.

    Returns the ExperimentService instance for testing purposes.
    """
    service = ExperimentService()
    tools = create_experiment_tools(service)

    # Register each tool
    for tool in tools:
        mcp.tool(tool)

    return service
