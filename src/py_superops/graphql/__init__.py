# # Copyright (c) 2024 SuperOps Team
# # Licensed under the MIT License.
# # See LICENSE file in the project root for full license information.

"""GraphQL utilities for the py-superops client library.

This package provides type-safe GraphQL query building, common queries,
and response handling for the SuperOps API.

Key Components:
    - Types: GraphQL type definitions and response models
    - Fragments: Reusable GraphQL fragments for common fields
    - Builder: Type-safe query and mutation builder classes
    - Queries: Pre-built common queries for SuperOps resources

Example Usage:
    ```python
    from py_superops.graphql import (
        CommonQueries,
        ClientQueryBuilder,
        ClientFilter,
        PaginationArgs,
        ClientStatus
    )

    # Using pre-built queries
    query, variables = CommonQueries.list_active_clients(page=1, page_size=25)

    # Using builders for custom queries
    builder = ClientQueryBuilder(detail_level="full")
    filter_obj = ClientFilter(status=ClientStatus.ACTIVE)
    pagination = PaginationArgs(page=1, pageSize=25)

    query = builder.build_list(filter_obj=filter_obj, pagination=pagination)
    variables = builder.get_variables()

    # Execute with SuperOpsClient
    async with SuperOpsClient(config) as client:
        response = await client.execute_query(query, variables)
        data = response['data']['clients']
    ```
"""

# Query and mutation builders
from .builder import (  # Base builders; Specific builders; Factory functions
    AssetQueryBuilder,
    ClientMutationBuilder,
    ClientQueryBuilder,
    MutationBuilder,
    ProjectMutationBuilder,
    ProjectQueryBuilder,
    QueryBuilder,
    SelectionQueryBuilder,
    TicketMutationBuilder,
    TicketQueryBuilder,
    create_asset_query_builder,
    create_client_mutation_builder,
    create_client_query_builder,
    create_project_mutation_builder,
    create_project_query_builder,
    create_ticket_mutation_builder,
    create_ticket_query_builder,
)

# GraphQL fragments
from .fragments import (  # Individual fragments; Fragment collections; Utility functions
    ALL_FRAGMENTS,
    ASSET_CORE_FIELDS,
    ASSET_FRAGMENTS,
    ASSET_FULL_FIELDS,
    ASSET_SUMMARY_FIELDS,
    BASE_FIELDS,
    CLIENT_CORE_FIELDS,
    CLIENT_FRAGMENTS,
    CLIENT_FULL_FIELDS,
    CLIENT_SUMMARY_FIELDS,
    CONTACT_CORE_FIELDS,
    CONTACT_FRAGMENTS,
    CONTACT_FULL_FIELDS,
    KB_ARTICLE_CORE_FIELDS,
    KB_ARTICLE_FULL_FIELDS,
    KB_ARTICLE_SUMMARY_FIELDS,
    KB_COLLECTION_CORE_FIELDS,
    KB_COLLECTION_FULL_FIELDS,
    KB_FRAGMENTS,
    PAGINATION_INFO,
    PROJECT_CORE_FIELDS,
    PROJECT_FRAGMENTS,
    PROJECT_FULL_FIELDS,
    PROJECT_MILESTONE_FIELDS,
    PROJECT_SUMMARY_FIELDS,
    PROJECT_TASK_CORE_FIELDS,
    PROJECT_TASK_FULL_FIELDS,
    PROJECT_TIME_ENTRY_FIELDS,
    SITE_CORE_FIELDS,
    SITE_FRAGMENTS,
    SITE_FULL_FIELDS,
    TICKET_COMMENT_FIELDS,
    TICKET_CORE_FIELDS,
    TICKET_FRAGMENTS,
    TICKET_FULL_FIELDS,
    TICKET_SUMMARY_FIELDS,
    build_fragments_string,
    create_query_with_fragments,
    get_asset_fields,
    get_client_fields,
    get_fragment_spreads,
    get_kb_fields,
    get_project_fields,
    get_ticket_fields,
    resolve_dependencies,
)

# Pre-built queries
from .queries import CommonQueries, SuperOpsQueries

# Type definitions and models
from .types import (  # Base types; Enums; Models; Filters; Input types for mutations; Response types; Utility functions
    Asset,
    AssetFilter,
    AssetInput,
    AssetsResponse,
    AssetStatus,
    BaseModel,
    Client,
    ClientFilter,
    ClientInput,
    ClientsResponse,
    ClientStatus,
    Contact,
    ContactInput,
    ContactsResponse,
    GraphQLResponse,
    KnowledgeBaseArticle,
    KnowledgeBaseArticleInput,
    KnowledgeBaseArticlesResponse,
    KnowledgeBaseCollection,
    KnowledgeBaseCollectionInput,
    KnowledgeBaseCollectionsResponse,
    PaginatedResponse,
    PaginationArgs,
    PaginationInfo,
    Project,
    ProjectFilter,
    ProjectInput,
    ProjectMilestone,
    ProjectPriority,
    ProjectsResponse,
    ProjectStatus,
    ProjectTask,
    ProjectTimeEntry,
    Site,
    SiteInput,
    SitesResponse,
    SortArgs,
    Ticket,
    TicketComment,
    TicketFilter,
    TicketInput,
    TicketPriority,
    TicketsResponse,
    TicketStatus,
    convert_datetime_to_iso,
    convert_iso_to_datetime,
    serialize_filter_value,
    serialize_input,
)

