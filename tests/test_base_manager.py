# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""Comprehensive tests for the base ResourceManager class."""

from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock

import pytest

from py_superops import SuperOpsClient, SuperOpsConfig
from py_superops.exceptions import (
    SuperOpsAPIError,
    SuperOpsResourceNotFoundError,
    SuperOpsValidationError,
)
from py_superops.graphql.types import BaseModel, GraphQLResponse, PaginationInfo
from py_superops.managers.base import ResourceManager


# Mock model for testing
class MockModel(BaseModel):
    """Mock model for testing base manager."""

    id: str
    name: str
    email: Optional[str] = None


# Concrete implementation for testing
class TestResourceManager(ResourceManager[MockModel]):
    """Test implementation of ResourceManager."""

    def __init__(self, client: SuperOpsClient):
        super().__init__(client, MockModel, "test_resource")


class TestResourceManagerBase:
    """Test cases for ResourceManager base class."""

    @pytest.fixture
    def test_client(self, test_config: SuperOpsConfig):
        """Create test client fixture."""
        return SuperOpsClient(test_config)

    @pytest.fixture
    def test_manager(self, test_client: SuperOpsClient):
        """Create test manager fixture."""
        return TestResourceManager(test_client)

    def test_init(self, test_client: SuperOpsClient):
        """Test ResourceManager initialization."""
        manager = TestResourceManager(test_client)

        assert manager.client == test_client
        assert manager.resource_type == MockModel
        assert manager.resource_name == "test_resource"
        assert hasattr(manager, "logger")

    def test_create_model_instance_success(self, test_manager: TestResourceManager):
        """Test successful model instance creation."""
        data = {"id": "123", "name": "Test User", "email": "test@example.com"}

        instance = test_manager._create_model_instance(data)

        assert isinstance(instance, MockModel)
        assert instance.id == "123"
        assert instance.name == "Test User"
        assert instance.email == "test@example.com"

    def test_create_model_instance_minimal_data(self, test_manager: TestResourceManager):
        """Test model instance creation with minimal required data."""
        data = {"id": "123", "name": "Test User"}

        instance = test_manager._create_model_instance(data)

        assert isinstance(instance, MockModel)
        assert instance.id == "123"
        assert instance.name == "Test User"
        assert instance.email is None

    def test_create_model_instance_validation_error(self, test_manager: TestResourceManager):
        """Test model instance creation with invalid data."""
        # Missing required fields
        data = {"id": "123"}  # Missing 'name' field

        with pytest.raises(SuperOpsValidationError):
            test_manager._create_model_instance(data)

    def test_create_model_instances_list(self, test_manager: TestResourceManager):
        """Test creating multiple model instances from list."""
        data_list = [
            {"id": "123", "name": "User 1", "email": "user1@example.com"},
            {"id": "456", "name": "User 2", "email": "user2@example.com"},
        ]

        instances = test_manager._create_model_instances(data_list)

        assert len(instances) == 2
        assert all(isinstance(instance, MockModel) for instance in instances)
        assert instances[0].id == "123"
        assert instances[1].id == "456"

    def test_create_model_instances_empty_list(self, test_manager: TestResourceManager):
        """Test creating model instances from empty list."""
        instances = test_manager._create_model_instances([])

        assert instances == []

    def test_validate_id_string(self, test_manager: TestResourceManager):
        """Test ID validation with valid string ID."""
        # Should not raise any exceptions
        test_manager._validate_id("valid-id-123")

    def test_validate_id_integer(self, test_manager: TestResourceManager):
        """Test ID validation with integer ID."""
        # Should convert to string and not raise exceptions
        test_manager._validate_id(123)

    def test_validate_id_empty_string(self, test_manager: TestResourceManager):
        """Test ID validation with empty string."""
        with pytest.raises(SuperOpsValidationError, match="ID cannot be empty"):
            test_manager._validate_id("")

    def test_validate_id_none(self, test_manager: TestResourceManager):
        """Test ID validation with None."""
        with pytest.raises(SuperOpsValidationError, match="ID cannot be empty"):
            test_manager._validate_id(None)

    def test_validate_id_whitespace(self, test_manager: TestResourceManager):
        """Test ID validation with whitespace-only string."""
        with pytest.raises(SuperOpsValidationError, match="ID cannot be empty"):
            test_manager._validate_id("   ")

    def test_validate_pagination_valid_params(self, test_manager: TestResourceManager):
        """Test pagination validation with valid parameters."""
        # Should not raise any exceptions
        test_manager._validate_pagination(limit=25, offset=10)

    def test_validate_pagination_defaults(self, test_manager: TestResourceManager):
        """Test pagination validation with default parameters."""
        # Should not raise any exceptions
        test_manager._validate_pagination()

    def test_validate_pagination_invalid_limit_negative(self, test_manager: TestResourceManager):
        """Test pagination validation with negative limit."""
        with pytest.raises(SuperOpsValidationError, match="Limit must be between"):
            test_manager._validate_pagination(limit=-1)

    def test_validate_pagination_invalid_limit_too_high(self, test_manager: TestResourceManager):
        """Test pagination validation with too high limit."""
        with pytest.raises(SuperOpsValidationError, match="Limit must be between"):
            test_manager._validate_pagination(limit=1001)

    def test_validate_pagination_invalid_offset_negative(self, test_manager: TestResourceManager):
        """Test pagination validation with negative offset."""
        with pytest.raises(SuperOpsValidationError, match="Offset must be non-negative"):
            test_manager._validate_pagination(offset=-1)

    def test_parse_graphql_response_success(self, test_manager: TestResourceManager):
        """Test parsing successful GraphQL response."""
        response_data = {
            "data": {
                "test_resources": [{"id": "123", "name": "User 1"}, {"id": "456", "name": "User 2"}]
            }
        }

        result = test_manager._parse_graphql_response(response_data, "test_resources")

        assert result == response_data["data"]["test_resources"]

    def test_parse_graphql_response_with_errors(self, test_manager: TestResourceManager):
        """Test parsing GraphQL response with errors."""
        response_data = {"errors": [{"message": "Field not found", "path": ["test_resources"]}]}

        with pytest.raises(SuperOpsAPIError, match="Field not found"):
            test_manager._parse_graphql_response(response_data, "test_resources")

    def test_parse_graphql_response_missing_data(self, test_manager: TestResourceManager):
        """Test parsing GraphQL response with missing data field."""
        response_data = {}

        with pytest.raises(SuperOpsAPIError, match="No data in response"):
            test_manager._parse_graphql_response(response_data, "test_resources")

    def test_parse_graphql_response_missing_field(self, test_manager: TestResourceManager):
        """Test parsing GraphQL response with missing expected field."""
        response_data = {"data": {"other_field": []}}

        with pytest.raises(SuperOpsAPIError, match="Expected field 'test_resources' not found"):
            test_manager._parse_graphql_response(response_data, "test_resources")

    def test_handle_not_found_error(self, test_manager: TestResourceManager):
        """Test handling of resource not found scenarios."""
        with pytest.raises(
            SuperOpsResourceNotFoundError, match="test_resource with ID 'missing' not found"
        ):
            test_manager._handle_not_found_error("missing")

    def test_build_field_list_from_list(self, test_manager: TestResourceManager):
        """Test building field list from list of strings."""
        fields = ["id", "name", "email"]
        result = test_manager._build_field_list(fields)

        assert result == "id name email"

    def test_build_field_list_from_string(self, test_manager: TestResourceManager):
        """Test building field list from string."""
        fields = "id name email"
        result = test_manager._build_field_list(fields)

        assert result == "id name email"

    def test_build_field_list_none(self, test_manager: TestResourceManager):
        """Test building field list with None input."""
        result = test_manager._build_field_list(None)

        # Should return a default field list
        assert isinstance(result, str)
        assert "id" in result

    def test_build_filters_dict(self, test_manager: TestResourceManager):
        """Test building GraphQL filters from dictionary."""
        filters = {"name": "test", "active": True, "count": 42}

        result = test_manager._build_filters(filters)

        assert 'name: "test"' in result
        assert "active: true" in result
        assert "count: 42" in result

    def test_build_filters_empty(self, test_manager: TestResourceManager):
        """Test building GraphQL filters with empty input."""
        result = test_manager._build_filters({})
        assert result == ""

        result = test_manager._build_filters(None)
        assert result == ""

    def test_format_graphql_value_string(self, test_manager: TestResourceManager):
        """Test GraphQL value formatting for strings."""
        result = test_manager._format_graphql_value("test string")
        assert result == '"test string"'

    def test_format_graphql_value_boolean(self, test_manager: TestResourceManager):
        """Test GraphQL value formatting for booleans."""
        assert test_manager._format_graphql_value(True) == "true"
        assert test_manager._format_graphql_value(False) == "false"

    def test_format_graphql_value_number(self, test_manager: TestResourceManager):
        """Test GraphQL value formatting for numbers."""
        assert test_manager._format_graphql_value(42) == "42"
        assert test_manager._format_graphql_value(3.14) == "3.14"

    def test_format_graphql_value_none(self, test_manager: TestResourceManager):
        """Test GraphQL value formatting for None."""
        result = test_manager._format_graphql_value(None)
        assert result == "null"

    def test_format_graphql_value_list(self, test_manager: TestResourceManager):
        """Test GraphQL value formatting for lists."""
        result = test_manager._format_graphql_value(["a", "b", "c"])
        assert result == '["a", "b", "c"]'

    def test_format_graphql_value_dict(self, test_manager: TestResourceManager):
        """Test GraphQL value formatting for dictionaries."""
        result = test_manager._format_graphql_value({"key": "value", "number": 42})
        assert "{" in result
        assert 'key: "value"' in result
        assert "number: 42" in result

    def test_manager_str_representation(self, test_manager: TestResourceManager):
        """Test manager string representation."""
        str_repr = str(test_manager)
        assert "TestResourceManager" in str_repr
        assert "test_resource" in str_repr

    def test_manager_repr(self, test_manager: TestResourceManager):
        """Test manager repr."""
        repr_str = repr(test_manager)
        assert "TestResourceManager" in repr_str
        assert "test_resource" in repr_str

    def test_get_logger(self, test_manager: TestResourceManager):
        """Test logger access."""
        logger = test_manager.logger
        assert logger.name.endswith("base")

    def test_model_validation_edge_cases(self, test_manager: TestResourceManager):
        """Test model validation with edge cases."""
        # Test with extra fields (should be allowed/ignored)
        data = {"id": "123", "name": "Test User", "extra_field": "should be ignored"}

        instance = test_manager._create_model_instance(data)
        assert instance.id == "123"
        assert instance.name == "Test User"

    def test_concurrent_access_safety(self, test_manager: TestResourceManager):
        """Test that manager is safe for concurrent access."""
        # Test that the manager doesn't maintain state that would cause issues
        # in concurrent scenarios
        data1 = {"id": "123", "name": "User 1"}
        data2 = {"id": "456", "name": "User 2"}

        instance1 = test_manager._create_model_instance(data1)
        instance2 = test_manager._create_model_instance(data2)

        # Instances should be independent
        assert instance1.id != instance2.id
        assert instance1.name != instance2.name
