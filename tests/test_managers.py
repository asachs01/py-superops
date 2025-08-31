"""Tests for resource managers."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from py_superops.exceptions import (
    SuperOpsAPIError,
    SuperOpsResourceNotFoundError,
    SuperOpsValidationError,
)
from py_superops.graphql.types import AssetStatus, ClientStatus, TicketPriority, TicketStatus
from py_superops.managers import (
    AssetManager,
    ClientManager,
    ContactManager,
    KnowledgeBaseManager,
    SiteManager,
    TicketManager,
)
from py_superops.managers.base import ResourceManager


class TestResourceManager:
    """Test the base ResourceManager class."""

    # Create a concrete implementation for testing
    @dataclass
    class TestModel:
        """Test model for ResourceManager testing."""

        id: str
        name: str
        status: str

        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> "TestResourceManager.TestModel":
            return cls(**data)

    class ConcreteResourceManager(ResourceManager):
        """Concrete ResourceManager for testing."""

        def _build_get_query(self, **kwargs) -> str:
            return """
            query GetTestResource($id: ID!) {
                testResource(id: $id) {
                    id
                    name
                    status
                }
            }
            """

        def _build_list_query(self, **kwargs) -> str:
            return """
            query ListTestResources($page: Int, $pageSize: Int, $filters: TestResourceFilter, $sortBy: String, $sortOrder: SortOrder) {
                testResources(page: $page, pageSize: $pageSize, filter: $filters, sortBy: $sortBy, sortOrder: $sortOrder) {
                    items {
                        id
                        name
                        status
                    }
                    pagination {
                        page
                        pageSize
                        total
                        hasNextPage
                        hasPreviousPage
                    }
                }
            }
            """

        def _build_create_mutation(self, **kwargs) -> str:
            return """
            mutation CreateTestResource($input: TestResourceInput!) {
                createTestresource(input: $input) {
                    id
                    name
                    status
                }
            }
            """

        def _build_update_mutation(self, **kwargs) -> str:
            return """
            mutation UpdateTestResource($id: ID!, $input: TestResourceInput!) {
                updateTestresource(id: $id, input: $input) {
                    id
                    name
                    status
                }
            }
            """

        def _build_delete_mutation(self, **kwargs) -> str:
            return """
            mutation DeleteTestResource($id: ID!) {
                deleteTestresource(id: $id) {
                    success
                    message
                }
            }
            """

        def _build_search_query(self, **kwargs) -> str:
            return """
            query SearchTestResources($query: String!, $page: Int, $pageSize: Int) {
                searchTestresources(query: $query, page: $page, pageSize: $pageSize) {
                    items {
                        id
                        name
                        status
                    }
                    pagination {
                        page
                        pageSize
                        total
                        hasNextPage
                        hasPreviousPage
                    }
                }
            }
            """

    @pytest.fixture
    def mock_client(self):
        """Create a mock SuperOps client."""
        client = AsyncMock()
        client.execute_query = AsyncMock()
        client.execute_mutation = AsyncMock()
        return client

    @pytest.fixture
    def resource_manager(self, mock_client):
        """Create a test resource manager."""
        return self.ConcreteResourceManager(
            client=mock_client, resource_type=self.TestModel, resource_name="testresource"
        )

    @pytest.mark.asyncio
    async def test_get_success(self, resource_manager, mock_client):
        """Test successful resource retrieval."""
        # Setup mock response
        mock_response = {
            "data": {
                "testresource": {"id": "test-123", "name": "Test Resource", "status": "ACTIVE"}
            }
        }
        mock_client.execute_query.return_value = mock_response

        # Test get
        result = await resource_manager.get("test-123")

        # Assertions
        assert result is not None
        assert result.id == "test-123"
        assert result.name == "Test Resource"
        assert result.status == "ACTIVE"

        # Verify query was called correctly
        mock_client.execute_query.assert_called_once()
        call_args = mock_client.execute_query.call_args
        assert "GetTestResource" in call_args[0][0]
        assert call_args[0][1]["id"] == "test-123"

    @pytest.mark.asyncio
    async def test_get_not_found(self, resource_manager, mock_client):
        """Test resource not found scenario."""
        # Setup mock response
        mock_response = {"data": {"testresource": None}}
        mock_client.execute_query.return_value = mock_response

        # Test get
        result = await resource_manager.get("nonexistent")

        # Assertions
        assert result is None

    @pytest.mark.asyncio
    async def test_get_invalid_id(self, resource_manager):
        """Test get with invalid resource ID."""
        with pytest.raises(SuperOpsValidationError, match="Invalid resource ID"):
            await resource_manager.get("")

        with pytest.raises(SuperOpsValidationError, match="Invalid resource ID"):
            await resource_manager.get(None)

    @pytest.mark.asyncio
    async def test_list_success(self, resource_manager, mock_client):
        """Test successful resource listing."""
        # Setup mock response
        mock_response = {
            "data": {
                "testresources": {
                    "items": [
                        {"id": "test-1", "name": "Resource 1", "status": "ACTIVE"},
                        {"id": "test-2", "name": "Resource 2", "status": "INACTIVE"},
                    ],
                    "pagination": {
                        "page": 1,
                        "pageSize": 50,
                        "total": 2,
                        "hasNextPage": False,
                        "hasPreviousPage": False,
                    },
                }
            }
        }
        mock_client.execute_query.return_value = mock_response

        # Test list
        result = await resource_manager.list(page=1, page_size=50)

        # Assertions
        assert "items" in result
        assert "pagination" in result
        assert len(result["items"]) == 2
        assert result["items"][0].id == "test-1"
        assert result["items"][1].id == "test-2"
        assert result["pagination"]["total"] == 2

    @pytest.mark.asyncio
    async def test_list_with_filters(self, resource_manager, mock_client):
        """Test listing with filters."""
        mock_response = {
            "data": {
                "testresources": {
                    "items": [],
                    "pagination": {
                        "page": 1,
                        "pageSize": 25,
                        "total": 0,
                        "hasNextPage": False,
                        "hasPreviousPage": False,
                    },
                }
            }
        }
        mock_client.execute_query.return_value = mock_response

        filters = {"status": "ACTIVE", "name": "Test"}
        result = await resource_manager.list(
            page=1, page_size=25, filters=filters, sort_by="name", sort_order="desc"
        )

        # Verify the query was called with correct parameters
        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["filters"] == filters
        assert variables["sortBy"] == "name"
        assert variables["sortOrder"] == "DESC"

    @pytest.mark.asyncio
    async def test_list_validation_errors(self, resource_manager):
        """Test list parameter validation."""
        # Invalid page
        with pytest.raises(SuperOpsValidationError, match="Page number must be >= 1"):
            await resource_manager.list(page=0)

        # Invalid page size
        with pytest.raises(SuperOpsValidationError, match="Page size must be between 1 and 1000"):
            await resource_manager.list(page_size=0)

        with pytest.raises(SuperOpsValidationError, match="Page size must be between 1 and 1000"):
            await resource_manager.list(page_size=1001)

        # Invalid sort order
        with pytest.raises(SuperOpsValidationError, match="Sort order must be 'asc' or 'desc'"):
            await resource_manager.list(sort_order="invalid")

    @pytest.mark.asyncio
    async def test_create_success(self, resource_manager, mock_client):
        """Test successful resource creation."""
        # Setup mock response
        mock_response = {
            "data": {
                "createTestresource": {"id": "new-123", "name": "New Resource", "status": "ACTIVE"}
            }
        }
        mock_client.execute_mutation.return_value = mock_response

        # Test create
        data = {"name": "New Resource", "status": "ACTIVE"}
        result = await resource_manager.create(data)

        # Assertions
        assert result.id == "new-123"
        assert result.name == "New Resource"
        assert result.status == "ACTIVE"

        # Verify mutation was called correctly
        mock_client.execute_mutation.assert_called_once()
        call_args = mock_client.execute_mutation.call_args
        assert "CreateTestResource" in call_args[0][0]
        assert call_args[0][1]["input"] == data

    @pytest.mark.asyncio
    async def test_create_validation_error(self, resource_manager):
        """Test create with invalid data."""
        with pytest.raises(SuperOpsValidationError, match="Resource data cannot be empty"):
            await resource_manager.create({})

        with pytest.raises(SuperOpsValidationError, match="Resource data cannot be empty"):
            await resource_manager.create(None)

    @pytest.mark.asyncio
    async def test_update_success(self, resource_manager, mock_client):
        """Test successful resource update."""
        # Setup mock response
        mock_response = {
            "data": {
                "updateTestresource": {
                    "id": "test-123",
                    "name": "Updated Resource",
                    "status": "INACTIVE",
                }
            }
        }
        mock_client.execute_mutation.return_value = mock_response

        # Test update
        data = {"name": "Updated Resource", "status": "INACTIVE"}
        result = await resource_manager.update("test-123", data)

        # Assertions
        assert result.id == "test-123"
        assert result.name == "Updated Resource"
        assert result.status == "INACTIVE"

    @pytest.mark.asyncio
    async def test_update_not_found(self, resource_manager, mock_client):
        """Test update of non-existent resource."""
        # Setup mock response
        mock_response = {"data": {"updateTestresource": None}}
        mock_client.execute_mutation.return_value = mock_response

        # Test update
        data = {"name": "Updated Resource"}
        with pytest.raises(SuperOpsResourceNotFoundError):
            await resource_manager.update("nonexistent", data)

    @pytest.mark.asyncio
    async def test_update_validation_errors(self, resource_manager):
        """Test update validation errors."""
        # Invalid resource ID
        with pytest.raises(SuperOpsValidationError, match="Invalid resource ID"):
            await resource_manager.update("", {"name": "Test"})

        # Empty data
        with pytest.raises(SuperOpsValidationError, match="Update data cannot be empty"):
            await resource_manager.update("test-123", {})

    @pytest.mark.asyncio
    async def test_delete_success(self, resource_manager, mock_client):
        """Test successful resource deletion."""
        # Setup mock response
        mock_response = {
            "data": {
                "deleteTestresource": {"success": True, "message": "Resource deleted successfully"}
            }
        }
        mock_client.execute_mutation.return_value = mock_response

        # Test delete
        result = await resource_manager.delete("test-123")

        # Assertions
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_not_found(self, resource_manager, mock_client):
        """Test deletion of non-existent resource."""
        # Setup mock response
        mock_response = {"data": {"deleteTestresource": None}}
        mock_client.execute_mutation.return_value = mock_response

        # Test delete
        with pytest.raises(SuperOpsResourceNotFoundError):
            await resource_manager.delete("nonexistent")

    @pytest.mark.asyncio
    async def test_delete_validation_error(self, resource_manager):
        """Test delete with invalid resource ID."""
        with pytest.raises(SuperOpsValidationError, match="Invalid resource ID"):
            await resource_manager.delete("")

    @pytest.mark.asyncio
    async def test_search_success(self, resource_manager, mock_client):
        """Test successful resource search."""
        # Setup mock response
        mock_response = {
            "data": {
                "searchTestresources": {
                    "items": [{"id": "test-1", "name": "Test Resource", "status": "ACTIVE"}],
                    "pagination": {
                        "page": 1,
                        "pageSize": 50,
                        "total": 1,
                        "hasNextPage": False,
                        "hasPreviousPage": False,
                    },
                }
            }
        }
        mock_client.execute_query.return_value = mock_response

        # Test search
        result = await resource_manager.search("test query", page=1, page_size=50)

        # Assertions
        assert "items" in result
        assert "pagination" in result
        assert len(result["items"]) == 1
        assert result["items"][0].name == "Test Resource"

    @pytest.mark.asyncio
    async def test_search_validation_errors(self, resource_manager):
        """Test search parameter validation."""
        # Empty query
        with pytest.raises(
            SuperOpsValidationError, match="Search query must be a non-empty string"
        ):
            await resource_manager.search("")

        # None query
        with pytest.raises(
            SuperOpsValidationError, match="Search query must be a non-empty string"
        ):
            await resource_manager.search(None)

        # Invalid page
        with pytest.raises(SuperOpsValidationError, match="Page number must be >= 1"):
            await resource_manager.search("test", page=0)

    def test_create_instance_success(self, resource_manager):
        """Test successful instance creation from data."""
        data = {"id": "test-123", "name": "Test", "status": "ACTIVE"}
        instance = resource_manager._create_instance(data)

        assert isinstance(instance, self.TestModel)
        assert instance.id == "test-123"
        assert instance.name == "Test"
        assert instance.status == "ACTIVE"

    def test_create_instance_error(self, resource_manager):
        """Test instance creation with invalid data."""
        # Missing required field
        data = {"name": "Test"}  # Missing 'id' and 'status'

        with pytest.raises(SuperOpsValidationError, match="Invalid testresource data"):
            resource_manager._create_instance(data)

    def test_empty_pagination(self, resource_manager):
        """Test empty pagination creation."""
        pagination = resource_manager._empty_pagination()

        expected = {
            "page": 1,
            "pageSize": 0,
            "total": 0,
            "hasNextPage": False,
            "hasPreviousPage": False,
        }
        assert pagination == expected


class TestClientManager:
    """Test the ClientManager class."""

    @pytest.fixture
    def client_manager(self, client):
        """Create a client manager."""
        return ClientManager(client)

    @pytest.mark.asyncio
    async def test_get_client_by_id(
        self, client_manager, mock_successful_request, mock_success_response
    ):
        """Test getting a client by ID."""
        result = await client_manager.get("client-123")

        # Verify the mock was called
        mock_successful_request.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_clients_with_status_filter(self, client_manager, mock_successful_request):
        """Test listing clients with status filter."""
        await client_manager.list(page=1, page_size=25, filters={"status": ClientStatus.ACTIVE})

        # Verify the request was made
        mock_successful_request.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_client(self, client_manager, mock_successful_request, sample_client_data):
        """Test creating a new client."""
        await client_manager.create(sample_client_data)

        # Verify the mutation was called
        mock_successful_request.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_clients_by_name(self, client_manager, mock_successful_request):
        """Test searching clients by name."""
        await client_manager.search("Acme Corp")

        # Verify the search query was called
        mock_successful_request.post.assert_called_once()


class TestTicketManager:
    """Test the TicketManager class."""

    @pytest.fixture
    def ticket_manager(self, client):
        """Create a ticket manager."""
        return TicketManager(client)

    @pytest.mark.asyncio
    async def test_list_tickets_by_status(self, ticket_manager, mock_successful_request):
        """Test listing tickets by status."""
        await ticket_manager.list(filters={"status": TicketStatus.OPEN})

        mock_successful_request.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_tickets_by_priority(self, ticket_manager, mock_successful_request):
        """Test listing tickets by priority."""
        await ticket_manager.list(filters={"priority": TicketPriority.URGENT})

        mock_successful_request.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_ticket(self, ticket_manager, mock_successful_request, sample_ticket_data):
        """Test creating a new ticket."""
        await ticket_manager.create(sample_ticket_data)

        mock_successful_request.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_ticket_status(self, ticket_manager, mock_successful_request):
        """Test updating ticket status."""
        await ticket_manager.update("ticket-123", {"status": TicketStatus.RESOLVED})

        mock_successful_request.post.assert_called_once()


class TestAssetManager:
    """Test the AssetManager class."""

    @pytest.fixture
    def asset_manager(self, client):
        """Create an asset manager."""
        return AssetManager(client)

    @pytest.mark.asyncio
    async def test_list_assets_by_client(self, asset_manager, mock_successful_request):
        """Test listing assets by client."""
        await asset_manager.list(filters={"client_id": "client-123"})

        mock_successful_request.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_assets_by_type(self, asset_manager, mock_successful_request):
        """Test listing assets by type."""
        await asset_manager.list(filters={"asset_type": "Server"})

        mock_successful_request.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_asset(self, asset_manager, mock_successful_request, sample_asset_data):
        """Test creating a new asset."""
        await asset_manager.create(sample_asset_data)

        mock_successful_request.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_assets_by_serial(self, asset_manager, mock_successful_request):
        """Test searching assets by serial number."""
        await asset_manager.search("ABC123")

        mock_successful_request.post.assert_called_once()


class TestSiteManager:
    """Test the SiteManager class."""

    @pytest.fixture
    def site_manager(self, client):
        """Create a site manager."""
        return SiteManager(client)

    @pytest.mark.asyncio
    async def test_list_sites_by_client(self, site_manager, mock_successful_request):
        """Test listing sites by client."""
        await site_manager.list(filters={"client_id": "client-123"})

        mock_successful_request.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_site(self, site_manager, mock_successful_request, sample_site_data):
        """Test creating a new site."""
        await site_manager.create(sample_site_data)

        mock_successful_request.post.assert_called_once()


class TestContactManager:
    """Test the ContactManager class."""

    @pytest.fixture
    def contact_manager(self, client):
        """Create a contact manager."""
        return ContactManager(client)

    @pytest.mark.asyncio
    async def test_list_contacts_by_client(self, contact_manager, mock_successful_request):
        """Test listing contacts by client."""
        await contact_manager.list(filters={"client_id": "client-123"})

        mock_successful_request.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_contact(
        self, contact_manager, mock_successful_request, sample_contact_data
    ):
        """Test creating a new contact."""
        await contact_manager.create(sample_contact_data)

        mock_successful_request.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_contacts_by_email(self, contact_manager, mock_successful_request):
        """Test searching contacts by email."""
        await contact_manager.search("john.doe@example.com")

        mock_successful_request.post.assert_called_once()


class TestKnowledgeBaseManager:
    """Test the KnowledgeBaseManager class."""

    @pytest.fixture
    def kb_manager(self, client):
        """Create a knowledge base manager."""
        return KnowledgeBaseManager(client)

    @pytest.mark.asyncio
    async def test_list_collections(self, kb_manager, mock_successful_request):
        """Test listing knowledge base collections."""
        await kb_manager.list_collections(is_public=True)

        mock_successful_request.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_articles_by_collection(self, kb_manager, mock_successful_request):
        """Test listing articles by collection."""
        await kb_manager.list_articles(collection_id="collection-123", is_published=True)

        mock_successful_request.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_collection(
        self, kb_manager, mock_successful_request, sample_kb_collection_data
    ):
        """Test creating a knowledge base collection."""
        await kb_manager.create_collection(sample_kb_collection_data)

        mock_successful_request.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_article(
        self, kb_manager, mock_successful_request, sample_kb_article_data
    ):
        """Test creating a knowledge base article."""
        await kb_manager.create_article(sample_kb_article_data)

        mock_successful_request.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_articles(self, kb_manager, mock_successful_request):
        """Test searching knowledge base articles."""
        await kb_manager.search_articles("troubleshooting")

        mock_successful_request.post.assert_called_once()


class TestManagerErrorHandling:
    """Test error handling across all managers."""

    @pytest.mark.asyncio
    async def test_api_error_propagation(self, client):
        """Test that API errors are properly propagated."""
        # Setup client to raise API error
        client.execute_query.side_effect = SuperOpsAPIError("API Error", 500, {})

        manager = ClientManager(client)

        with pytest.raises(SuperOpsAPIError):
            await manager.get("client-123")

    @pytest.mark.asyncio
    async def test_network_error_handling(self, client):
        """Test network error handling."""
        # Setup client to raise network error
        from py_superops.exceptions import SuperOpsNetworkError

        client.execute_query.side_effect = SuperOpsNetworkError("Network error")

        manager = ClientManager(client)

        with pytest.raises(SuperOpsNetworkError):
            await manager.get("client-123")

    @pytest.mark.asyncio
    async def test_validation_error_handling(self, client):
        """Test validation error handling."""
        manager = ClientManager(client)

        # Test invalid parameters that should raise validation errors
        with pytest.raises(SuperOpsValidationError):
            await manager.get("")  # Empty ID

        with pytest.raises(SuperOpsValidationError):
            await manager.list(page=0)  # Invalid page

        with pytest.raises(SuperOpsValidationError):
            await manager.create({})  # Empty data


class TestManagerPerformance:
    """Test performance aspects of managers."""

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client, performance_timer):
        """Test concurrent requests to managers."""
        import asyncio

        # Setup mock responses
        client.execute_query.return_value = {
            "data": {"client": {"id": "test", "name": "Test", "status": "ACTIVE"}}
        }

        manager = ClientManager(client)

        # Test concurrent gets
        with performance_timer() as timer:
            tasks = [manager.get(f"client-{i}") for i in range(10)]
            results = await asyncio.gather(*tasks)

        # Verify all requests completed
        assert len(results) == 10
        assert all(result is not None for result in results)

        # Performance should be reasonable (adjust threshold as needed)
        assert timer.elapsed < 1.0  # Should complete in less than 1 second

    @pytest.mark.asyncio
    async def test_batch_operations(self, client):
        """Test batch operations performance."""
        import asyncio

        # Setup mock response for list operation
        client.execute_query.return_value = {
            "data": {
                "clients": {
                    "items": [
                        {"id": f"client-{i}", "name": f"Client {i}", "status": "ACTIVE"}
                        for i in range(100)
                    ],
                    "pagination": {
                        "page": 1,
                        "pageSize": 100,
                        "total": 100,
                        "hasNextPage": False,
                        "hasPreviousPage": False,
                    },
                }
            }
        }

        manager = ClientManager(client)

        # Test large list operation
        result = await manager.list(page_size=100)

        # Verify efficient batch retrieval
        assert len(result["items"]) == 100
        assert result["pagination"]["total"] == 100