# Version information
__version__ = "0.1.0"
__all__ = [
    # Types and models
    "GraphQLResponse",
    "PaginationInfo",
    "BaseModel",
    "PaginationArgs",
    "SortArgs",
    "TicketStatus",
    "TicketPriority",
    "AssetStatus",
    "ClientStatus",
    "ProjectStatus",
    "ProjectPriority",
    "Client",
    "Contact",
    "Site",
    "Asset",
    "Ticket",
    "TicketComment",
    "Project",
    "ProjectMilestone",
    "ProjectTask",
    "ProjectTimeEntry",
    "KnowledgeBaseCollection",
    "KnowledgeBaseArticle",
    "ClientFilter",
    "TicketFilter",
    "AssetFilter",
    "ProjectFilter",
    "ClientInput",
    "TicketInput",
    "AssetInput",
    "ProjectInput",
    "ContactInput",
    "SiteInput",
    "KnowledgeBaseCollectionInput",
    "KnowledgeBaseArticleInput",
    "PaginatedResponse",
    "ClientsResponse",
    "TicketsResponse",
    "AssetsResponse",
    "ProjectsResponse",
    "ContactsResponse",
    "SitesResponse",
    "KnowledgeBaseCollectionsResponse",
    "KnowledgeBaseArticlesResponse",
    "serialize_input",
    "serialize_filter_value",
    "convert_datetime_to_iso",
    "convert_iso_to_datetime",
    # Fragments
    "BASE_FIELDS",
    "PAGINATION_INFO",
    "CLIENT_CORE_FIELDS",
    "CLIENT_FULL_FIELDS",
    "CLIENT_SUMMARY_FIELDS",
    "CONTACT_CORE_FIELDS",
    "CONTACT_FULL_FIELDS",
    "SITE_CORE_FIELDS",
    "SITE_FULL_FIELDS",
    "ASSET_CORE_FIELDS",
    "ASSET_FULL_FIELDS",
    "ASSET_SUMMARY_FIELDS",
    "TICKET_CORE_FIELDS",
    "TICKET_FULL_FIELDS",
    "TICKET_SUMMARY_FIELDS",
    "TICKET_COMMENT_FIELDS",
    "KB_COLLECTION_CORE_FIELDS",
    "KB_COLLECTION_FULL_FIELDS",
    "KB_ARTICLE_CORE_FIELDS",
    "KB_ARTICLE_FULL_FIELDS",
    "KB_ARTICLE_SUMMARY_FIELDS",
    "PROJECT_CORE_FIELDS",
    "PROJECT_FULL_FIELDS",
    "PROJECT_SUMMARY_FIELDS",
    "PROJECT_MILESTONE_FIELDS",
    "PROJECT_TASK_CORE_FIELDS",
    "PROJECT_TASK_FULL_FIELDS",
    "PROJECT_TIME_ENTRY_FIELDS",
    "ALL_FRAGMENTS",
    "CLIENT_FRAGMENTS",
    "CONTACT_FRAGMENTS",
    "SITE_FRAGMENTS",
    "ASSET_FRAGMENTS",
    "TICKET_FRAGMENTS",
    "KB_FRAGMENTS",
    "PROJECT_FRAGMENTS",
    "resolve_dependencies",
    "build_fragments_string",
    "get_fragment_spreads",
    "create_query_with_fragments",
    "get_client_fields",
    "get_ticket_fields",
    "get_asset_fields",
    "get_kb_fields",
    "get_project_fields",
    # Builders
    "QueryBuilder",
    "SelectionQueryBuilder",
    "MutationBuilder",
    "ClientQueryBuilder",
    "TicketQueryBuilder",
    "AssetQueryBuilder",
    "ProjectQueryBuilder",
    "ClientMutationBuilder",
    "TicketMutationBuilder",
    "ProjectMutationBuilder",
    "create_client_query_builder",
    "create_ticket_query_builder",
    "create_asset_query_builder",
    "create_project_query_builder",
    "create_client_mutation_builder",
    "create_ticket_mutation_builder",
    "create_project_mutation_builder",
    # Queries
    "CommonQueries",
    "SuperOpsQueries",
]


# Convenience functions for easy access
def build_client_list_query(
    status: ClientStatus = None,
    name_search: str = None,
    page: int = 1,
    page_size: int = 50,
    detail_level: str = "core",
) -> tuple[str, dict]:
    """Build a client list query with common filters.

    Args:
        status: Client status filter
        name_search: Name search filter
        page: Page number
        page_size: Items per page
        detail_level: Level of detail (summary, core, full)

    Returns:
        Tuple of (query string, variables dict)
    """
    if name_search:
        return CommonQueries.search_clients_by_name(name_search, page, page_size, detail_level)
    elif status:
        builder = create_client_query_builder(detail_level)
        client_filter = ClientFilter(status=status)
        pagination = PaginationArgs(page=page, pageSize=page_size)

        query = builder.build_list(filter_obj=client_filter, pagination=pagination)
        variables = builder.get_variables()

        return query, variables
    else:
        return CommonQueries.list_all_clients(page, page_size, detail_level=detail_level)


