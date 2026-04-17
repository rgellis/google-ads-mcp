"""Local services lead service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.services.services.local_services_lead_service import (
    LocalServicesLeadServiceClient,
)
from google.ads.googleads.v23.services.types.local_services_lead_service import (
    AppendLeadConversationRequest,
    AppendLeadConversationResponse,
    Conversation,
    ProvideLeadFeedbackRequest,
    ProvideLeadFeedbackResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import format_customer_id, get_logger, serialize_proto_message

logger = get_logger(__name__)


class LocalServicesLeadService:
    def __init__(self) -> None:
        self._client: Optional[LocalServicesLeadServiceClient] = None

    @property
    def client(self) -> LocalServicesLeadServiceClient:
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("LocalServicesLeadService")
        assert self._client is not None
        return self._client

    async def append_lead_conversation(
        self, ctx: Context, customer_id: str, conversations: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        try:
            customer_id = format_customer_id(customer_id)
            conv_objects = []
            for conv in conversations:
                c = Conversation()
                c.local_services_lead = conv["local_services_lead"]
                c.text = conv["text"]
                conv_objects.append(c)
            request = AppendLeadConversationRequest()
            request.customer_id = customer_id
            request.conversations = conv_objects
            response: AppendLeadConversationResponse = (
                self.client.append_lead_conversation(request=request)
            )
            await ctx.log(
                level="info", message=f"Appended {len(conversations)} conversations"
            )
            return serialize_proto_message(response)
        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to append lead conversation: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def provide_lead_feedback(
        self,
        ctx: Context,
        resource_name: str,
        survey_answer: str,
        satisfied_reason: Optional[str] = None,
        satisfied_comment: Optional[str] = None,
        dissatisfied_reason: Optional[str] = None,
        dissatisfied_comment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Provide feedback for a Local Services lead.

        Args:
            ctx: FastMCP context
            resource_name: Lead resource name
            survey_answer: Feedback answer - SATISFIED or DISSATISFIED
            satisfied_reason: Reason for satisfaction (when SATISFIED)
            satisfied_comment: Additional comment (when SATISFIED)
            dissatisfied_reason: Reason for dissatisfaction (when DISSATISFIED)
            dissatisfied_comment: Additional comment (when DISSATISFIED)

        Returns:
            Feedback submission result
        """
        try:
            from google.ads.googleads.v23.enums.types.local_services_lead_survey_answer import (
                LocalServicesLeadSurveyAnswerEnum,
            )
            from google.ads.googleads.v23.services.types.local_services_lead_service import (
                SurveyDissatisfied,
                SurveySatisfied,
            )

            request = ProvideLeadFeedbackRequest()
            request.resource_name = resource_name
            request.survey_answer = getattr(
                LocalServicesLeadSurveyAnswerEnum.SurveyAnswer,
                survey_answer,
            )

            if satisfied_reason is not None or satisfied_comment is not None:
                survey_satisfied = SurveySatisfied()
                if satisfied_reason is not None:
                    reason_enum = type(survey_satisfied.survey_satisfied_reason)
                    survey_satisfied.survey_satisfied_reason = reason_enum[
                        satisfied_reason
                    ]
                if satisfied_comment is not None:
                    survey_satisfied.other_reason_comment = satisfied_comment
                request.survey_satisfied = survey_satisfied

            if dissatisfied_reason is not None or dissatisfied_comment is not None:
                survey_dissatisfied = SurveyDissatisfied()
                if dissatisfied_reason is not None:
                    reason_enum = type(survey_dissatisfied.survey_dissatisfied_reason)
                    survey_dissatisfied.survey_dissatisfied_reason = reason_enum[
                        dissatisfied_reason
                    ]
                if dissatisfied_comment is not None:
                    survey_dissatisfied.other_reason_comment = dissatisfied_comment
                request.survey_dissatisfied = survey_dissatisfied

            response: ProvideLeadFeedbackResponse = self.client.provide_lead_feedback(
                request=request
            )
            await ctx.log(
                level="info", message=f"Provided feedback for lead {resource_name}"
            )
            return serialize_proto_message(response)
        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to provide lead feedback: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_local_services_lead_tools(
    service: LocalServicesLeadService,
) -> List[Callable[..., Awaitable[Any]]]:
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def append_lead_conversation(
        ctx: Context, customer_id: str, conversations: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Append conversation messages to Local Services leads (for service providers using Local Services Ads).

        Args:
            customer_id: The customer ID
            conversations: List of dicts, each with:
                - local_services_lead: Lead resource name (e.g. customers/123/localServicesLeads/456)
                - text: The message text to append

        Returns:
            Append results with status for each conversation
        """
        return await service.append_lead_conversation(
            ctx=ctx, customer_id=customer_id, conversations=conversations
        )

    async def provide_lead_feedback(
        ctx: Context,
        resource_name: str,
        survey_answer: str,
        satisfied_reason: Optional[str] = None,
        satisfied_comment: Optional[str] = None,
        dissatisfied_reason: Optional[str] = None,
        dissatisfied_comment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Provide feedback for a Local Services lead to improve lead quality.

        Args:
            resource_name: Lead resource name (e.g. customers/123/localServicesLeads/456)
            survey_answer: Feedback answer - SATISFIED or DISSATISFIED
            satisfied_reason: Reason for satisfaction (when SATISFIED) -
                BOOKED_CUSTOMER, LIKELY_BOOKED_CUSTOMER, SERVICE_RELATED,
                HIGH_VALUE_SERVICE, OTHER_SATISFIED_REASON
            satisfied_comment: Additional comment for satisfaction feedback
            dissatisfied_reason: Reason for dissatisfaction (when DISSATISFIED) -
                GEO_MISMATCH, JOB_TYPE_MISMATCH, NOT_READY_TO_BOOK, SPAM,
                DUPLICATE, SOLICITATION, OTHER_DISSATISFIED_REASON
            dissatisfied_comment: Additional comment for dissatisfaction feedback

        Returns:
            Feedback submission result
        """
        return await service.provide_lead_feedback(
            ctx=ctx,
            resource_name=resource_name,
            survey_answer=survey_answer,
            satisfied_reason=satisfied_reason,
            satisfied_comment=satisfied_comment,
            dissatisfied_reason=dissatisfied_reason,
            dissatisfied_comment=dissatisfied_comment,
        )

    tools.extend([append_lead_conversation, provide_lead_feedback])
    return tools


def register_local_services_lead_tools(mcp: FastMCP[Any]) -> LocalServicesLeadService:
    service = LocalServicesLeadService()
    tools = create_local_services_lead_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
