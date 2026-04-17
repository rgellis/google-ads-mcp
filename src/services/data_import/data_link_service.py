"""Data link service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.enums.types.data_link_status import DataLinkStatusEnum
from google.ads.googleads.v23.resources.types.data_link import DataLink
from google.ads.googleads.v23.services.services.data_link_service import (
    DataLinkServiceClient,
)
from google.ads.googleads.v23.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v23.services.types.data_link_service import (
    CreateDataLinkRequest,
    CreateDataLinkResponse,
    RemoveDataLinkRequest,
    RemoveDataLinkResponse,
    UpdateDataLinkRequest,
    UpdateDataLinkResponse,
)

from src.sdk_client import get_sdk_client
from src.utils import (
    format_customer_id,
    get_logger,
    serialize_proto_message,
    set_request_options,
)

logger = get_logger(__name__)


class DataLinkService:
    """Data link service for managing third-party data connections."""

    def __init__(self) -> None:
        """Initialize the data link service."""
        self._client: Optional[DataLinkServiceClient] = None

    @property
    def client(self) -> DataLinkServiceClient:
        """Get the data link service client."""
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("DataLinkService")
        assert self._client is not None
        return self._client

    async def create_data_link(
        self,
        ctx: Context,
        customer_id: str,
        youtube_video_channel_id: Optional[str] = None,
        youtube_video_video_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a data link.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            youtube_video_channel_id: YouTube channel ID (for YouTube video links)
            youtube_video_video_id: YouTube video ID (for YouTube video links)

        Returns:
            Created data link details
        """
        try:
            customer_id = format_customer_id(customer_id)

            data_link = DataLink()
            if youtube_video_channel_id or youtube_video_video_id:
                if youtube_video_channel_id:
                    data_link.youtube_video.channel_id = youtube_video_channel_id
                if youtube_video_video_id:
                    data_link.youtube_video.video_id = youtube_video_video_id

            request = CreateDataLinkRequest()
            request.customer_id = customer_id
            request.data_link = data_link

            response: CreateDataLinkResponse = self.client.create_data_link(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Created data link for customer {customer_id}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create data link: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_data_link(
        self,
        ctx: Context,
        customer_id: str,
        resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Remove a data link.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            resource_name: Resource name of the data link to remove

        Returns:
            Removal result with resource name
        """
        try:
            customer_id = format_customer_id(customer_id)

            request = RemoveDataLinkRequest()
            request.customer_id = customer_id
            request.resource_name = resource_name
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: RemoveDataLinkResponse = self.client.remove_data_link(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Removed data link: {resource_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove data link: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_data_link(
        self,
        ctx: Context,
        customer_id: str,
        resource_name: str,
        data_link_status: DataLinkStatusEnum.DataLinkStatus,
    ) -> Dict[str, Any]:
        """Update a data link's status.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            resource_name: Resource name of the data link to update
            data_link_status: New status (REQUESTED, PENDING_APPROVAL, ENABLED, DISABLED, REVOKED, REJECTED)

        Returns:
            Updated data link details
        """
        try:
            customer_id = format_customer_id(customer_id)

            request = UpdateDataLinkRequest()
            request.customer_id = customer_id
            request.resource_name = resource_name
            request.data_link_status = data_link_status

            response: UpdateDataLinkResponse = self.client.update_data_link(
                request=request
            )

            await ctx.log(
                level="info",
                message=f"Updated data link {resource_name} status to {data_link_status}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update data link: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def list_data_links(
        self,
        ctx: Context,
        customer_id: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """List data links for a customer.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            limit: Maximum number of results

        Returns:
            List of data links
        """
        try:
            customer_id = format_customer_id(customer_id)

            sdk_client = get_sdk_client()
            google_ads_service: GoogleAdsServiceClient = sdk_client.client.get_service(
                "GoogleAdsService"
            )

            query = f"""
                SELECT
                    data_link.resource_name,
                    data_link.data_link_id,
                    data_link.product_link_id,
                    data_link.type,
                    data_link.status
                FROM data_link
                LIMIT {limit}
            """

            response = google_ads_service.search(customer_id=customer_id, query=query)

            results = []
            for row in response:
                results.append(serialize_proto_message(row.data_link))

            await ctx.log(
                level="info",
                message=f"Found {len(results)} data links",
            )

            return results

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to list data links: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_data_link_tools(
    service: DataLinkService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the data link service."""
    tools = []

    async def create_data_link(
        ctx: Context,
        customer_id: str,
        youtube_video_channel_id: Optional[str] = None,
        youtube_video_video_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a data link.

        Args:
            customer_id: The customer ID
            youtube_video_channel_id: YouTube channel ID (for YouTube video links)
            youtube_video_video_id: YouTube video ID (for YouTube video links)

        Returns:
            Created data link details
        """
        return await service.create_data_link(
            ctx=ctx,
            customer_id=customer_id,
            youtube_video_channel_id=youtube_video_channel_id,
            youtube_video_video_id=youtube_video_video_id,
        )

    async def remove_data_link(
        ctx: Context,
        customer_id: str,
        resource_name: str,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Remove a data link.

        Args:
            customer_id: The customer ID
            resource_name: Resource name of the data link (e.g., customers/123/dataLinks/456)

        Returns:
            Removal result
        """
        return await service.remove_data_link(
            ctx=ctx,
            customer_id=customer_id,
            resource_name=resource_name,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def update_data_link(
        ctx: Context,
        customer_id: str,
        resource_name: str,
        data_link_status: str,
    ) -> Dict[str, Any]:
        """Update a data link's status.

        Args:
            customer_id: The customer ID
            resource_name: Resource name of the data link (e.g., customers/123/dataLinks/456)
            data_link_status: New status - REQUESTED, PENDING_APPROVAL, ENABLED, DISABLED, REVOKED, REJECTED

        Returns:
            Updated data link details
        """
        status_enum = getattr(DataLinkStatusEnum.DataLinkStatus, data_link_status)
        return await service.update_data_link(
            ctx=ctx,
            customer_id=customer_id,
            resource_name=resource_name,
            data_link_status=status_enum,
        )

    async def list_data_links(
        ctx: Context,
        customer_id: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """List data links for a customer.

        Args:
            customer_id: The customer ID
            limit: Maximum number of results

        Returns:
            List of data links
        """
        return await service.list_data_links(
            ctx=ctx,
            customer_id=customer_id,
            limit=limit,
        )

    tools.extend(
        [
            create_data_link,
            remove_data_link,
            update_data_link,
            list_data_links,
        ]
    )
    return tools


def register_data_link_tools(mcp: FastMCP[Any]) -> DataLinkService:
    """Register data link tools with the MCP server.

    Returns the DataLinkService instance for testing purposes.
    """
    service = DataLinkService()
    tools = create_data_link_tools(service)

    for tool in tools:
        mcp.tool(tool)

    return service
