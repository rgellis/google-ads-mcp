"""Tests for CustomerCustomizerService."""

from typing import Any
from unittest.mock import AsyncMock, Mock
import pytest
from src.services.account.customer_customizer_service import (
    CustomerCustomizerService,
    create_customer_customizer_tools,
    register_customer_customizer_tools,
)
from google.ads.googleads.v23.enums.types.customizer_attribute_type import (
    CustomizerAttributeTypeEnum,
)
from google.ads.googleads.v23.services.types.customer_customizer_service import (
    CustomerCustomizerOperation,
    MutateCustomerCustomizersResponse,
    MutateCustomerCustomizerResult,
)


class TestCustomerCustomizerService:
    """Test cases for CustomerCustomizerService."""

    @pytest.fixture
    def mock_client(self) -> Any:
        """Create a mock client."""
        return Mock()

    @pytest.fixture
    def service(self, mock_client: Any) -> CustomerCustomizerService:
        """Create service with mock client."""
        svc = CustomerCustomizerService()
        svc._client = mock_client  # type: ignore
        return svc

    @pytest.fixture
    def mock_ctx(self) -> AsyncMock:
        """Create a mock FastMCP context."""
        ctx = AsyncMock()
        ctx.log = AsyncMock()
        return ctx

    @pytest.mark.asyncio
    async def test_mutate_customer_customizers(
        self, service: CustomerCustomizerService, mock_client: Any, mock_ctx: AsyncMock
    ) -> None:
        """Test successful customer customizers mutation."""
        mock_response = MutateCustomerCustomizersResponse(
            results=[MutateCustomerCustomizerResult(resource_name="test/resource")]
        )
        mock_client.mutate_customer_customizers.return_value = mock_response
        result = await service.mutate_customer_customizers(
            ctx=mock_ctx,
            customer_id="1234567890",
            operations=[CustomerCustomizerOperation()],
        )
        assert isinstance(result, dict)
        mock_client.mutate_customer_customizers.assert_called_once()
        mock_ctx.log.assert_called()

    @pytest.mark.asyncio
    async def test_create_customer_customizer(
        self, service: CustomerCustomizerService, mock_client: Any, mock_ctx: AsyncMock
    ) -> None:
        """Test creating a customer customizer."""
        mock_response = MutateCustomerCustomizersResponse(
            results=[MutateCustomerCustomizerResult(resource_name="test/resource")]
        )
        mock_client.mutate_customer_customizers.return_value = mock_response
        result = await service.create_customer_customizer(
            ctx=mock_ctx,
            customer_id="1234567890",
            customizer_attribute="customers/1234567890/customizerAttributes/1",
            value_type=CustomizerAttributeTypeEnum.CustomizerAttributeType.TEXT,
            string_value="test_value",
        )
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_remove_customer_customizer(
        self, service: CustomerCustomizerService, mock_client: Any, mock_ctx: AsyncMock
    ) -> None:
        """Test removing a customer customizer."""
        mock_response = MutateCustomerCustomizersResponse(results=[])
        mock_client.mutate_customer_customizers.return_value = mock_response
        result = await service.remove_customer_customizer(
            ctx=mock_ctx,
            customer_id="1234567890",
            resource_name="customers/1234567890/customerCustomizers/1",
        )
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_mutate_customer_customizers_failure(
        self, service: CustomerCustomizerService, mock_client: Any, mock_ctx: AsyncMock
    ) -> None:
        """Test customer customizers mutation failure."""
        mock_client.mutate_customer_customizers.side_effect = Exception("API Error")

        with pytest.raises(Exception, match="Failed to mutate customer customizers"):
            await service.mutate_customer_customizers(
                ctx=mock_ctx,
                customer_id="1234567890",
                operations=[CustomerCustomizerOperation()],
            )

    def test_create_customer_customizer_operation(
        self, service: CustomerCustomizerService
    ) -> None:
        """Test creating customer customizer operation."""
        operation = service.create_customer_customizer_operation(
            customizer_attribute="customers/1234567890/customizerAttributes/1",
            value_type=CustomizerAttributeTypeEnum.CustomizerAttributeType.TEXT,
            string_value="test_value",
        )
        assert isinstance(operation, CustomerCustomizerOperation)
        assert (
            operation.create.customizer_attribute
            == "customers/1234567890/customizerAttributes/1"
        )

    def test_create_remove_operation(self, service: CustomerCustomizerService) -> None:
        """Test creating remove operation."""
        operation = service.create_remove_operation(
            resource_name="customers/1234567890/customerCustomizers/1"
        )
        assert isinstance(operation, CustomerCustomizerOperation)
        assert operation.remove == "customers/1234567890/customerCustomizers/1"

    def test_register_tools(self) -> None:
        """Test registering tools."""
        mock_mcp = Mock()
        service = register_customer_customizer_tools(mock_mcp)
        assert isinstance(service, CustomerCustomizerService)
        assert mock_mcp.tool.call_count > 0
