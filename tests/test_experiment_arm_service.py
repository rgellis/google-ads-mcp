"""Tests for Google Ads Experiment Arm Service"""

import pytest
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

from fastmcp import Context
from google.ads.googleads.v23.services.types.experiment_arm_service import (
    ExperimentArmOperation,
    MutateExperimentArmsResponse,
    MutateExperimentArmResult,
)

from src.services.campaign.experiment_arm_service import ExperimentArmService


@pytest.fixture
def mock_service_client() -> Any:
    """Create a mock ExperimentArm service client"""
    return Mock()


@pytest.fixture
def experiment_arm_service(mock_service_client: Any) -> ExperimentArmService:
    """Create ExperimentArmService instance with mock client"""
    service = ExperimentArmService()
    service._client = mock_service_client  # type: ignore
    return service


def test_create_experiment_arm_operation(
    experiment_arm_service: ExperimentArmService,
) -> None:
    """Test creating experiment arm operation for creation"""
    experiment = "customers/1234567890/experiments/123"
    name = "Test Experiment Arm"
    control = True
    traffic_split = 50
    campaigns = ["customers/1234567890/campaigns/456"]

    operation = experiment_arm_service.create_experiment_arm_operation(
        experiment=experiment,
        name=name,
        control=control,
        traffic_split=traffic_split,
        campaigns=campaigns,
    )

    assert isinstance(operation, ExperimentArmOperation)
    assert operation.create.experiment == experiment
    assert operation.create.name == name
    assert operation.create.control == control
    assert operation.create.traffic_split == traffic_split
    assert operation.create.campaigns == campaigns


def test_create_experiment_arm_operation_without_campaigns(
    experiment_arm_service: ExperimentArmService,
) -> None:
    """Test creating experiment arm operation without campaigns"""
    experiment = "customers/1234567890/experiments/123"
    name = "Test Experiment Arm"
    control = False
    traffic_split = 50

    operation = experiment_arm_service.create_experiment_arm_operation(
        experiment=experiment,
        name=name,
        control=control,
        traffic_split=traffic_split,
    )

    assert isinstance(operation, ExperimentArmOperation)
    assert operation.create.experiment == experiment
    assert operation.create.name == name
    assert operation.create.control == control
    assert operation.create.traffic_split == traffic_split
    assert operation.create.campaigns == []


def test_update_experiment_arm_operation(
    experiment_arm_service: ExperimentArmService,
) -> None:
    """Test creating experiment arm operation for update"""
    resource_name = "customers/1234567890/experimentArms/123~456"
    name = "Updated Experiment Arm"
    traffic_split = 60
    campaigns = ["customers/1234567890/campaigns/789"]

    operation = experiment_arm_service.update_experiment_arm_operation(
        resource_name=resource_name,
        name=name,
        traffic_split=traffic_split,
        campaigns=campaigns,
    )

    assert isinstance(operation, ExperimentArmOperation)
    assert operation.update.resource_name == resource_name
    assert operation.update.name == name
    assert operation.update.traffic_split == traffic_split
    assert operation.update.campaigns == campaigns
    assert set(operation.update_mask.paths) == {
        "name",
        "traffic_split",
        "campaigns",
    }


def test_update_experiment_arm_operation_partial(
    experiment_arm_service: ExperimentArmService,
) -> None:
    """Test creating experiment arm operation for partial update"""
    resource_name = "customers/1234567890/experimentArms/123~456"
    name = "Updated Experiment Arm"

    operation = experiment_arm_service.update_experiment_arm_operation(
        resource_name=resource_name, name=name
    )

    assert isinstance(operation, ExperimentArmOperation)
    assert operation.update.resource_name == resource_name
    assert operation.update.name == name
    assert operation.update_mask.paths == ["name"]


def test_remove_experiment_arm_operation(
    experiment_arm_service: ExperimentArmService,
) -> None:
    """Test creating experiment arm operation for removal"""
    resource_name = "customers/1234567890/experimentArms/123~456"

    operation = experiment_arm_service.remove_experiment_arm_operation(resource_name)

    assert isinstance(operation, ExperimentArmOperation)
    assert operation.remove == resource_name


@pytest.mark.asyncio
async def test_mutate_experiment_arms(
    experiment_arm_service: ExperimentArmService,
    mock_service_client: Any,
    mock_ctx: Context,
) -> None:
    """Test mutating experiment arms"""
    customer_id = "1234567890"
    operations = [ExperimentArmOperation()]

    mock_response = MutateExperimentArmsResponse(
        results=[
            MutateExperimentArmResult(
                resource_name="customers/1234567890/experimentArms/123~456"
            )
        ]
    )
    mock_service_client.mutate_experiment_arms.return_value = mock_response  # type: ignore

    expected_result = {
        "results": [{"resource_name": "customers/1234567890/experimentArms/123~456"}]
    }

    with patch(
        "src.services.campaign.experiment_arm_service.serialize_proto_message",
        return_value=expected_result,
    ):
        response = await experiment_arm_service.mutate_experiment_arms(
            ctx=mock_ctx,
            customer_id=customer_id,
            operations=operations,
            partial_failure=True,
            validate_only=False,
        )

    assert response == expected_result

    call_args = mock_service_client.mutate_experiment_arms.call_args  # type: ignore
    request = call_args.kwargs["request"]
    assert request.customer_id == customer_id
    assert request.operations == operations


@pytest.mark.asyncio
async def test_mutate_experiment_arms_response_content_type(
    experiment_arm_service: ExperimentArmService,
    mock_service_client: Any,
    mock_ctx: Context,
) -> None:
    """Test response_content_type parameter reaches the request"""
    customer_id = "1234567890"
    operations = [ExperimentArmOperation()]

    mock_response = MutateExperimentArmsResponse(
        results=[
            MutateExperimentArmResult(
                resource_name="customers/1234567890/experimentArms/123~456"
            )
        ]
    )
    mock_service_client.mutate_experiment_arms.return_value = mock_response  # type: ignore

    with patch(
        "src.services.campaign.experiment_arm_service.serialize_proto_message",
        return_value={"results": []},
    ):
        await experiment_arm_service.mutate_experiment_arms(
            ctx=mock_ctx,
            customer_id=customer_id,
            operations=operations,
            response_content_type="MUTABLE_RESOURCE",
        )

    call_args = mock_service_client.mutate_experiment_arms.call_args  # type: ignore
    request = call_args.kwargs["request"]
    assert request.customer_id == customer_id
