"""Tests for BenchmarksService."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from fastmcp import Context

from src.services.planning.benchmarks_service import (
    BenchmarksService,
    register_benchmarks_tools,
)


@pytest.fixture
def service(mock_sdk_client: Any) -> BenchmarksService:
    """Create a BenchmarksService instance with mocked dependencies."""
    mock_client = Mock()
    mock_sdk_client.client.get_service.return_value = mock_client  # type: ignore

    with patch(
        "src.services.planning.benchmarks_service.get_sdk_client",
        return_value=mock_sdk_client,
    ):
        svc = BenchmarksService()
        _ = svc.client
        return svc


@pytest.mark.asyncio
async def test_list_benchmarks_locations(
    service: BenchmarksService,
    mock_ctx: Context,
) -> None:
    """Test listing benchmarks locations."""
    mock_client = service.client
    mock_client.list_benchmarks_locations.return_value = Mock()  # type: ignore

    expected_result = {"locations": []}

    with patch(
        "src.services.planning.benchmarks_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.list_benchmarks_locations(ctx=mock_ctx)

    assert result == expected_result
    mock_client.list_benchmarks_locations.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_list_benchmarks_locations_error(
    service: BenchmarksService,
    mock_ctx: Context,
) -> None:
    """Test error handling when listing locations fails."""
    mock_client = service.client
    mock_client.list_benchmarks_locations.side_effect = Exception("API error")  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.list_benchmarks_locations(ctx=mock_ctx)

    assert "Failed to list benchmarks locations" in str(exc_info.value)


@pytest.mark.asyncio
async def test_list_benchmarks_products(
    service: BenchmarksService,
    mock_ctx: Context,
) -> None:
    """Test listing benchmarks products."""
    mock_client = service.client
    mock_client.list_benchmarks_products.return_value = Mock()  # type: ignore

    expected_result = {"products": []}

    with patch(
        "src.services.planning.benchmarks_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.list_benchmarks_products(ctx=mock_ctx)

    assert result == expected_result
    mock_client.list_benchmarks_products.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_list_benchmarks_products_error(
    service: BenchmarksService,
    mock_ctx: Context,
) -> None:
    """Test error handling when listing products fails."""
    mock_client = service.client
    mock_client.list_benchmarks_products.side_effect = Exception("API error")  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.list_benchmarks_products(ctx=mock_ctx)

    assert "Failed to list benchmarks products" in str(exc_info.value)


@pytest.mark.asyncio
async def test_list_benchmarks_sources(
    service: BenchmarksService,
    mock_ctx: Context,
) -> None:
    """Test listing benchmarks sources."""
    mock_client = service.client
    mock_client.list_benchmarks_sources.return_value = Mock()  # type: ignore

    expected_result = {"sources": []}

    with patch(
        "src.services.planning.benchmarks_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.list_benchmarks_sources(ctx=mock_ctx)

    assert result == expected_result
    mock_client.list_benchmarks_sources.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_list_benchmarks_sources_error(
    service: BenchmarksService,
    mock_ctx: Context,
) -> None:
    """Test error handling when listing sources fails."""
    mock_client = service.client
    mock_client.list_benchmarks_sources.side_effect = Exception("API error")  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.list_benchmarks_sources(ctx=mock_ctx)

    assert "Failed to list benchmarks sources" in str(exc_info.value)


@pytest.mark.asyncio
async def test_list_benchmarks_available_dates(
    service: BenchmarksService,
    mock_ctx: Context,
) -> None:
    """Test listing benchmarks available dates."""
    mock_client = service.client
    mock_client.list_benchmarks_available_dates.return_value = Mock()  # type: ignore

    expected_result = {"available_dates": []}

    with patch(
        "src.services.planning.benchmarks_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.list_benchmarks_available_dates(ctx=mock_ctx)

    assert result == expected_result
    mock_client.list_benchmarks_available_dates.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_list_benchmarks_available_dates_error(
    service: BenchmarksService,
    mock_ctx: Context,
) -> None:
    """Test error handling when listing available dates fails."""
    mock_client = service.client
    mock_client.list_benchmarks_available_dates.side_effect = Exception("API error")  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.list_benchmarks_available_dates(ctx=mock_ctx)

    assert "Failed to list benchmarks available dates" in str(exc_info.value)


@pytest.mark.asyncio
async def test_generate_benchmarks_metrics(
    service: BenchmarksService,
    mock_ctx: Context,
) -> None:
    """Test generating benchmarks metrics."""
    mock_client = service.client
    mock_client.generate_benchmarks_metrics.return_value = Mock()  # type: ignore

    expected_result = {"metrics": {}}

    with patch(
        "src.services.planning.benchmarks_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.generate_benchmarks_metrics(
            ctx=mock_ctx,
            customer_id="1234567890",
            industry_vertical_id=12345,
            location_resource_name="geoTargetConstants/2840",
            start_date="2024-01-01",
            end_date="2024-03-31",
        )

    assert result == expected_result
    mock_client.generate_benchmarks_metrics.assert_called_once()  # type: ignore
    call_args = mock_client.generate_benchmarks_metrics.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_id == "1234567890"


@pytest.mark.asyncio
async def test_generate_benchmarks_metrics_with_currency(
    service: BenchmarksService,
    mock_ctx: Context,
) -> None:
    """Test generating benchmarks metrics with currency code."""
    mock_client = service.client
    mock_client.generate_benchmarks_metrics.return_value = Mock()  # type: ignore

    expected_result = {"metrics": {}}

    with patch(
        "src.services.planning.benchmarks_service.serialize_proto_message",
        return_value=expected_result,
    ):
        result = await service.generate_benchmarks_metrics(
            ctx=mock_ctx,
            customer_id="1234567890",
            industry_vertical_id=12345,
            location_resource_name="geoTargetConstants/2840",
            start_date="2024-01-01",
            end_date="2024-03-31",
            currency_code="USD",
        )

    assert result == expected_result
    call_args = mock_client.generate_benchmarks_metrics.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.currency_code == "USD"


@pytest.mark.asyncio
async def test_generate_benchmarks_metrics_error(
    service: BenchmarksService,
    mock_ctx: Context,
    google_ads_exception: Any,
) -> None:
    """Test error handling when generating benchmarks metrics fails."""
    mock_client = service.client
    mock_client.generate_benchmarks_metrics.side_effect = google_ads_exception  # type: ignore

    with pytest.raises(Exception) as exc_info:
        await service.generate_benchmarks_metrics(
            ctx=mock_ctx,
            customer_id="1234567890",
            industry_vertical_id=12345,
            location_resource_name="geoTargetConstants/2840",
            start_date="2024-01-01",
            end_date="2024-03-31",
        )

    assert "Test Google Ads Exception" in str(exc_info.value)


@pytest.mark.asyncio
async def test_generate_benchmarks_with_optional_fields(
    service: BenchmarksService,
    mock_ctx: Context,
) -> None:
    """Test generate_benchmarks_metrics with product_filter, breakdown, and group."""
    mock_client = service.client
    mock_client.generate_benchmarks_metrics.return_value = Mock()  # type: ignore

    with patch(
        "src.services.planning.benchmarks_service.serialize_proto_message",
        return_value={"metrics": {}},
    ):
        result = await service.generate_benchmarks_metrics(
            ctx=mock_ctx,
            customer_id="1234567890",
            industry_vertical_id=12345,
            location_resource_name="geoTargetConstants/2840",
            start_date="2024-01-01",
            end_date="2024-03-31",
            product_codes=["VIDEO_TRUEVIEW"],
            date_breakdown="MONTH",
            customer_benchmarks_group="my_group",
        )

    call_args = mock_client.generate_benchmarks_metrics.call_args  # type: ignore
    request = call_args[1]["request"]
    assert request.customer_benchmarks_group == "my_group"
    assert request.breakdown_definition is not None
    assert request.product_filter is not None


@pytest.mark.asyncio
async def test_list_benchmarks_sources_with_filter(
    service: BenchmarksService,
    mock_ctx: Context,
) -> None:
    """Test list_benchmarks_sources with source type filter."""
    mock_client = service.client
    mock_client.list_benchmarks_sources.return_value = Mock()  # type: ignore

    with patch(
        "src.services.planning.benchmarks_service.serialize_proto_message",
        return_value={"sources": []},
    ):
        result = await service.list_benchmarks_sources(
            ctx=mock_ctx,
            benchmarks_source_types=["INDUSTRY_VERTICAL"],
        )

    call_args = mock_client.list_benchmarks_sources.call_args  # type: ignore
    request = call_args[1]["request"]
    assert len(request.benchmarks_sources) == 1


def test_register_tools() -> None:
    """Test tool registration."""
    mock_mcp = Mock()
    svc = register_benchmarks_tools(mock_mcp)
    assert isinstance(svc, BenchmarksService)
    assert mock_mcp.tool.call_count == 5  # type: ignore
