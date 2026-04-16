"""Tests for Google Ads Product Link Service"""

import pytest
from typing import Any
from unittest.mock import AsyncMock, Mock

from google.ads.googleads.v23.resources.types.product_link import (
    ProductLink,
)
from google.ads.googleads.v23.services.types.product_link_service import (
    CreateProductLinkResponse,
    RemoveProductLinkResponse,
)

from src.services.product_integration.product_link_service import (
    ProductLinkService,
    create_product_link_tools,
    register_product_link_tools,
)


class TestProductLinkService:
    """Test cases for ProductLinkService"""

    @pytest.fixture
    def mock_service_client(self) -> Any:
        """Create a mock ProductLinkService client (the inner gRPC stub)."""
        return Mock()

    @pytest.fixture
    def product_link_service(self, mock_service_client: Any) -> ProductLinkService:
        """Create ProductLinkService instance with mock client"""
        service = ProductLinkService()
        service._client = mock_service_client  # type: ignore
        return service

    @pytest.fixture
    def mock_ctx(self) -> AsyncMock:
        """Create a mock FastMCP context."""
        ctx = AsyncMock()
        ctx.log = AsyncMock()
        return ctx

    @pytest.mark.asyncio
    async def test_create_product_link(
        self,
        product_link_service: ProductLinkService,
        mock_service_client: Any,
        mock_ctx: AsyncMock,
    ) -> None:
        """Test creating a product link"""
        customer_id = "1234567890"
        product_link = ProductLink()

        mock_response = CreateProductLinkResponse(
            resource_name="customers/1234567890/productLinks/123"
        )
        mock_service_client.create_product_link.return_value = mock_response  # type: ignore

        response = await product_link_service.create_product_link(
            ctx=mock_ctx, customer_id=customer_id, product_link=product_link
        )

        assert isinstance(response, dict)
        mock_service_client.create_product_link.assert_called_once()  # type: ignore
        mock_ctx.log.assert_called()

        call_args = mock_service_client.create_product_link.call_args  # type: ignore
        request = call_args.kwargs["request"]
        assert request.customer_id == customer_id
        assert request.product_link == product_link

    @pytest.mark.asyncio
    async def test_remove_product_link(
        self,
        product_link_service: ProductLinkService,
        mock_service_client: Any,
        mock_ctx: AsyncMock,
    ) -> None:
        """Test removing a product link"""
        customer_id = "1234567890"
        resource_name = "customers/1234567890/productLinks/123"

        mock_response = RemoveProductLinkResponse(resource_name=resource_name)
        mock_service_client.remove_product_link.return_value = mock_response  # type: ignore

        response = await product_link_service.remove_product_link(
            ctx=mock_ctx, customer_id=customer_id, resource_name=resource_name
        )

        assert isinstance(response, dict)

        call_args = mock_service_client.remove_product_link.call_args  # type: ignore
        request = call_args.kwargs["request"]
        assert request.customer_id == customer_id
        assert request.resource_name == resource_name

    @pytest.mark.asyncio
    async def test_create_merchant_center_link(
        self,
        product_link_service: ProductLinkService,
        mock_service_client: Any,
        mock_ctx: AsyncMock,
    ) -> None:
        """Test creating a Merchant Center link"""
        customer_id = "1234567890"
        merchant_center_id = 123456789

        mock_response = CreateProductLinkResponse(
            resource_name="customers/1234567890/productLinks/123"
        )
        mock_service_client.create_product_link.return_value = mock_response  # type: ignore

        response = await product_link_service.create_merchant_center_link(
            ctx=mock_ctx, customer_id=customer_id, merchant_center_id=merchant_center_id
        )

        assert isinstance(response, dict)

        call_args = mock_service_client.create_product_link.call_args  # type: ignore
        request = call_args.kwargs["request"]
        assert request.customer_id == customer_id
        assert (
            request.product_link.merchant_center.merchant_center_id
            == merchant_center_id
        )

    @pytest.mark.asyncio
    async def test_create_google_ads_link(
        self,
        product_link_service: ProductLinkService,
        mock_service_client: Any,
        mock_ctx: AsyncMock,
    ) -> None:
        """Test creating a Google Ads link"""
        customer_id = "1234567890"
        linked_customer_id = 9876543210

        mock_response = CreateProductLinkResponse(
            resource_name="customers/1234567890/productLinks/123"
        )
        mock_service_client.create_product_link.return_value = mock_response  # type: ignore

        response = await product_link_service.create_google_ads_link(
            ctx=mock_ctx, customer_id=customer_id, linked_customer_id=linked_customer_id
        )

        assert isinstance(response, dict)

        call_args = mock_service_client.create_product_link.call_args  # type: ignore
        request = call_args.kwargs["request"]
        assert request.customer_id == customer_id
        assert (
            request.product_link.google_ads.customer
            == f"customers/{linked_customer_id}"
        )

    @pytest.mark.asyncio
    async def test_create_data_partner_link(
        self,
        product_link_service: ProductLinkService,
        mock_service_client: Any,
        mock_ctx: AsyncMock,
    ) -> None:
        """Test creating a data partner link"""
        customer_id = "1234567890"
        data_partner_id = 555666777

        mock_response = CreateProductLinkResponse(
            resource_name="customers/1234567890/productLinks/123"
        )
        mock_service_client.create_product_link.return_value = mock_response  # type: ignore

        response = await product_link_service.create_data_partner_link(
            ctx=mock_ctx, customer_id=customer_id, data_partner_id=data_partner_id
        )

        assert isinstance(response, dict)

        call_args = mock_service_client.create_product_link.call_args  # type: ignore
        request = call_args.kwargs["request"]
        assert request.customer_id == customer_id
        assert request.product_link.data_partner.data_partner_id == data_partner_id

    @pytest.mark.asyncio
    async def test_remove_product_link_validate_only(
        self,
        product_link_service: ProductLinkService,
        mock_service_client: Any,
        mock_ctx: AsyncMock,
    ) -> None:
        """Test validate_only reaches the RemoveProductLink request"""
        customer_id = "1234567890"
        resource_name = "customers/1234567890/productLinks/123"

        mock_response = RemoveProductLinkResponse(resource_name=resource_name)
        mock_service_client.remove_product_link.return_value = mock_response  # type: ignore

        await product_link_service.remove_product_link(
            ctx=mock_ctx,
            customer_id=customer_id,
            resource_name=resource_name,
            validate_only=True,
        )

        call_args = mock_service_client.remove_product_link.call_args  # type: ignore
        request = call_args.kwargs["request"]
        assert request.validate_only is True

    @pytest.mark.asyncio
    async def test_create_product_link_failure(
        self,
        product_link_service: ProductLinkService,
        mock_service_client: Any,
        mock_ctx: AsyncMock,
    ) -> None:
        """Test product link creation failure."""
        mock_service_client.create_product_link.side_effect = Exception("API Error")

        with pytest.raises(Exception, match="Failed to create product link"):
            await product_link_service.create_product_link(
                ctx=mock_ctx,
                customer_id="1234567890",
                product_link=ProductLink(),
            )

    def test_register_tools(self) -> None:
        """Test registering tools."""
        mock_mcp = Mock()
        service = register_product_link_tools(mock_mcp)
        assert isinstance(service, ProductLinkService)
        assert mock_mcp.tool.call_count > 0
