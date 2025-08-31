# # Copyright (c) 2024 SuperOps Team
# # Licensed under the MIT License.
# # See LICENSE file in the project root for full license information.

"""Pre-built common queries for SuperOps resources.

This module provides ready-to-use GraphQL queries for common operations,
following patterns discovered from migrator tool analysis.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from .builder import (
    create_asset_query_builder,
    create_client_query_builder,
    create_ticket_query_builder,
)
from .types import (
    AssetFilter,
    AssetStatus,
    ClientFilter,
    ClientStatus,
    PaginationArgs,
    SortArgs,
    TicketFilter,
    TicketPriority,
    TicketStatus,
)


class CommonQueries:
    """Collection of common GraphQL queries for SuperOps resources."""

    # Client Queries
    @staticmethod
    def list_all_clients(
        page: int = 1,
        page_size: int = 50,
        sort_field: str = "name",
        sort_direction: str = "ASC",
        detail_level: str = "core",
    ) -> tuple[str, Dict[str, Any]]:
        """Get all clients with pagination.

        Args:
            page: Page number
            page_size: Items per page
            sort_field: Field to sort by
            sort_direction: Sort direction (ASC/DESC)
            detail_level: Level of detail (summary, core, full)

        Returns:
            Tuple of (query string, variables dict)
        """
        builder = create_client_query_builder(detail_level)
        pagination = PaginationArgs(page=page, pageSize=page_size)
        sort_args = SortArgs(field=sort_field, direction=sort_direction)

        query = builder.build_list(pagination=pagination, sort=sort_args)
        variables = builder.get_variables()

        return query, variables

    @staticmethod
    def list_active_clients(
        page: int = 1, page_size: int = 50, detail_level: str = "core"
    ) -> tuple[str, Dict[str, Any]]:
        """Get only active clients.

        Args:
            page: Page number
            page_size: Items per page
            detail_level: Level of detail (summary, core, full)

        Returns:
            Tuple of (query string, variables dict)
        """
        builder = create_client_query_builder(detail_level)
        client_filter = ClientFilter(status=ClientStatus.ACTIVE)
        pagination = PaginationArgs(page=page, pageSize=page_size)

        query = builder.build_list(filter_obj=client_filter, pagination=pagination)
        variables = builder.get_variables()

        return query, variables

    @staticmethod
    def search_clients_by_name(
        name_query: str, page: int = 1, page_size: int = 50, detail_level: str = "core"
    ) -> tuple[str, Dict[str, Any]]:
        """Search clients by name.

        Args:
            name_query: Name search query
            page: Page number
            page_size: Items per page
            detail_level: Level of detail (summary, core, full)

        Returns:
            Tuple of (query string, variables dict)
        """
        builder = create_client_query_builder(detail_level)
        client_filter = ClientFilter(name=name_query)
        pagination = PaginationArgs(page=page, pageSize=page_size)

        query = builder.build_list(filter_obj=client_filter, pagination=pagination)
        variables = builder.get_variables()

        return query, variables

    @staticmethod
    def get_client_by_id(client_id: str, detail_level: str = "full") -> tuple[str, Dict[str, Any]]:
        """Get a specific client by ID.

        Args:
            client_id: Client ID
            detail_level: Level of detail (summary, core, full)

        Returns:
            Tuple of (query string, variables dict)
        """
        builder = create_client_query_builder(detail_level)
        query = builder.build_get(client_id)
        variables = builder.get_variables()

        return query, variables

    # Ticket Queries
    @staticmethod
    def list_open_tickets(
        page: int = 1,
        page_size: int = 50,
        sort_field: str = "createdAt",
        sort_direction: str = "DESC",
        detail_level: str = "core",
        include_comments: bool = False,
    ) -> tuple[str, Dict[str, Any]]:
        """Get all open tickets.

        Args:
            page: Page number
            page_size: Items per page
            sort_field: Field to sort by
            sort_direction: Sort direction (ASC/DESC)
            detail_level: Level of detail (summary, core, full)
            include_comments: Whether to include comments

        Returns:
            Tuple of (query string, variables dict)
        """
        builder = create_ticket_query_builder(detail_level, include_comments)
        ticket_filter = TicketFilter(status=TicketStatus.OPEN)
        pagination = PaginationArgs(page=page, pageSize=page_size)
        sort_args = SortArgs(field=sort_field, direction=sort_direction)

        query = builder.build_list(filter_obj=ticket_filter, pagination=pagination, sort=sort_args)
        variables = builder.get_variables()

        return query, variables

    @staticmethod
    def list_tickets_by_client(
        client_id: str,
        status: Optional[TicketStatus] = None,
        page: int = 1,
        page_size: int = 50,
        detail_level: str = "core",
    ) -> tuple[str, Dict[str, Any]]:
        """Get tickets for a specific client.

        Args:
            client_id: Client ID
            status: Optional ticket status filter
            page: Page number
            page_size: Items per page
            detail_level: Level of detail (summary, core, full)

        Returns:
            Tuple of (query string, variables dict)
        """
        builder = create_ticket_query_builder(detail_level)
        ticket_filter = TicketFilter(client_id=client_id, status=status)
        pagination = PaginationArgs(page=page, pageSize=page_size)

        query = builder.build_list(filter_obj=ticket_filter, pagination=pagination)
        variables = builder.get_variables()

        return query, variables

    @staticmethod
    def list_urgent_tickets(
        page: int = 1, page_size: int = 50, detail_level: str = "full"
    ) -> tuple[str, Dict[str, Any]]:
        """Get urgent and critical priority tickets.

        Args:
            page: Page number
            page_size: Items per page
            detail_level: Level of detail (summary, core, full)

        Returns:
            Tuple of (query string, variables dict)
        """
        builder = create_ticket_query_builder(detail_level)
        # Note: For multiple priority values, we'd need to modify the filter
        # This is a simplified version assuming single priority filter
        ticket_filter = TicketFilter(priority=TicketPriority.URGENT)
        pagination = PaginationArgs(page=page, pageSize=page_size)
        sort_args = SortArgs(field="priority", direction="DESC")

        query = builder.build_list(filter_obj=ticket_filter, pagination=pagination, sort=sort_args)
        variables = builder.get_variables()

        return query, variables

    @staticmethod
    def list_overdue_tickets(
        current_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50,
        detail_level: str = "full",
    ) -> tuple[str, Dict[str, Any]]:
        """Get overdue tickets.

        Args:
            current_date: Current date for comparison (defaults to now)
            page: Page number
            page_size: Items per page
            detail_level: Level of detail (summary, core, full)

        Returns:
            Tuple of (query string, variables dict)
        """
        if current_date is None:
            current_date = datetime.now()

        builder = create_ticket_query_builder(detail_level)
        ticket_filter = TicketFilter(due_before=current_date)
        pagination = PaginationArgs(page=page, pageSize=page_size)
        sort_args = SortArgs(field="dueDate", direction="ASC")

        query = builder.build_list(filter_obj=ticket_filter, pagination=pagination, sort=sort_args)
        variables = builder.get_variables()

        return query, variables

    @staticmethod
    def get_ticket_by_id(
        ticket_id: str, detail_level: str = "full", include_comments: bool = True
    ) -> tuple[str, Dict[str, Any]]:
        """Get a specific ticket by ID.

        Args:
            ticket_id: Ticket ID
            detail_level: Level of detail (summary, core, full)
            include_comments: Whether to include comments

        Returns:
            Tuple of (query string, variables dict)
        """
        builder = create_ticket_query_builder(detail_level, include_comments)
        query = builder.build_get(ticket_id)
        variables = builder.get_variables()

        return query, variables

    # Asset Queries
    @staticmethod
    def list_assets_by_client(
        client_id: str,
        status: Optional[AssetStatus] = None,
        page: int = 1,
        page_size: int = 50,
        detail_level: str = "core",
    ) -> tuple[str, Dict[str, Any]]:
        """Get assets for a specific client.

        Args:
            client_id: Client ID
            status: Optional asset status filter
            page: Page number
            page_size: Items per page
            detail_level: Level of detail (summary, core, full)

        Returns:
            Tuple of (query string, variables dict)
        """
        builder = create_asset_query_builder(detail_level)
        asset_filter = AssetFilter(client_id=client_id, status=status)
        pagination = PaginationArgs(page=page, pageSize=page_size)

        query = builder.build_list(filter_obj=asset_filter, pagination=pagination)
        variables = builder.get_variables()

        return query, variables

    @staticmethod
    def list_active_assets(
        page: int = 1, page_size: int = 50, sort_field: str = "name", detail_level: str = "core"
    ) -> tuple[str, Dict[str, Any]]:
        """Get all active assets.

        Args:
            page: Page number
            page_size: Items per page
            sort_field: Field to sort by
            detail_level: Level of detail (summary, core, full)

        Returns:
            Tuple of (query string, variables dict)
        """
        builder = create_asset_query_builder(detail_level)
        asset_filter = AssetFilter(status=AssetStatus.ACTIVE)
        pagination = PaginationArgs(page=page, pageSize=page_size)
        sort_args = SortArgs(field=sort_field, direction="ASC")

        query = builder.build_list(filter_obj=asset_filter, pagination=pagination, sort=sort_args)
        variables = builder.get_variables()

        return query, variables

    @staticmethod
    def search_assets_by_type(
        asset_type: str, page: int = 1, page_size: int = 50, detail_level: str = "core"
    ) -> tuple[str, Dict[str, Any]]:
        """Search assets by type.

        Args:
            asset_type: Asset type to search for
            page: Page number
            page_size: Items per page
            detail_level: Level of detail (summary, core, full)

        Returns:
            Tuple of (query string, variables dict)
        """
        builder = create_asset_query_builder(detail_level)
        asset_filter = AssetFilter(asset_type=asset_type)
        pagination = PaginationArgs(page=page, pageSize=page_size)

        query = builder.build_list(filter_obj=asset_filter, pagination=pagination)
        variables = builder.get_variables()

        return query, variables

    @staticmethod
    def get_asset_by_id(asset_id: str, detail_level: str = "full") -> tuple[str, Dict[str, Any]]:
        """Get a specific asset by ID.

        Args:
            asset_id: Asset ID
            detail_level: Level of detail (summary, core, full)

        Returns:
            Tuple of (query string, variables dict)
        """
        builder = create_asset_query_builder(detail_level)
        query = builder.build_get(asset_id)
        variables = builder.get_variables()

        return query, variables

    # Knowledge Base Queries
    @staticmethod
    def list_kb_collections(
        page: int = 1, page_size: int = 50, is_public: Optional[bool] = None
    ) -> tuple[str, Dict[str, Any]]:
        """Get knowledge base collections.

        Args:
            page: Page number
            page_size: Items per page
            is_public: Filter by public/private status

        Returns:
            Tuple of (query string, variables dict)
        """
        query = """
        query ListKBCollections($page: Int, $pageSize: Int, $isPublic: Boolean) {
          knowledgeBaseCollections(page: $page, pageSize: $pageSize, isPublic: $isPublic) {
            items {
              ...KBCollectionFullFields
            }
            pagination {
              ...PaginationInfo
            }
          }
        }

        fragment KBCollectionFullFields on KnowledgeBaseCollection {
          ...BaseFields
          name
          description
          parentId
          isPublic
          articleCount
        }

        fragment BaseFields on BaseModel {
          id
          createdAt
          updatedAt
        }

        fragment PaginationInfo on PaginationInfo {
          page
          pageSize
          total
          hasNextPage
          hasPreviousPage
        }
        """

        variables = {
            "page": page,
            "pageSize": page_size,
        }

        if is_public is not None:
            variables["isPublic"] = is_public

        return query, variables

    @staticmethod
    def list_kb_articles_by_collection(
        collection_id: str, page: int = 1, page_size: int = 50, is_published: Optional[bool] = None
    ) -> tuple[str, Dict[str, Any]]:
        """Get knowledge base articles by collection.

        Args:
            collection_id: Collection ID
            page: Page number
            page_size: Items per page
            is_published: Filter by published status

        Returns:
            Tuple of (query string, variables dict)
        """
        query = """
        query ListKBArticles($collectionId: ID!, $page: Int, $pageSize: Int, $isPublished: Boolean) {
          knowledgeBaseArticles(
            collectionId: $collectionId,
            page: $page,
            pageSize: $pageSize,
            isPublished: $isPublished
          ) {
            items {
              ...KBArticleFullFields
            }
            pagination {
              ...PaginationInfo
            }
          }
        }

        fragment KBArticleFullFields on KnowledgeBaseArticle {
          ...BaseFields
          collectionId
          title
          content
          summary
          authorId
          authorName
          isPublished
          isFeatured
          viewCount
          tags
        }

        fragment BaseFields on BaseModel {
          id
          createdAt
          updatedAt
        }

        fragment PaginationInfo on PaginationInfo {
          page
          pageSize
          total
          hasNextPage
          hasPreviousPage
        }
        """

        variables = {
            "collectionId": collection_id,
            "page": page,
            "pageSize": page_size,
        }

        if is_published is not None:
            variables["isPublished"] = is_published

        return query, variables

    @staticmethod
    def search_kb_articles(
        search_term: str, page: int = 1, page_size: int = 50, is_published: bool = True
    ) -> tuple[str, Dict[str, Any]]:
        """Search knowledge base articles.

        Args:
            search_term: Search term
            page: Page number
            page_size: Items per page
            is_published: Whether to search only published articles

        Returns:
            Tuple of (query string, variables dict)
        """
        query = """
        query SearchKBArticles($searchTerm: String!, $page: Int, $pageSize: Int, $isPublished: Boolean) {
          searchKnowledgeBaseArticles(
            searchTerm: $searchTerm,
            page: $page,
            pageSize: $pageSize,
            isPublished: $isPublished
          ) {
            items {
              ...KBArticleSummaryFields
            }
            pagination {
              ...PaginationInfo
            }
          }
        }

        fragment KBArticleSummaryFields on KnowledgeBaseArticle {
          id
          title
          summary
          authorName
          isPublished
          viewCount
          createdAt
          updatedAt
        }

        fragment PaginationInfo on PaginationInfo {
          page
          pageSize
          total
          hasNextPage
          hasPreviousPage
        }
        """

        variables = {
            "searchTerm": search_term,
            "page": page,
            "pageSize": page_size,
            "isPublished": is_published,
        }

        return query, variables

    # Dashboard/Overview Queries
    @staticmethod
    def get_client_overview(client_id: str) -> tuple[str, Dict[str, Any]]:
        """Get comprehensive client overview with related data.

        Args:
            client_id: Client ID

        Returns:
            Tuple of (query string, variables dict)
        """
        query = """
        query GetClientOverview($clientId: ID!) {
          client(id: $clientId) {
            ...ClientFullFields
            sites {
              ...SiteCoreFields
            }
            contacts {
              ...ContactCoreFields
            }
          }

          tickets(filter: {clientId: $clientId}, page: 1, pageSize: 10, sortField: "createdAt", sortDirection: DESC) {
            items {
              ...TicketSummaryFields
            }
            pagination {
              total
            }
          }

          assets(filter: {clientId: $clientId}, page: 1, pageSize: 10) {
            items {
              ...AssetSummaryFields
            }
            pagination {
              total
            }
          }
        }

        fragment ClientFullFields on Client {
          ...BaseFields
          name
          email
          phone
          address
          status
          billingAddress
          notes
          tags
          customFields
        }

        fragment SiteCoreFields on Site {
          ...BaseFields
          clientId
          name
          address
        }

        fragment ContactCoreFields on Contact {
          ...BaseFields
          clientId
          firstName
          lastName
          email
          phone
          isPrimary
        }

        fragment TicketSummaryFields on Ticket {
          id
          title
          status
          priority
          assignedTo
          createdAt
          dueDate
        }

        fragment AssetSummaryFields on Asset {
          id
          name
          assetType
          status
          manufacturer
          model
        }

        fragment BaseFields on BaseModel {
          id
          createdAt
          updatedAt
        }
        """

        variables = {"clientId": client_id}

        return query, variables


# Convenience wrapper class for easy access
class SuperOpsQueries(CommonQueries):
    """Extended queries class with additional convenience methods."""

    @classmethod
    def get_dashboard_summary(cls) -> tuple[str, Dict[str, Any]]:
        """Get dashboard summary with key metrics.

        Returns:
            Tuple of (query string, variables dict)
        """
        query = """
        query GetDashboardSummary {
          ticketsSummary: tickets(page: 1, pageSize: 1) {
            pagination {
              total
            }
          }

          openTickets: tickets(filter: {status: OPEN}, page: 1, pageSize: 1) {
            pagination {
              total
            }
          }

          urgentTickets: tickets(filter: {priority: URGENT}, page: 1, pageSize: 1) {
            pagination {
              total
            }
          }

          clientsSummary: clients(page: 1, pageSize: 1) {
            pagination {
              total
            }
          }

          activeClients: clients(filter: {status: ACTIVE}, page: 1, pageSize: 1) {
            pagination {
              total
            }
          }

          assetsSummary: assets(page: 1, pageSize: 1) {
            pagination {
              total
            }
          }
        }
        """

        return query, {}

    @classmethod
    def get_recent_activity(cls, limit: int = 20) -> tuple[str, Dict[str, Any]]:
        """Get recent activity across tickets and assets.

        Args:
            limit: Maximum number of items to return

        Returns:
            Tuple of (query string, variables dict)
        """
        query = """
        query GetRecentActivity($limit: Int) {
          recentTickets: tickets(page: 1, pageSize: $limit, sortField: "updatedAt", sortDirection: DESC) {
            items {
              ...TicketSummaryFields
            }
          }

          recentAssets: assets(page: 1, pageSize: $limit, sortField: "updatedAt", sortDirection: DESC) {
            items {
              ...AssetSummaryFields
            }
          }
        }

        fragment TicketSummaryFields on Ticket {
          id
          title
          status
          priority
          assignedTo
          createdAt
          updatedAt
        }

        fragment AssetSummaryFields on Asset {
          id
          name
          assetType
          status
          updatedAt
        }
        """

        variables = {"limit": limit}

        return query, variables
