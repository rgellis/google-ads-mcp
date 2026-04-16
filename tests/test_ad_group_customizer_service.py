"""Tests for Ad Group Customizer Service."""

import pytest
from typing import Any
from unittest.mock import AsyncMock, Mock

from google.ads.googleads.v23.services.services.ad_group_customizer_service import (
    AdGroupCustomizerServiceClient,
)
from google.ads.googleads.v23.services.types.ad_group_customizer_service import (
    AdGroupCustomizerOperation,
    MutateAdGroupCustomizersRequest,
    MutateAdGroupCustomizersResponse,
    MutateAdGroupCustomizerResult,
)
from google.ads.googleads.v23.enums.types.response_content_type import (
    ResponseContentTypeEnum,
)
from google.ads.googleads.v23.enums.types.customizer_attribute_type import (
    CustomizerAttributeTypeEnum,
)

from src.services.ad_group.ad_group_customizer_service import (
    AdGroupCustomizerService,
    create_ad_group_customizer_tools,
    register_ad_group_customizer_tools,
)


class TestAdGroupCustomizerService:
    """Test cases for AdGroupCustomizerService."""

    @pytest.fixture
    def mock_client(self) -> Any:
        """Create a mock AdGroupCustomizerServiceClient."""
        return Mock(spec=AdGroupCustomizerServiceClient)

    @pytest.fixture
    def service(self, mock_client: Any) -> AdGroupCustomizerService:
        """Create an AdGroupCustomizerService instance with mock client."""
        service = AdGroupCustomizerService()
        service._client = mock_client  # type: ignore[reportPrivateUsage]
        return service

    @pytest.fixture
    def mock_ctx(self) -> AsyncMock:
        """Create a mock FastMCP context."""
        ctx = AsyncMock()
        ctx.log = AsyncMock()
        return ctx

    @pytest.mark.asyncio
    async def test_mutate_ad_group_customizers_success(
        self, service: AdGroupCustomizerService, mock_client: Any, mock_ctx: AsyncMock
    ) -> None:
        """Test successful ad group customizers mutation."""
        customer_id = "1234567890"

        operation = AdGroupCustomizerOperation()
        operation.create.ad_group = "customers/1234567890/adGroups/123"
        operation.create.customizer_attribute = (
            "customers/1234567890/customizerAttributes/456"
        )
        operation.create.value.type_ = (
            CustomizerAttributeTypeEnum.CustomizerAttributeType.TEXT
        )
        operation.create.value.string_value = "Test Value"
        operations = [operation]

        expected_response = MutateAdGroupCustomizersResponse(
            results=[
                MutateAdGroupCustomizerResult(
                    resource_name="customers/1234567890/adGroupCustomizers/123~456"
                )
            ]
        )
        mock_client.mutate_ad_group_customizers.return_value = expected_response  # type: ignore

        response = await service.mutate_ad_group_customizers(
            ctx=mock_ctx,
            customer_id=customer_id,
            operations=operations,
        )

        assert isinstance(response, dict)
        mock_client.mutate_ad_group_customizers.assert_called_once()  # type: ignore
        mock_ctx.log.assert_called()

        call_args = mock_client.mutate_ad_group_customizers.call_args[1]  # type: ignore
        request = call_args["request"]
        assert isinstance(request, MutateAdGroupCustomizersRequest)
        assert request.customer_id == customer_id
        assert len(request.operations) == 1

    @pytest.mark.asyncio
    async def test_mutate_ad_group_customizers_with_options(
        self, service: AdGroupCustomizerService, mock_client: Any, mock_ctx: AsyncMock
    ) -> None:
        """Test ad group customizers mutation with all options."""
        customer_id = "1234567890"

        operation = AdGroupCustomizerOperation()
        operation.create.ad_group = "customers/1234567890/adGroups/123"
        operation.create.customizer_attribute = (
            "customers/1234567890/customizerAttributes/456"
        )
        operations = [operation]

        expected_response = MutateAdGroupCustomizersResponse()
        mock_client.mutate_ad_group_customizers.return_value = expected_response  # type: ignore

        response = await service.mutate_ad_group_customizers(
            ctx=mock_ctx,
            customer_id=customer_id,
            operations=operations,
            partial_failure=True,
            validate_only=True,
            response_content_type=ResponseContentTypeEnum.ResponseContentType.MUTABLE_RESOURCE,
        )

        assert isinstance(response, dict)
        call_args = mock_client.mutate_ad_group_customizers.call_args[1]  # type: ignore
        request = call_args["request"]
        assert request.partial_failure is True
        assert request.validate_only is True
        assert (
            request.response_content_type
            == ResponseContentTypeEnum.ResponseContentType.MUTABLE_RESOURCE
        )

    @pytest.mark.asyncio
    async def test_mutate_ad_group_customizers_failure(
        self, service: AdGroupCustomizerService, mock_client: Any, mock_ctx: AsyncMock
    ) -> None:
        """Test ad group customizers mutation failure."""
        customer_id = "1234567890"

        operation = AdGroupCustomizerOperation()
        operation.create.ad_group = "customers/1234567890/adGroups/123"
        operations = [operation]

        mock_client.mutate_ad_group_customizers.side_effect = Exception("API Error")  # type: ignore

        with pytest.raises(Exception, match="Failed to mutate ad group customizers"):
            await service.mutate_ad_group_customizers(
                ctx=mock_ctx,
                customer_id=customer_id,
                operations=operations,
            )

    def test_create_ad_group_customizer_operation(
        self, service: AdGroupCustomizerService
    ) -> None:
        """Test creating ad group customizer operation."""
        ad_group = "customers/1234567890/adGroups/123"
        customizer_attribute = "customers/1234567890/customizerAttributes/456"
        value_type = CustomizerAttributeTypeEnum.CustomizerAttributeType.TEXT
        string_value = "Test Value"

        operation = service.create_ad_group_customizer_operation(
            ad_group=ad_group,
            customizer_attribute=customizer_attribute,
            value_type=value_type,
            string_value=string_value,
        )

        assert isinstance(operation, AdGroupCustomizerOperation)
        assert operation.create.ad_group == ad_group
        assert operation.create.customizer_attribute == customizer_attribute
        assert operation.create.value.type_ == value_type
        assert operation.create.value.string_value == string_value

    def test_create_remove_operation(self, service: AdGroupCustomizerService) -> None:
        """Test creating remove operation."""
        resource_name = "customers/1234567890/adGroupCustomizers/123~456"

        operation = service.create_remove_operation(resource_name=resource_name)

        assert isinstance(operation, AdGroupCustomizerOperation)
        assert operation.remove == resource_name
        assert not operation.create

    @pytest.mark.asyncio
    async def test_create_ad_group_customizer(
        self, service: AdGroupCustomizerService, mock_client: Any, mock_ctx: AsyncMock
    ) -> None:
        """Test creating a single ad group customizer."""
        customer_id = "1234567890"
        ad_group = "customers/1234567890/adGroups/123"
        customizer_attribute = "customers/1234567890/customizerAttributes/456"
        value_type = CustomizerAttributeTypeEnum.CustomizerAttributeType.TEXT
        string_value = "Test Value"

        expected_response = MutateAdGroupCustomizersResponse(
            results=[
                MutateAdGroupCustomizerResult(
                    resource_name="customers/1234567890/adGroupCustomizers/123~456"
                )
            ]
        )
        mock_client.mutate_ad_group_customizers.return_value = expected_response  # type: ignore

        response = await service.create_ad_group_customizer(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group=ad_group,
            customizer_attribute=customizer_attribute,
            value_type=value_type,
            string_value=string_value,
        )

        assert isinstance(response, dict)
        mock_client.mutate_ad_group_customizers.assert_called_once()  # type: ignore

    @pytest.mark.asyncio
    async def test_remove_ad_group_customizer(
        self, service: AdGroupCustomizerService, mock_client: Any, mock_ctx: AsyncMock
    ) -> None:
        """Test removing an ad group customizer."""
        customer_id = "1234567890"
        resource_name = "customers/1234567890/adGroupCustomizers/123~456"

        expected_response = MutateAdGroupCustomizersResponse(
            results=[MutateAdGroupCustomizerResult(resource_name=resource_name)]
        )
        mock_client.mutate_ad_group_customizers.return_value = expected_response  # type: ignore

        response = await service.remove_ad_group_customizer(
            ctx=mock_ctx,
            customer_id=customer_id,
            resource_name=resource_name,
        )

        assert isinstance(response, dict)
        mock_client.mutate_ad_group_customizers.assert_called_once()  # type: ignore

    @pytest.mark.asyncio
    async def test_create_text_customizer(
        self, service: AdGroupCustomizerService, mock_client: Any, mock_ctx: AsyncMock
    ) -> None:
        """Test creating a text customizer."""
        customer_id = "1234567890"
        ad_group = "customers/1234567890/adGroups/123"
        customizer_attribute = "customers/1234567890/customizerAttributes/456"
        text_value = "Test Text"

        expected_response = MutateAdGroupCustomizersResponse(
            results=[
                MutateAdGroupCustomizerResult(
                    resource_name="customers/1234567890/adGroupCustomizers/123~456"
                )
            ]
        )
        mock_client.mutate_ad_group_customizers.return_value = expected_response  # type: ignore

        response = await service.create_text_customizer(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group=ad_group,
            customizer_attribute=customizer_attribute,
            text_value=text_value,
        )

        assert isinstance(response, dict)
        mock_client.mutate_ad_group_customizers.assert_called_once()  # type: ignore

    @pytest.mark.asyncio
    async def test_create_number_customizer(
        self, service: AdGroupCustomizerService, mock_client: Any, mock_ctx: AsyncMock
    ) -> None:
        """Test creating a number customizer."""
        expected_response = MutateAdGroupCustomizersResponse(
            results=[
                MutateAdGroupCustomizerResult(
                    resource_name="customers/1234567890/adGroupCustomizers/123~456"
                )
            ]
        )
        mock_client.mutate_ad_group_customizers.return_value = expected_response  # type: ignore

        response = await service.create_number_customizer(
            ctx=mock_ctx,
            customer_id="1234567890",
            ad_group="customers/1234567890/adGroups/123",
            customizer_attribute="customers/1234567890/customizerAttributes/456",
            number_value="42",
        )

        assert isinstance(response, dict)
        mock_client.mutate_ad_group_customizers.assert_called_once()  # type: ignore

    @pytest.mark.asyncio
    async def test_create_price_customizer(
        self, service: AdGroupCustomizerService, mock_client: Any, mock_ctx: AsyncMock
    ) -> None:
        """Test creating a price customizer."""
        expected_response = MutateAdGroupCustomizersResponse(
            results=[
                MutateAdGroupCustomizerResult(
                    resource_name="customers/1234567890/adGroupCustomizers/123~456"
                )
            ]
        )
        mock_client.mutate_ad_group_customizers.return_value = expected_response  # type: ignore

        response = await service.create_price_customizer(
            ctx=mock_ctx,
            customer_id="1234567890",
            ad_group="customers/1234567890/adGroups/123",
            customizer_attribute="customers/1234567890/customizerAttributes/456",
            price_value="19.99",
        )

        assert isinstance(response, dict)
        mock_client.mutate_ad_group_customizers.assert_called_once()  # type: ignore

    @pytest.mark.asyncio
    async def test_create_percent_customizer(
        self, service: AdGroupCustomizerService, mock_client: Any, mock_ctx: AsyncMock
    ) -> None:
        """Test creating a percent customizer."""
        expected_response = MutateAdGroupCustomizersResponse(
            results=[
                MutateAdGroupCustomizerResult(
                    resource_name="customers/1234567890/adGroupCustomizers/123~456"
                )
            ]
        )
        mock_client.mutate_ad_group_customizers.return_value = expected_response  # type: ignore

        response = await service.create_percent_customizer(
            ctx=mock_ctx,
            customer_id="1234567890",
            ad_group="customers/1234567890/adGroups/123",
            customizer_attribute="customers/1234567890/customizerAttributes/456",
            percent_value="25",
        )

        assert isinstance(response, dict)
        mock_client.mutate_ad_group_customizers.assert_called_once()  # type: ignore

    def test_register_tools(self) -> None:
        """Test registering tools."""
        mock_mcp = Mock()
        service = register_ad_group_customizer_tools(mock_mcp)
        assert isinstance(service, AdGroupCustomizerService)
        assert mock_mcp.tool.call_count > 0
