"""Tests for Ad Group Criterion Label Service."""

import pytest
from typing import Any
from unittest.mock import AsyncMock, Mock

from google.ads.googleads.v23.services.services.ad_group_criterion_label_service import (
    AdGroupCriterionLabelServiceClient,
)
from google.ads.googleads.v23.services.types.ad_group_criterion_label_service import (
    AdGroupCriterionLabelOperation,
    MutateAdGroupCriterionLabelsRequest,
    MutateAdGroupCriterionLabelsResponse,
    MutateAdGroupCriterionLabelResult,
)

from src.services.ad_group.ad_group_criterion_label_service import (
    AdGroupCriterionLabelService,
    create_ad_group_criterion_label_tools,
    register_ad_group_criterion_label_tools,
)


class TestAdGroupCriterionLabelService:
    """Test cases for AdGroupCriterionLabelService."""

    @pytest.fixture
    def mock_client(self) -> Any:
        """Create a mock AdGroupCriterionLabelServiceClient."""
        return Mock(spec=AdGroupCriterionLabelServiceClient)

    @pytest.fixture
    def service(self, mock_client: Any) -> AdGroupCriterionLabelService:
        """Create an AdGroupCriterionLabelService instance with mock client."""
        service = AdGroupCriterionLabelService()
        service._client = mock_client  # type: ignore[reportPrivateUsage]
        return service

    @pytest.fixture
    def mock_ctx(self) -> AsyncMock:
        """Create a mock FastMCP context."""
        ctx = AsyncMock()
        ctx.log = AsyncMock()
        return ctx

    @pytest.mark.asyncio
    async def test_mutate_ad_group_criterion_labels_success(
        self,
        service: AdGroupCriterionLabelService,
        mock_client: Any,
        mock_ctx: AsyncMock,
    ) -> None:
        """Test successful ad group criterion labels mutation."""
        customer_id = "1234567890"

        operation = AdGroupCriterionLabelOperation()
        operation.create.ad_group_criterion = (
            "customers/1234567890/adGroupCriteria/123~456"
        )
        operation.create.label = "customers/1234567890/labels/789"
        operations = [operation]

        expected_response = MutateAdGroupCriterionLabelsResponse(
            results=[
                MutateAdGroupCriterionLabelResult(
                    resource_name="customers/1234567890/adGroupCriterionLabels/123~456~789"
                )
            ]
        )
        mock_client.mutate_ad_group_criterion_labels.return_value = expected_response  # type: ignore

        response = await service.mutate_ad_group_criterion_labels(
            ctx=mock_ctx,
            customer_id=customer_id,
            operations=operations,
        )

        assert isinstance(response, dict)
        mock_client.mutate_ad_group_criterion_labels.assert_called_once()  # type: ignore
        mock_ctx.log.assert_called()

        call_args = mock_client.mutate_ad_group_criterion_labels.call_args[1]  # type: ignore
        request = call_args["request"]
        assert isinstance(request, MutateAdGroupCriterionLabelsRequest)
        assert request.customer_id == customer_id
        assert len(request.operations) == 1

    @pytest.mark.asyncio
    async def test_mutate_ad_group_criterion_labels_with_options(
        self,
        service: AdGroupCriterionLabelService,
        mock_client: Any,
        mock_ctx: AsyncMock,
    ) -> None:
        """Test ad group criterion labels mutation with all options."""
        customer_id = "1234567890"

        operation = AdGroupCriterionLabelOperation()
        operation.create.ad_group_criterion = (
            "customers/1234567890/adGroupCriteria/123~456"
        )
        operation.create.label = "customers/1234567890/labels/789"
        operations = [operation]

        expected_response = MutateAdGroupCriterionLabelsResponse()
        mock_client.mutate_ad_group_criterion_labels.return_value = expected_response  # type: ignore

        response = await service.mutate_ad_group_criterion_labels(
            ctx=mock_ctx,
            customer_id=customer_id,
            operations=operations,
            partial_failure=True,
            validate_only=True,
        )

        assert isinstance(response, dict)
        call_args = mock_client.mutate_ad_group_criterion_labels.call_args[1]  # type: ignore
        request = call_args["request"]
        assert request.partial_failure is True
        assert request.validate_only is True

    @pytest.mark.asyncio
    async def test_mutate_ad_group_criterion_labels_failure(
        self,
        service: AdGroupCriterionLabelService,
        mock_client: Any,
        mock_ctx: AsyncMock,
    ) -> None:
        """Test ad group criterion labels mutation failure."""
        customer_id = "1234567890"

        operation = AdGroupCriterionLabelOperation()
        operation.create.ad_group_criterion = (
            "customers/1234567890/adGroupCriteria/123~456"
        )
        operation.create.label = "customers/1234567890/labels/789"
        operations = [operation]

        mock_client.mutate_ad_group_criterion_labels.side_effect = Exception(  # type: ignore
            "API Error"
        )

        with pytest.raises(
            Exception, match="Failed to mutate ad group criterion labels"
        ):
            await service.mutate_ad_group_criterion_labels(
                ctx=mock_ctx,
                customer_id=customer_id,
                operations=operations,
            )

    def test_create_ad_group_criterion_label_operation(
        self, service: AdGroupCriterionLabelService
    ) -> None:
        """Test creating ad group criterion label operation."""
        ad_group_criterion = "customers/1234567890/adGroupCriteria/123~456"
        label = "customers/1234567890/labels/789"

        operation = service.create_ad_group_criterion_label_operation(
            ad_group_criterion=ad_group_criterion,
            label=label,
        )

        assert isinstance(operation, AdGroupCriterionLabelOperation)
        assert operation.create.ad_group_criterion == ad_group_criterion
        assert operation.create.label == label

    def test_create_remove_operation(
        self, service: AdGroupCriterionLabelService
    ) -> None:
        """Test creating remove operation."""
        resource_name = "customers/1234567890/adGroupCriterionLabels/123~456~789"

        operation = service.create_remove_operation(resource_name=resource_name)

        assert isinstance(operation, AdGroupCriterionLabelOperation)
        assert operation.remove == resource_name
        assert not operation.create

    @pytest.mark.asyncio
    async def test_assign_label_to_criterion(
        self,
        service: AdGroupCriterionLabelService,
        mock_client: Any,
        mock_ctx: AsyncMock,
    ) -> None:
        """Test assigning a label to a criterion."""
        customer_id = "1234567890"
        ad_group_criterion = "customers/1234567890/adGroupCriteria/123~456"
        label = "customers/1234567890/labels/789"

        expected_response = MutateAdGroupCriterionLabelsResponse(
            results=[
                MutateAdGroupCriterionLabelResult(
                    resource_name="customers/1234567890/adGroupCriterionLabels/123~456~789"
                )
            ]
        )
        mock_client.mutate_ad_group_criterion_labels.return_value = expected_response  # type: ignore

        response = await service.assign_label_to_criterion(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_criterion=ad_group_criterion,
            label=label,
        )

        assert isinstance(response, dict)
        mock_client.mutate_ad_group_criterion_labels.assert_called_once()  # type: ignore

    @pytest.mark.asyncio
    async def test_remove_label_from_criterion(
        self,
        service: AdGroupCriterionLabelService,
        mock_client: Any,
        mock_ctx: AsyncMock,
    ) -> None:
        """Test removing a label from a criterion."""
        customer_id = "1234567890"
        resource_name = "customers/1234567890/adGroupCriterionLabels/123~456~789"

        expected_response = MutateAdGroupCriterionLabelsResponse(
            results=[MutateAdGroupCriterionLabelResult(resource_name=resource_name)]
        )
        mock_client.mutate_ad_group_criterion_labels.return_value = expected_response  # type: ignore

        response = await service.remove_label_from_criterion(
            ctx=mock_ctx,
            customer_id=customer_id,
            resource_name=resource_name,
        )

        assert isinstance(response, dict)
        mock_client.mutate_ad_group_criterion_labels.assert_called_once()  # type: ignore

    @pytest.mark.asyncio
    async def test_assign_multiple_labels_to_criterion(
        self,
        service: AdGroupCriterionLabelService,
        mock_client: Any,
        mock_ctx: AsyncMock,
    ) -> None:
        """Test assigning multiple labels to a criterion."""
        customer_id = "1234567890"
        ad_group_criterion = "customers/1234567890/adGroupCriteria/123~456"
        labels = [
            "customers/1234567890/labels/789",
            "customers/1234567890/labels/101112",
        ]

        expected_response = MutateAdGroupCriterionLabelsResponse(
            results=[
                MutateAdGroupCriterionLabelResult(
                    resource_name="customers/1234567890/adGroupCriterionLabels/123~456~789"
                ),
                MutateAdGroupCriterionLabelResult(
                    resource_name="customers/1234567890/adGroupCriterionLabels/123~456~101112"
                ),
            ]
        )
        mock_client.mutate_ad_group_criterion_labels.return_value = expected_response  # type: ignore

        response = await service.assign_multiple_labels_to_criterion(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_criterion=ad_group_criterion,
            labels=labels,
        )

        assert isinstance(response, dict)
        mock_client.mutate_ad_group_criterion_labels.assert_called_once()  # type: ignore

        call_args = mock_client.mutate_ad_group_criterion_labels.call_args[1]  # type: ignore
        request = call_args["request"]
        assert len(request.operations) == 2

    @pytest.mark.asyncio
    async def test_assign_label_to_multiple_criteria(
        self,
        service: AdGroupCriterionLabelService,
        mock_client: Any,
        mock_ctx: AsyncMock,
    ) -> None:
        """Test assigning a label to multiple criteria."""
        customer_id = "1234567890"
        ad_group_criteria = [
            "customers/1234567890/adGroupCriteria/123~456",
            "customers/1234567890/adGroupCriteria/123~789",
        ]
        label = "customers/1234567890/labels/101112"

        expected_response = MutateAdGroupCriterionLabelsResponse(
            results=[
                MutateAdGroupCriterionLabelResult(
                    resource_name="customers/1234567890/adGroupCriterionLabels/123~456~101112"
                ),
                MutateAdGroupCriterionLabelResult(
                    resource_name="customers/1234567890/adGroupCriterionLabels/123~789~101112"
                ),
            ]
        )
        mock_client.mutate_ad_group_criterion_labels.return_value = expected_response  # type: ignore

        response = await service.assign_label_to_multiple_criteria(
            ctx=mock_ctx,
            customer_id=customer_id,
            ad_group_criteria=ad_group_criteria,
            label=label,
        )

        assert isinstance(response, dict)
        mock_client.mutate_ad_group_criterion_labels.assert_called_once()  # type: ignore

        call_args = mock_client.mutate_ad_group_criterion_labels.call_args[1]  # type: ignore
        request = call_args["request"]
        assert len(request.operations) == 2

    def test_register_tools(self) -> None:
        """Test registering tools."""
        mock_mcp = Mock()
        service = register_ad_group_criterion_label_tools(mock_mcp)
        assert isinstance(service, AdGroupCriterionLabelService)
        assert mock_mcp.tool.call_count > 0
