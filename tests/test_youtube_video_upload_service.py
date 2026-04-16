"""Tests for YouTubeVideoUploadService."""

from typing import Any
from unittest.mock import Mock, mock_open, patch

import pytest
from fastmcp import Context

from src.services.assets.youtube_video_upload_service import (
    YouTubeVideoUploadService,
    register_youtube_video_upload_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> YouTubeVideoUploadService:
    """Create a YouTubeVideoUploadService instance with mocked dependencies."""
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client  # type: ignore

    with patch(
        "src.services.assets.youtube_video_upload_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = YouTubeVideoUploadService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_create_youtube_video_upload(
    service: YouTubeVideoUploadService,
    mock_ctx: Context,
) -> None:
    """Test creating a YouTube video upload."""
    mock_client = service.client
    mock_client.create_you_tube_video_upload.return_value = Mock()  # type: ignore

    expected_result = {
        "resource_name": "customers/1234567890/youTubeVideoUploads/abc123"
    }

    m = mock_open(read_data=b"video data")
    with (
        patch("builtins.open", m),
        patch(
            "src.services.assets.youtube_video_upload_service.serialize_proto_message",
            return_value=expected_result,
        ),
    ):
        result = await service.create_youtube_video_upload(
            ctx=mock_ctx,
            customer_id="1234567890",
            channel_id="UCxxxxxx",
            video_title="My Test Video",
            video_file_path="/tmp/test_video.mp4",
        )

    assert result == expected_result
    mock_client.create_you_tube_video_upload.assert_called_once()  # type: ignore
    call_args = mock_client.create_you_tube_video_upload.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == "1234567890"
    assert request.you_tube_video_upload.channel_id == "UCxxxxxx"
    assert request.you_tube_video_upload.video_title == "My Test Video"


@pytest.mark.asyncio
async def test_create_youtube_video_upload_with_description(
    service: YouTubeVideoUploadService,
    mock_ctx: Context,
) -> None:
    """Test creating a YouTube video upload with description."""
    mock_client = service.client
    mock_client.create_you_tube_video_upload.return_value = Mock()  # type: ignore

    expected_result = {
        "resource_name": "customers/1234567890/youTubeVideoUploads/abc123"
    }

    m = mock_open(read_data=b"video data")
    with (
        patch("builtins.open", m),
        patch(
            "src.services.assets.youtube_video_upload_service.serialize_proto_message",
            return_value=expected_result,
        ),
    ):
        result = await service.create_youtube_video_upload(
            ctx=mock_ctx,
            customer_id="1234567890",
            channel_id="UCxxxxxx",
            video_title="My Test Video",
            video_file_path="/tmp/test_video.mp4",
            video_description="This is my test video description",
            video_privacy="PUBLIC",
        )

    assert result == expected_result
    call_args = mock_client.create_you_tube_video_upload.call_args  # type: ignore
    request = call_args[1]["request"]
    assert (
        request.you_tube_video_upload.video_description
        == "This is my test video description"
    )


@pytest.mark.asyncio
async def test_create_youtube_video_upload_error(
    service: YouTubeVideoUploadService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when creating YouTube video upload fails."""
    mock_client = service.client
    mock_client.create_you_tube_video_upload.side_effect = google_ads_exception  # type: ignore

    m = mock_open(read_data=b"video data")
    with patch("builtins.open", m), pytest.raises(Exception) as exc_info:
        await service.create_youtube_video_upload(
            ctx=mock_ctx,
            customer_id="1234567890",
            channel_id="UCxxxxxx",
            video_title="My Test Video",
            video_file_path="/tmp/test_video.mp4",
        )

    assert "Test Google Ads Exception" in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_youtube_video_upload(
    service: YouTubeVideoUploadService,
    mock_ctx: Context,
) -> None:
    """Test updating a YouTube video upload."""
    mock_client = service.client
    mock_client.update_you_tube_video_upload.return_value = Mock()  # type: ignore

    expected_result = {
        "resource_name": "customers/1234567890/youTubeVideoUploads/abc123"
    }

    with patch(
        "src.services.assets.youtube_video_upload_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.update_youtube_video_upload(
            ctx=mock_ctx,
            customer_id="1234567890",
            resource_name="customers/1234567890/youTubeVideoUploads/abc123",
            video_title="Updated Title",
        )

    assert result == expected_result
    mock_client.update_you_tube_video_upload.assert_called_once()  # type: ignore
    call_args = mock_client.update_you_tube_video_upload.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == "1234567890"
    assert (
        request.you_tube_video_upload.resource_name
        == "customers/1234567890/youTubeVideoUploads/abc123"
    )
    assert request.you_tube_video_upload.video_title == "Updated Title"
    assert "video_title" in list(request.update_mask.paths)


@pytest.mark.asyncio
async def test_update_youtube_video_upload_multiple_fields(
    service: YouTubeVideoUploadService,
    mock_ctx: Context,
) -> None:
    """Test updating multiple fields of a YouTube video upload."""
    mock_client = service.client
    mock_client.update_you_tube_video_upload.return_value = Mock()  # type: ignore

    expected_result = {
        "resource_name": "customers/1234567890/youTubeVideoUploads/abc123"
    }

    with patch(
        "src.services.assets.youtube_video_upload_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.update_youtube_video_upload(
            ctx=mock_ctx,
            customer_id="1234567890",
            resource_name="customers/1234567890/youTubeVideoUploads/abc123",
            video_title="New Title",
            video_description="New Description",
            video_privacy="PUBLIC",
        )

    assert result == expected_result
    call_args = mock_client.update_you_tube_video_upload.call_args  # type: ignore
    request = call_args[1]["request"]
    mask_paths = list(request.update_mask.paths)
    assert "video_title" in mask_paths
    assert "video_description" in mask_paths
    assert "video_privacy" in mask_paths


@pytest.mark.asyncio
async def test_update_youtube_video_upload_error(
    service: YouTubeVideoUploadService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when updating YouTube video upload fails."""
    mock_client = service.client
    mock_client.update_you_tube_video_upload.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.update_youtube_video_upload(
            ctx=mock_ctx,
            customer_id="1234567890",
            resource_name="customers/1234567890/youTubeVideoUploads/abc123",
            video_title="Updated Title",
        )

    assert "Test Google Ads Exception" in str(exc_info.value)


@pytest.mark.asyncio
async def test_remove_youtube_video_uploads(
    service: YouTubeVideoUploadService,
    mock_ctx: Context,
) -> None:
    """Test removing YouTube video uploads."""
    mock_client = service.client
    mock_client.remove_you_tube_video_upload.return_value = Mock()  # type: ignore

    expected_result = {"results": []}

    with patch(
        "src.services.assets.youtube_video_upload_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.remove_youtube_video_uploads(
            ctx=mock_ctx,
            customer_id="1234567890",
            resource_names=[
                "customers/1234567890/youTubeVideoUploads/abc123",
                "customers/1234567890/youTubeVideoUploads/def456",
            ],
        )

    assert result == expected_result
    mock_client.remove_you_tube_video_upload.assert_called_once()  # type: ignore
    call_args = mock_client.remove_you_tube_video_upload.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == "1234567890"
    assert list(request.resource_names) == [
        "customers/1234567890/youTubeVideoUploads/abc123",
        "customers/1234567890/youTubeVideoUploads/def456",
    ]


@pytest.mark.asyncio
async def test_remove_youtube_video_uploads_error(
    service: YouTubeVideoUploadService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when removing YouTube video uploads fails."""
    mock_client = service.client
    mock_client.remove_you_tube_video_upload.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.remove_youtube_video_uploads(
            ctx=mock_ctx,
            customer_id="1234567890",
            resource_names=["customers/1234567890/youTubeVideoUploads/abc123"],
        )

    assert "Test Google Ads Exception" in str(exc_info.value)


def test_register_tools() -> None:
    """Test tool registration."""
    mock_mcp = Mock()
    svc = register_youtube_video_upload_tools(mock_mcp)
    assert isinstance(svc, YouTubeVideoUploadService)
    assert mock_mcp.tool.call_count == 3  # type: ignore
