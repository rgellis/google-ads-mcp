"""YouTube video upload service implementation using Google Ads SDK."""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import Context, FastMCP
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.resources.types.youtube_video_upload import (
    YouTubeVideoUpload,
)
from google.ads.googleads.v23.services.services.you_tube_video_upload_service import (
    YouTubeVideoUploadServiceClient,
)
from google.ads.googleads.v23.services.types.youtube_video_upload_service import (
    CreateYouTubeVideoUploadRequest,
    CreateYouTubeVideoUploadResponse,
    RemoveYouTubeVideoUploadRequest,
    RemoveYouTubeVideoUploadResponse,
    UpdateYouTubeVideoUploadRequest,
    UpdateYouTubeVideoUploadResponse,
)
from google.protobuf import field_mask_pb2

from src.sdk_client import get_sdk_client
from src.utils import (
    format_customer_id,
    get_logger,
    serialize_proto_message,
    set_request_options,
)

logger = get_logger(__name__)


class YouTubeVideoUploadService:
    """Service for managing YouTube video uploads via the Ads API."""

    def __init__(self) -> None:
        self._client: Optional[YouTubeVideoUploadServiceClient] = None

    @property
    def client(self) -> YouTubeVideoUploadServiceClient:
        if self._client is None:
            sdk_client = get_sdk_client()
            self._client = sdk_client.client.get_service("YouTubeVideoUploadService")
        assert self._client is not None
        return self._client

    async def create_youtube_video_upload(
        self,
        ctx: Context,
        customer_id: str,
        channel_id: str,
        video_title: str,
        video_file_path: str,
        video_description: Optional[str] = None,
        video_privacy: str = "PRIVATE",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Create a YouTube video upload.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            channel_id: YouTube channel ID
            video_title: Title for the video
            video_file_path: Path to the video file
            video_description: Optional description
            video_privacy: Privacy setting (PRIVATE, PUBLIC, UNLISTED)

        Returns:
            Created video upload details
        """
        try:
            customer_id = format_customer_id(customer_id)

            from google.ads.googleads.v23.enums.types.youtube_video_privacy import (
                YouTubeVideoPrivacyEnum,
            )

            upload = YouTubeVideoUpload()
            upload.channel_id = channel_id
            upload.video_title = video_title
            upload.video_privacy = getattr(
                YouTubeVideoPrivacyEnum.YouTubeVideoPrivacy, video_privacy
            )
            if video_description:
                upload.video_description = video_description

            request = CreateYouTubeVideoUploadRequest()
            request.customer_id = customer_id
            request.you_tube_video_upload = upload
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            with open(video_file_path, "rb") as stream:
                response: CreateYouTubeVideoUploadResponse = (
                    self.client.create_you_tube_video_upload(
                        request=request, stream=stream
                    )
                )

            await ctx.log(
                level="info",
                message=f"Created YouTube video upload: {video_title}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to create YouTube video upload: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def update_youtube_video_upload(
        self,
        ctx: Context,
        customer_id: str,
        resource_name: str,
        video_title: Optional[str] = None,
        video_description: Optional[str] = None,
        video_privacy: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Update a YouTube video upload.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            resource_name: Resource name of the video upload
            video_title: New title (optional)
            video_description: New description (optional)
            video_privacy: New privacy setting (optional)

        Returns:
            Updated video upload details
        """
        try:
            customer_id = format_customer_id(customer_id)

            upload = YouTubeVideoUpload()
            upload.resource_name = resource_name

            update_mask_fields = []
            if video_title is not None:
                upload.video_title = video_title
                update_mask_fields.append("video_title")
            if video_description is not None:
                upload.video_description = video_description
                update_mask_fields.append("video_description")
            if video_privacy is not None:
                from google.ads.googleads.v23.enums.types.youtube_video_privacy import (
                    YouTubeVideoPrivacyEnum,
                )

                upload.video_privacy = getattr(
                    YouTubeVideoPrivacyEnum.YouTubeVideoPrivacy, video_privacy
                )
                update_mask_fields.append("video_privacy")

            request = UpdateYouTubeVideoUploadRequest()
            request.customer_id = customer_id
            request.you_tube_video_upload = upload
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )
            request.update_mask.CopyFrom(
                field_mask_pb2.FieldMask(paths=update_mask_fields)
            )

            response: UpdateYouTubeVideoUploadResponse = (
                self.client.update_you_tube_video_upload(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Updated YouTube video upload: {resource_name}",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to update YouTube video upload: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e

    async def remove_youtube_video_uploads(
        self,
        ctx: Context,
        customer_id: str,
        resource_names: List[str],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Any = None,
    ) -> Dict[str, Any]:
        """Remove YouTube video uploads.

        Args:
            ctx: FastMCP context
            customer_id: The customer ID
            resource_names: List of resource names to remove

        Returns:
            Removal result
        """
        try:
            customer_id = format_customer_id(customer_id)

            request = RemoveYouTubeVideoUploadRequest()
            request.customer_id = customer_id
            request.resource_names = resource_names
            set_request_options(
                request,
                partial_failure=partial_failure,
                validate_only=validate_only,
                response_content_type=response_content_type,
            )

            response: RemoveYouTubeVideoUploadResponse = (
                self.client.remove_you_tube_video_upload(request=request)
            )

            await ctx.log(
                level="info",
                message=f"Removed {len(resource_names)} YouTube video uploads",
            )

            return serialize_proto_message(response)

        except GoogleAdsException as e:
            error_msg = f"Google Ads API error: {e.failure}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to remove YouTube video uploads: {str(e)}"
            await ctx.log(level="error", message=error_msg)
            raise Exception(error_msg) from e


def create_youtube_video_upload_tools(
    service: YouTubeVideoUploadService,
) -> List[Callable[..., Awaitable[Any]]]:
    """Create tool functions for the YouTube video upload service."""
    tools: List[Callable[..., Awaitable[Any]]] = []

    async def create_youtube_video_upload(
        ctx: Context,
        customer_id: str,
        channel_id: str,
        video_title: str,
        video_file_path: str,
        video_description: Optional[str] = None,
        video_privacy: str = "PRIVATE",
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a YouTube video upload for use in video campaigns.

        Args:
            customer_id: The customer ID
            channel_id: YouTube channel ID
            video_title: Title for the video
            video_file_path: Path to the video file
            video_description: Optional description
            video_privacy: PRIVATE, PUBLIC, or UNLISTED
        """
        return await service.create_youtube_video_upload(
            ctx=ctx,
            customer_id=customer_id,
            channel_id=channel_id,
            video_title=video_title,
            video_file_path=video_file_path,
            video_description=video_description,
            video_privacy=video_privacy,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def update_youtube_video_upload(
        ctx: Context,
        customer_id: str,
        resource_name: str,
        video_title: Optional[str] = None,
        video_description: Optional[str] = None,
        video_privacy: Optional[str] = None,
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a YouTube video upload.

        Args:
            customer_id: The customer ID
            resource_name: Resource name of the video upload
            video_title: New title
            video_description: New description
            video_privacy: PRIVATE, PUBLIC, or UNLISTED
        """
        return await service.update_youtube_video_upload(
            ctx=ctx,
            customer_id=customer_id,
            resource_name=resource_name,
            video_title=video_title,
            video_description=video_description,
            video_privacy=video_privacy,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    async def remove_youtube_video_uploads(
        ctx: Context,
        customer_id: str,
        resource_names: List[str],
        partial_failure: bool = False,
        validate_only: bool = False,
        response_content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Remove YouTube video uploads.

        Args:
            customer_id: The customer ID
            resource_names: List of resource names to remove
        """
        return await service.remove_youtube_video_uploads(
            ctx=ctx,
            customer_id=customer_id,
            resource_names=resource_names,
            partial_failure=partial_failure,
            validate_only=validate_only,
            response_content_type=response_content_type,
        )

    tools.extend(
        [
            create_youtube_video_upload,
            update_youtube_video_upload,
            remove_youtube_video_uploads,
        ]
    )
    return tools


def register_youtube_video_upload_tools(
    mcp: FastMCP[Any],
) -> YouTubeVideoUploadService:
    """Register YouTube video upload tools with the MCP server."""
    service = YouTubeVideoUploadService()
    tools = create_youtube_video_upload_tools(service)
    for tool in tools:
        mcp.tool(tool)
    return service