def build_ticket_list_query(
    client_id: str = None,
    status: TicketStatus = None,
    priority: TicketPriority = None,
    assigned_to: str = None,
    page: int = 1,
    page_size: int = 50,
    detail_level: str = "core",
    include_comments: bool = False,
) -> tuple[str, dict]:
    """Build a ticket list query with common filters.

    Args:
        client_id: Client ID filter
        status: Ticket status filter
        priority: Ticket priority filter
        assigned_to: Assigned to filter
        page: Page number
        page_size: Items per page
        detail_level: Level of detail (summary, core, full)
        include_comments: Whether to include comments

    Returns:
        Tuple of (query string, variables dict)
    """
    builder = create_ticket_query_builder(detail_level, include_comments)

    # Build filter
    filter_kwargs = {}
    if client_id:
        filter_kwargs["client_id"] = client_id
    if status:
        filter_kwargs["status"] = status
    if priority:
        filter_kwargs["priority"] = priority
    if assigned_to:
        filter_kwargs["assigned_to"] = assigned_to

    ticket_filter = TicketFilter(**filter_kwargs) if filter_kwargs else None
    pagination = PaginationArgs(page=page, pageSize=page_size)
    sort_args = SortArgs(field="createdAt", direction="DESC")

    query = builder.build_list(filter_obj=ticket_filter, pagination=pagination, sort=sort_args)
    variables = builder.get_variables()

    return query, variables


def build_asset_list_query(
    client_id: str = None,
    asset_type: str = None,
    status: AssetStatus = None,
    page: int = 1,
    page_size: int = 50,
    detail_level: str = "core",
) -> tuple[str, dict]:
    """Build an asset list query with common filters.

    Args:
        client_id: Client ID filter
        asset_type: Asset type filter
        status: Asset status filter
        page: Page number
        page_size: Items per page
        detail_level: Level of detail (summary, core, full)

    Returns:
        Tuple of (query string, variables dict)
    """
    builder = create_asset_query_builder(detail_level)

    # Build filter
    filter_kwargs = {}
    if client_id:
        filter_kwargs["client_id"] = client_id
    if asset_type:
        filter_kwargs["asset_type"] = asset_type
    if status:
        filter_kwargs["status"] = status

    asset_filter = AssetFilter(**filter_kwargs) if filter_kwargs else None
    pagination = PaginationArgs(page=page, pageSize=page_size)
    sort_args = SortArgs(field="name", direction="ASC")

    query = builder.build_list(filter_obj=asset_filter, pagination=pagination, sort=sort_args)
    variables = builder.get_variables()

    return query, variables


def build_project_list_query(
    client_id: str = None,
    status: ProjectStatus = None,
    priority: ProjectPriority = None,
    assigned_to: str = None,
    page: int = 1,
    page_size: int = 50,
    detail_level: str = "core",
    include_milestones: bool = False,
    include_tasks: bool = False,
) -> tuple[str, dict]:
    """Build a project list query with common filters.

    Args:
        client_id: Client ID filter
        status: Project status filter
        priority: Project priority filter
        assigned_to: Assigned to filter
        page: Page number
        page_size: Items per page
        detail_level: Level of detail (summary, core, full)
        include_milestones: Whether to include milestones
        include_tasks: Whether to include tasks

    Returns:
        Tuple of (query string, variables dict)
    """
    builder = create_project_query_builder(detail_level, include_milestones, include_tasks)

    # Build filter
    filter_kwargs = {}
    if client_id:
        filter_kwargs["client_id"] = client_id
    if status:
        filter_kwargs["status"] = status
    if priority:
        filter_kwargs["priority"] = priority
    if assigned_to:
        filter_kwargs["assigned_to"] = assigned_to

    project_filter = ProjectFilter(**filter_kwargs) if filter_kwargs else None
    pagination = PaginationArgs(page=page, pageSize=page_size)
    sort_args = SortArgs(field="createdAt", direction="DESC")

    query = builder.build_list(filter_obj=project_filter, pagination=pagination, sort=sort_args)
    variables = builder.get_variables()

    return query, variables


# Package information
def get_package_info():
    """Get GraphQL utilities package information."""
    return {
        "name": "py-superops.graphql",
        "version": __version__,
        "description": "GraphQL utilities for SuperOps API client",
        "components": [
            "Type-safe query builders",
            "GraphQL fragments and field selection",
            "Pre-built common queries",
            "Response parsing and validation",
            "Pagination and filtering support",
            "Mutation builders for CRUD operations",
        ],
        "supported_resources": [
            "Clients/Customers",
            "Contacts",
            "Sites",
            "Assets",
            "Tickets",
            "Projects",
            "Knowledge Base Collections",
            "Knowledge Base Articles",
        ],
    }
