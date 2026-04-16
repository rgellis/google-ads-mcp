"""Tests for CustomerCustomizerService."""

from typing import Any
from unittest.mock import Mock, patch
import pytest
from src.services.account.customer_customizer_service import (
    CustomerCustomizerService,
    register_customer_customizer_tools,
)
from google.ads.googleads.v23.enums.types.customizer_attribute_type import (
    CustomizerAttributeTypeEnum,
)
from google.ads.googleads.v23.services.types.customer_customizer_service import (
    CustomerCustomizerOperation,
)


@pytest.fixture
def service() -> CustomerCustomizerService:
    mock_client = Mock()
    svc = CustomerCustomizerService()
    svc._client = mock_client  # type: ignore
    return svc


def test_mutate_customer_customizers(service: CustomerCustomizerService) -> None:
    mock_client = service.client
    mock_response = Mock()
    mock_client.mutate_customer_customizers.return_value = mock_response
    result = service.mutate_customer_customizers(
        customer_id="1234567890",
        operations=[CustomerCustomizerOperation()],
    )
    assert result == mock_response
    mock_client.mutate_customer_customizers.assert_called_once()


def test_create_customer_customizer(service: CustomerCustomizerService) -> None:
    mock_client = service.client
    mock_response = Mock()
    mock_response.results = [Mock(resource_name="test")]
    mock_client.mutate_customer_customizers.return_value = mock_response
    result = service.create_customer_customizer(
        customer_id="1234567890",
        customizer_attribute="customers/1234567890/customizerAttributes/1",
        value_type=CustomizerAttributeTypeEnum.CustomizerAttributeType.TEXT,
        string_value="test_value",
    )
    assert result == mock_response


def test_remove_customer_customizer(service: CustomerCustomizerService) -> None:
    mock_client = service.client
    mock_response = Mock()
    mock_response.results = []
    mock_client.mutate_customer_customizers.return_value = mock_response
    result = service.remove_customer_customizer(
        customer_id="1234567890",
        resource_name="customers/1234567890/customerCustomizers/1",
    )
    assert result == mock_response


def test_register_tools() -> None:
    mock_mcp = Mock()
    register_customer_customizer_tools(mock_mcp)
    assert mock_mcp.tool.call_count > 0
