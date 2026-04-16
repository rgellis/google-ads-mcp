"""Tests for Asset Group Signal Service."""

import pytest
from typing import Any
from unittest.mock import AsyncMock, Mock

from google.ads.googleads.v23.services.services.asset_group_signal_service import (
    AssetGroupSignalServiceClient,
)
from google.ads.googleads.v23.services.types.asset_group_signal_service import (
    AssetGroupSignalOperation,
    MutateAssetGroupSignalsRequest,
    MutateAssetGroupSignalsResponse,
    MutateAssetGroupSignalResult,
)
from google.ads.googleads.v23.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)
from google.ads.googleads.v23.common.types.criteria import AudienceInfo, SearchThemeInfo

from src.services.assets.asset_group_signal_service import (
    AssetGroupSignalService,
    create_asset_group_signal_tools,
    register_asset_group_signal_tools,
)


class TestAssetGroupSignalService:
    """Test cases for AssetGroupSignalService."""

    @pytest.fixture
    def mock_client(self) -> Any:
        """Create a mock AssetGroupSignalServiceClient."""
        return Mock(spec=AssetGroupSignalServiceClient)

    @pytest.fixture
    def service(self, mock_client: Any) -> AssetGroupSignalService:
        """Create an AssetGroupSignalService instance with mock client."""
        service = AssetGroupSignalService()
        service._client = mock_client  # type: ignore[reportPrivateUsage]
        return service

    @pytest.fixture
    def mock_ctx(self) -> AsyncMock:
        """Create a mock FastMCP context."""
        ctx = AsyncMock()
        ctx.log = AsyncMock()
        return ctx

    @pytest.mark.asyncio
    async def test_mutate_asset_group_signals_success(
        self, service: AssetGroupSignalService, mock_client: Any, mock_ctx: AsyncMock
    ) -> None:
        """Test successful asset group signals mutation."""
        customer_id = "1234567890"

        operation = AssetGroupSignalOperation()
        operation.create.asset_group = "customers/1234567890/assetGroups/123"
        operation.create.audience.audience = "customers/1234567890/audiences/456"
        operations = [operation]

        expected_response = MutateAssetGroupSignalsResponse(
            results=[
                MutateAssetGroupSignalResult(
                    resource_name="customers/1234567890/assetGroupSignals/123~456"
                )
            ]
        )
        mock_client.mutate_asset_group_signals.return_value = expected_response  # type: ignore

        response = await service.mutate_asset_group_signals(
            ctx=mock_ctx,
            customer_id=customer_id,
            operations=operations,
        )

        assert isinstance(response, dict)
        mock_client.mutate_asset_group_signals.assert_called_once()  # type: ignore
        mock_ctx.log.assert_called()

        call_args = mock_client.mutate_asset_group_signals.call_args[1]  # type: ignore
        request = call_args["request"]
        assert isinstance(request, MutateAssetGroupSignalsRequest)
        assert request.customer_id == customer_id
        assert len(request.operations) == 1

    @pytest.mark.asyncio
    async def test_mutate_asset_group_signals_with_options(
        self, service: AssetGroupSignalService, mock_client: Any, mock_ctx: AsyncMock
    ) -> None:
        """Test asset group signals mutation with all options."""
        customer_id = "1234567890"

        operation = AssetGroupSignalOperation()
        operation.create.asset_group = "customers/1234567890/assetGroups/123"
        operation.create.audience.audience = "customers/1234567890/audiences/456"
        operations = [operation]

        expected_response = MutateAssetGroupSignalsResponse()
        mock_client.mutate_asset_group_signals.return_value = expected_response  # type: ignore

        response = await service.mutate_asset_group_signals(
            ctx=mock_ctx,
            customer_id=customer_id,
            operations=operations,
            partial_failure=True,
            validate_only=True,
            response_content_type=ResponseContentTypeEnum.ResponseContentType.MUTABLE_RESOURCE,
        )

        assert isinstance(response, dict)
        call_args = mock_client.mutate_asset_group_signals.call_args[1]  # type: ignore
        request = call_args["request"]
        assert request.partial_failure is True
        assert request.validate_only is True
        assert (
            request.response_content_type
            == ResponseContentTypeEnum.ResponseContentType.MUTABLE_RESOURCE
        )

    @pytest.mark.asyncio
    async def test_mutate_asset_group_signals_failure(
        self, service: AssetGroupSignalService, mock_client: Any, mock_ctx: AsyncMock
    ) -> None:
        """Test asset group signals mutation failure."""
        customer_id = "1234567890"

        operation = AssetGroupSignalOperation()
        operation.create.asset_group = "customers/1234567890/assetGroups/123"
        operations = [operation]

        mock_client.mutate_asset_group_signals.side_effect = Exception("API Error")  # type: ignore

        with pytest.raises(Exception, match="Failed to mutate asset group signals"):
            await service.mutate_asset_group_signals(
                ctx=mock_ctx,
                customer_id=customer_id,
                operations=operations,
            )

    def test_create_asset_group_signal_operation_with_audience(
        self, service: AssetGroupSignalService
    ) -> None:
        """Test creating asset group signal operation with audience."""
        asset_group = "customers/1234567890/assetGroups/123"
        audience_info = AudienceInfo(audience="customers/1234567890/audiences/456")

        operation = service.create_asset_group_signal_operation(
            asset_group=asset_group,
            audience_info=audience_info,
        )

        assert isinstance(operation, AssetGroupSignalOperation)
        assert operation.create.asset_group == asset_group
        assert operation.create.audience == audience_info
        assert not operation.create.search_theme

    def test_create_asset_group_signal_operation_with_search_theme(
        self, service: AssetGroupSignalService
    ) -> None:
        """Test creating asset group signal operation with search theme."""
        asset_group = "customers/1234567890/assetGroups/123"
        search_theme_info = SearchThemeInfo(text="running shoes")

        operation = service.create_asset_group_signal_operation(
            asset_group=asset_group,
            search_theme_info=search_theme_info,
        )

        assert isinstance(operation, AssetGroupSignalOperation)
        assert operation.create.asset_group == asset_group
        assert operation.create.search_theme == search_theme_info
        assert not operation.create.audience

    def test_create_asset_group_signal_operation_invalid_signals(
        self, service: AssetGroupSignalService
    ) -> None:
        """Test creating asset group signal operation with invalid signal combination."""
        asset_group = "customers/1234567890/assetGroups/123"
        audience_info = AudienceInfo(audience="customers/1234567890/audiences/456")
        search_theme_info = SearchThemeInfo(text="running shoes")

        # Both signals provided
        with pytest.raises(
            ValueError,
            match="Exactly one of audience_info or search_theme_info must be provided",
        ):
            service.create_asset_group_signal_operation(
                asset_group=asset_group,
                audience_info=audience_info,
                search_theme_info=search_theme_info,
            )

        # No signals provided
        with pytest.raises(
            ValueError,
            match="Exactly one of audience_info or search_theme_info must be provided",
        ):
            service.create_asset_group_signal_operation(
                asset_group=asset_group,
            )

    def test_create_remove_operation(self, service: AssetGroupSignalService) -> None:
        """Test creating remove operation."""
        resource_name = "customers/1234567890/assetGroupSignals/123~456"

        operation = service.create_remove_operation(resource_name=resource_name)

        assert isinstance(operation, AssetGroupSignalOperation)
        assert operation.remove == resource_name
        assert not operation.create

    def test_create_audience_signal(self, service: AssetGroupSignalService) -> None:
        """Test creating audience signal operation."""
        asset_group = "customers/1234567890/assetGroups/123"
        audience_resource_name = "customers/1234567890/audiences/456"

        operation = service.create_audience_signal(
            asset_group=asset_group,
            audience_resource_name=audience_resource_name,
        )

        assert isinstance(operation, AssetGroupSignalOperation)
        assert operation.create.asset_group == asset_group
        assert operation.create.audience.audience == audience_resource_name
        assert not operation.create.search_theme

    def test_create_search_theme_signal(self, service: AssetGroupSignalService) -> None:
        """Test creating search theme signal operation."""
        asset_group = "customers/1234567890/assetGroups/123"
        search_theme = "running shoes"

        operation = service.create_search_theme_signal(
            asset_group=asset_group,
            search_theme=search_theme,
        )

        assert isinstance(operation, AssetGroupSignalOperation)
        assert operation.create.asset_group == asset_group
        assert operation.create.search_theme.text == search_theme
        assert not operation.create.audience

    def test_register_tools(self) -> None:
        """Test registering tools."""
        mock_mcp = Mock()
        service = register_asset_group_signal_tools(mock_mcp)
        assert isinstance(service, AssetGroupSignalService)
        assert mock_mcp.tool.call_count > 0
