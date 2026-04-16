"""Tests for KeywordThemeConstantService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context

from src.services.planning.keyword_theme_constant_service import (
    KeywordThemeConstantService,
    register_keyword_theme_constant_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> KeywordThemeConstantService:
    """Create a KeywordThemeConstantService with mocked dependencies."""
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client
    with patch(
        "src.services.planning.keyword_theme_constant_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = KeywordThemeConstantService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_suggest_keyword_theme_constants(
    service: KeywordThemeConstantService, mock_ctx: Context
) -> None:
    """Test suggesting keyword theme constants."""
    mock_client = service.client
    mock_client.suggest_keyword_theme_constants.return_value = Mock()  # type: ignore

    expected_result = {
        "keyword_theme_constants": [
            {"resource_name": "keywordThemeConstants/1", "display_name": "Plumbing"}
        ]
    }

    with patch(
        "src.services.planning.keyword_theme_constant_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.suggest_keyword_theme_constants(
            ctx=mock_ctx,
            query_text="plumbing services",
            country_code="US",
            language_code="en",
        )

    assert result == expected_result
    mock_client.suggest_keyword_theme_constants.assert_called_once()  # type: ignore
    call_args = mock_client.suggest_keyword_theme_constants.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.query_text == "plumbing services"
    assert request.country_code == "US"
    assert request.language_code == "en"


@pytest.mark.asyncio
async def test_suggest_keyword_theme_constants_minimal(
    service: KeywordThemeConstantService, mock_ctx: Context
) -> None:
    """Test suggesting keyword theme constants with only required params."""
    mock_client = service.client
    mock_client.suggest_keyword_theme_constants.return_value = Mock()  # type: ignore

    expected_result = {"keyword_theme_constants": []}

    with patch(
        "src.services.planning.keyword_theme_constant_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.suggest_keyword_theme_constants(
            ctx=mock_ctx,
            query_text="restaurants",
        )

    assert result == expected_result
    mock_client.suggest_keyword_theme_constants.assert_called_once()  # type: ignore
    call_args = mock_client.suggest_keyword_theme_constants.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.query_text == "restaurants"


@pytest.mark.asyncio
async def test_suggest_keyword_theme_constants_error(
    service: KeywordThemeConstantService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling in suggest_keyword_theme_constants."""
    mock_client = service.client
    mock_client.suggest_keyword_theme_constants.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.suggest_keyword_theme_constants(
            ctx=mock_ctx,
            query_text="plumbing",
        )

    assert "Failed to suggest keyword themes" in str(exc_info.value)


def test_register_tools() -> None:
    """Test tool registration."""
    mock_mcp = Mock()
    svc = register_keyword_theme_constant_tools(mock_mcp)
    assert isinstance(svc, KeywordThemeConstantService)
    assert mock_mcp.tool.call_count == 1  # type: ignore
    registered_tools = [call[0][0] for call in mock_mcp.tool.call_args_list]  # type: ignore
    tool_names = [t.__name__ for t in registered_tools]
    assert tool_names == ["suggest_keyword_theme_constants"]
