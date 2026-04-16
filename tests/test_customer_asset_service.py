"""Tests for Customer Asset Service."""

import pytest
from typing import Any
from unittest.mock import AsyncMock, Mock

from google.ads.googleads.v23.services.services.customer_asset_service import (
    CustomerAssetServiceClient,
)
from google.ads.googleads.v23.services.types.customer_asset_service import (
    CustomerAssetOperation,
    MutateCustomerAssetsRequest,
    MutateCustomerAssetsResponse,
    MutateCustomerAssetResult,
)
from google.ads.googleads.v23.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)
from google.ads.googleads.v23.enums.types.asset_field_type import (
    AssetFieldTypeEnum,
)
from google.ads.googleads.v23.enums.types.asset_link_status import (
    AssetLinkStatusEnum,
)
from google.protobuf import field_mask_pb2

from src.services.assets.customer_asset_service import (
    CustomerAssetService,
    create_customer_asset_tools,
    register_customer_asset_tools,
)


class TestCustomerAssetService:
    """Test cases for CustomerAssetService."""

    @pytest.fixture
    def mock_client(self) -> Any:
        """Create a mock CustomerAssetServiceClient."""
        return Mock(spec=CustomerAssetServiceClient)

    @pytest.fixture
    def service(self, mock_client: Any) -> CustomerAssetService:
        """Create a CustomerAssetService instance with mock client."""
        service = CustomerAssetService()
        service._client = mock_client  # type: ignore
        return service

    @pytest.fixture
    def mock_ctx(self) -> AsyncMock:
        """Create a mock FastMCP context."""
        ctx = AsyncMock()
        ctx.log = AsyncMock()
        return ctx

    @pytest.mark.asyncio
    async def test_mutate_customer_assets_success(
        self, service: CustomerAssetService, mock_client: Any, mock_ctx: AsyncMock
    ) -> None:
        """Test successful customer assets mutation."""
        customer_id = "1234567890"
        operations = [CustomerAssetOperation()]
        expected_response = MutateCustomerAssetsResponse(
            results=[
                MutateCustomerAssetResult(
                    resource_name="customers/1234567890/customerAssets/123~LOGO"
                )
            ]
        )
        mock_client.mutate_customer_assets.return_value = expected_response  # type: ignore

        response = await service.mutate_customer_assets(
            ctx=mock_ctx,
            customer_id=customer_id,
            operations=operations,
        )

        assert isinstance(response, dict)
        mock_client.mutate_customer_assets.assert_called_once()  # type: ignore
        mock_ctx.log.assert_called()

        call_args = mock_client.mutate_customer_assets.call_args[1]  # type: ignore
        request = call_args["request"]
        assert isinstance(request, MutateCustomerAssetsRequest)
        assert request.customer_id == customer_id
        assert request.partial_failure is False
        assert request.validate_only is False

    @pytest.mark.asyncio
    async def test_mutate_customer_assets_with_options(
        self, service: CustomerAssetService, mock_client: Any, mock_ctx: AsyncMock
    ) -> None:
        """Test customer assets mutation with all options."""
        customer_id = "1234567890"
        operations = [CustomerAssetOperation()]
        expected_response = MutateCustomerAssetsResponse()
        mock_client.mutate_customer_assets.return_value = expected_response  # type: ignore

        response = await service.mutate_customer_assets(
            ctx=mock_ctx,
            customer_id=customer_id,
            operations=operations,
            partial_failure=True,
            validate_only=True,
            response_content_type=ResponseContentTypeEnum.ResponseContentType.MUTABLE_RESOURCE,
        )

        assert isinstance(response, dict)
        call_args = mock_client.mutate_customer_assets.call_args[1]  # type: ignore
        request = call_args["request"]
        assert request.partial_failure is True
        assert request.validate_only is True
        assert (
            request.response_content_type
            == ResponseContentTypeEnum.ResponseContentType.MUTABLE_RESOURCE
        )

    @pytest.mark.asyncio
    async def test_mutate_customer_assets_failure(
        self, service: CustomerAssetService, mock_client: Any, mock_ctx: AsyncMock
    ) -> None:
        """Test customer assets mutation failure."""
        customer_id = "1234567890"
        operations = [CustomerAssetOperation()]
        mock_client.mutate_customer_assets.side_effect = Exception("API Error")  # type: ignore

        with pytest.raises(Exception, match="Failed to mutate customer assets"):
            await service.mutate_customer_assets(
                ctx=mock_ctx,
                customer_id=customer_id,
                operations=operations,
            )

    def test_create_customer_asset_operation(
        self, service: CustomerAssetService
    ) -> None:
        """Test creating customer asset operation."""
        asset = "customers/1234567890/assets/123"
        field_type = AssetFieldTypeEnum.AssetFieldType.LOGO
        status = AssetLinkStatusEnum.AssetLinkStatus.ENABLED

        operation = service.create_customer_asset_operation(
            asset=asset,
            field_type=field_type,
            status=status,
        )

        assert isinstance(operation, CustomerAssetOperation)
        assert operation.create.asset == asset
        assert operation.create.field_type == field_type
        assert operation.create.status == status

    def test_create_update_operation(self, service: CustomerAssetService) -> None:
        """Test creating update operation."""
        resource_name = "customers/1234567890/customerAssets/123~LOGO"
        status = AssetLinkStatusEnum.AssetLinkStatus.PAUSED

        operation = service.create_update_operation(
            resource_name=resource_name,
            status=status,
        )

        assert isinstance(operation, CustomerAssetOperation)
        assert operation.update.resource_name == resource_name
        assert operation.update.status == status
        assert operation.update_mask.paths == ["status"]

    def test_create_update_operation_with_custom_mask(
        self, service: CustomerAssetService
    ) -> None:
        """Test creating update operation with custom field mask."""
        resource_name = "customers/1234567890/customerAssets/123~LOGO"
        status = AssetLinkStatusEnum.AssetLinkStatus.PAUSED
        update_mask = field_mask_pb2.FieldMask(paths=["status", "custom_field"])

        operation = service.create_update_operation(
            resource_name=resource_name,
            status=status,
            update_mask=update_mask,
        )

        assert isinstance(operation, CustomerAssetOperation)
        assert operation.update_mask == update_mask

    def test_create_remove_operation(self, service: CustomerAssetService) -> None:
        """Test creating remove operation."""
        resource_name = "customers/1234567890/customerAssets/123~LOGO"

        operation = service.create_remove_operation(resource_name=resource_name)

        assert isinstance(operation, CustomerAssetOperation)
        assert operation.remove == resource_name
        assert not operation.create
        assert not operation.update

    @pytest.mark.asyncio
    async def test_create_customer_asset(
        self, service: CustomerAssetService, mock_client: Any, mock_ctx: AsyncMock
    ) -> None:
        """Test creating a single customer asset."""
        customer_id = "1234567890"
        asset = "customers/1234567890/assets/123"
        field_type = AssetFieldTypeEnum.AssetFieldType.LOGO
        status = AssetLinkStatusEnum.AssetLinkStatus.ENABLED

        expected_response = MutateCustomerAssetsResponse(
            results=[
                MutateCustomerAssetResult(
                    resource_name="customers/1234567890/customerAssets/123~LOGO"
                )
            ]
        )
        mock_client.mutate_customer_assets.return_value = expected_response  # type: ignore

        response = await service.create_customer_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            asset=asset,
            field_type=field_type,
            status=status,
        )

        assert isinstance(response, dict)
        mock_client.mutate_customer_assets.assert_called_once()  # type: ignore

    @pytest.mark.asyncio
    async def test_update_customer_asset_status(
        self, service: CustomerAssetService, mock_client: Any, mock_ctx: AsyncMock
    ) -> None:
        """Test updating customer asset status."""
        customer_id = "1234567890"
        resource_name = "customers/1234567890/customerAssets/123~LOGO"
        status = AssetLinkStatusEnum.AssetLinkStatus.PAUSED

        expected_response = MutateCustomerAssetsResponse(
            results=[MutateCustomerAssetResult(resource_name=resource_name)]
        )
        mock_client.mutate_customer_assets.return_value = expected_response  # type: ignore

        response = await service.update_customer_asset_status(
            ctx=mock_ctx,
            customer_id=customer_id,
            resource_name=resource_name,
            status=status,
        )

        assert isinstance(response, dict)
        mock_client.mutate_customer_assets.assert_called_once()  # type: ignore

    @pytest.mark.asyncio
    async def test_remove_customer_asset(
        self, service: CustomerAssetService, mock_client: Any, mock_ctx: AsyncMock
    ) -> None:
        """Test removing customer asset."""
        customer_id = "1234567890"
        resource_name = "customers/1234567890/customerAssets/123~LOGO"

        expected_response = MutateCustomerAssetsResponse(
            results=[MutateCustomerAssetResult(resource_name=resource_name)]
        )
        mock_client.mutate_customer_assets.return_value = expected_response  # type: ignore

        response = await service.remove_customer_asset(
            ctx=mock_ctx,
            customer_id=customer_id,
            resource_name=resource_name,
        )

        assert isinstance(response, dict)
        mock_client.mutate_customer_assets.assert_called_once()  # type: ignore

    def test_register_tools(self) -> None:
        """Test registering tools."""
        mock_mcp = Mock()
        service = register_customer_asset_tools(mock_mcp)
        assert isinstance(service, CustomerAssetService)
        assert mock_mcp.tool.call_count > 0
