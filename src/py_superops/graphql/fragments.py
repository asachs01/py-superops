# # Copyright (c) 2024 SuperOps Team
# # Licensed under the MIT License.
# # See LICENSE file in the project root for full license information.

"""Reusable GraphQL fragments for common fields in SuperOps API.

This module provides GraphQL fragments that can be reused across queries and mutations
to maintain consistency and reduce duplication.
"""

from typing import Dict, Set


class GraphQLFragment:
    """Represents a GraphQL fragment with dependencies."""

    def __init__(self, name: str, on_type: str, fields: str, dependencies: Set[str] = None):
        """Initialize a GraphQL fragment.

        Args:
            name: Fragment name
            on_type: GraphQL type the fragment applies to
            fields: Fragment field selection
            dependencies: Set of other fragment names this fragment depends on
        """
        self.name = name
        self.on_type = on_type
        self.fields = fields.strip()
        self.dependencies = dependencies or set()

    def __str__(self) -> str:
        """Return the fragment definition."""
        return f"fragment {self.name} on {self.on_type} {{\n{self.fields}\n}}"

    def get_spread(self) -> str:
        """Return the fragment spread syntax."""
        return f"...{self.name}"


# Base fragments
BASE_FIELDS = GraphQLFragment(
    name="BaseFields",
    on_type="BaseModel",
    fields="""
    id
    createdAt
    updatedAt
    """,
)

PAGINATION_INFO = GraphQLFragment(
    name="PaginationInfo",
    on_type="PaginationInfo",
    fields="""
    page
    pageSize
    total
    hasNextPage
    hasPreviousPage
    """,
)

# Client fragments
CLIENT_CORE_FIELDS = GraphQLFragment(
    name="ClientCoreFields",
    on_type="Client",
    fields="""
    ...BaseFields
    name
    email
    phone
    status
    """,
    dependencies={"BaseFields"},
)

CLIENT_FULL_FIELDS = GraphQLFragment(
    name="ClientFullFields",
    on_type="Client",
    fields="""
    ...ClientCoreFields
    address
    billingAddress
    notes
    tags
    customFields
    """,
    dependencies={"ClientCoreFields"},
)

CLIENT_SUMMARY_FIELDS = GraphQLFragment(
    name="ClientSummaryFields",
    on_type="Client",
    fields="""
    id
    name
    email
    status
    """,
)

# Contact fragments
CONTACT_CORE_FIELDS = GraphQLFragment(
    name="ContactCoreFields",
    on_type="Contact",
    fields="""
    ...BaseFields
    clientId
    firstName
    lastName
    email
    phone
    isPrimary
    """,
    dependencies={"BaseFields"},
)

CONTACT_FULL_FIELDS = GraphQLFragment(
    name="ContactFullFields",
    on_type="Contact",
    fields="""
    ...ContactCoreFields
    title
    notes
    """,
    dependencies={"ContactCoreFields"},
)

# Site fragments
SITE_CORE_FIELDS = GraphQLFragment(
    name="SiteCoreFields",
    on_type="Site",
    fields="""
    ...BaseFields
    clientId
    name
    address
    """,
    dependencies={"BaseFields"},
)

SITE_FULL_FIELDS = GraphQLFragment(
    name="SiteFullFields",
    on_type="Site",
    fields="""
    ...SiteCoreFields
    description
    timezone
    notes
    """,
    dependencies={"SiteCoreFields"},
)

# Asset fragments
ASSET_CORE_FIELDS = GraphQLFragment(
    name="AssetCoreFields",
    on_type="Asset",
    fields="""
    ...BaseFields
    clientId
    siteId
    name
    assetType
    status
    """,
    dependencies={"BaseFields"},
)

ASSET_FULL_FIELDS = GraphQLFragment(
    name="AssetFullFields",
    on_type="Asset",
    fields="""
    ...AssetCoreFields
    manufacturer
    model
    serialNumber
    purchaseDate
    warrantyExpiry
    location
    notes
    customFields
    """,
    dependencies={"AssetCoreFields"},
)

ASSET_SUMMARY_FIELDS = GraphQLFragment(
    name="AssetSummaryFields",
    on_type="Asset",
    fields="""
    id
    name
    assetType
    status
    manufacturer
    model
    """,
)

# Ticket fragments
TICKET_CORE_FIELDS = GraphQLFragment(
    name="TicketCoreFields",
    on_type="Ticket",
    fields="""
    ...BaseFields
    clientId
    siteId
    assetId
    contactId
    title
    status
    priority
    assignedTo
    """,
    dependencies={"BaseFields"},
)

TICKET_FULL_FIELDS = GraphQLFragment(
    name="TicketFullFields",
    on_type="Ticket",
    fields="""
    ...TicketCoreFields
    description
    dueDate
    resolution
    timeSpent
    tags
    customFields
    """,
    dependencies={"TicketCoreFields"},
)

TICKET_SUMMARY_FIELDS = GraphQLFragment(
    name="TicketSummaryFields",
    on_type="Ticket",
    fields="""
    id
    title
    status
    priority
    assignedTo
    createdAt
    dueDate
    """,
)

TICKET_COMMENT_FIELDS = GraphQLFragment(
    name="TicketCommentFields",
    on_type="TicketComment",
    fields="""
    ...BaseFields
    ticketId
    authorId
    authorName
    content
    isInternal
    timeSpent
    """,
    dependencies={"BaseFields"},
)

# Task fragments
TASK_CORE_FIELDS = GraphQLFragment(
    name="TaskCoreFields",
    on_type="Task",
    fields="""
    ...BaseFields
    title
    description
    status
    priority
    projectId
    assignedTo
    assignedToTeam
    creatorId
    parentTaskId
    dueDate
    startDate
    """,
    dependencies={"BaseFields"},
)

TASK_FULL_FIELDS = GraphQLFragment(
    name="TaskFullFields",
    on_type="Task",
    fields="""
    ...TaskCoreFields
    subtaskCount
    completedAt
    estimatedHours
    actualHours
    recurrenceType
    recurrenceInterval
    recurrenceEndDate
    parentRecurringTaskId
    timeEntriesCount
    totalTimeLogged
    billableTime
    labels
    tags
    customFields
    progressPercentage
    isMilestone
    isTemplate
    templateId
    attachmentCount
    commentCount
    overdueAlertSent
    reminderSent
    """,
    dependencies={"TaskCoreFields"},
)

TASK_SUMMARY_FIELDS = GraphQLFragment(
    name="TaskSummaryFields",
    on_type="Task",
    fields="""
    id
    title
    status
    priority
    assignedTo
    dueDate
    progressPercentage
    createdAt
    updatedAt
    """,
)

TASK_COMMENT_FIELDS = GraphQLFragment(
    name="TaskCommentFields",
    on_type="TaskComment",
    fields="""
    ...BaseFields
    taskId
    authorId
    authorName
    content
    isInternal
    timeLogged
    """,
    dependencies={"BaseFields"},
)

TASK_TIME_ENTRY_FIELDS = GraphQLFragment(
    name="TaskTimeEntryFields",
    on_type="TaskTimeEntry",
    fields="""
    ...BaseFields
    taskId
    userId
    userName
    hours
    description
    dateLogged
    isBillable
    hourlyRate
    """,
    dependencies={"BaseFields"},
)

TASK_TEMPLATE_FIELDS = GraphQLFragment(
    name="TaskTemplateFields",
    on_type="TaskTemplate",
    fields="""
    ...BaseFields
    name
    description
    defaultPriority
    estimatedHours
    defaultAssigneeId
    defaultTags
    defaultCustomFields
    checklistItems
    """,
    dependencies={"BaseFields"},
)

# Knowledge Base fragments
KB_COLLECTION_CORE_FIELDS = GraphQLFragment(
    name="KBCollectionCoreFields",
    on_type="KnowledgeBaseCollection",
    fields="""
    ...BaseFields
    name
    description
    parentId
    isPublic
    """,
    dependencies={"BaseFields"},
)

KB_COLLECTION_FULL_FIELDS = GraphQLFragment(
    name="KBCollectionFullFields",
    on_type="KnowledgeBaseCollection",
    fields="""
    ...KBCollectionCoreFields
    articleCount
    """,
    dependencies={"KBCollectionCoreFields"},
)

KB_ARTICLE_CORE_FIELDS = GraphQLFragment(
    name="KBArticleCoreFields",
    on_type="KnowledgeBaseArticle",
    fields="""
    ...BaseFields
    collectionId
    title
    summary
    authorId
    authorName
    isPublished
    isFeatured
    """,
    dependencies={"BaseFields"},
)

KB_ARTICLE_FULL_FIELDS = GraphQLFragment(
    name="KBArticleFullFields",
    on_type="KnowledgeBaseArticle",
    fields="""
    ...KBArticleCoreFields
    content
    viewCount
    tags
    """,
    dependencies={"KBArticleCoreFields"},
)

KB_ARTICLE_SUMMARY_FIELDS = GraphQLFragment(
    name="KBArticleSummaryFields",
    on_type="KnowledgeBaseArticle",
    fields="""
    id
    title
    summary
    authorName
    isPublished
    viewCount
    createdAt
    updatedAt
    """,
)


# Fragment collections for easy access
ALL_FRAGMENTS = {
    fragment.name: fragment
    for fragment in [
        BASE_FIELDS,
        PAGINATION_INFO,
        CLIENT_CORE_FIELDS,
        CLIENT_FULL_FIELDS,
        CLIENT_SUMMARY_FIELDS,
        CONTACT_CORE_FIELDS,
        CONTACT_FULL_FIELDS,
        SITE_CORE_FIELDS,
        SITE_FULL_FIELDS,
        ASSET_CORE_FIELDS,
        ASSET_FULL_FIELDS,
        ASSET_SUMMARY_FIELDS,
        TICKET_CORE_FIELDS,
        TICKET_FULL_FIELDS,
        TICKET_SUMMARY_FIELDS,
        TICKET_COMMENT_FIELDS,
        TASK_CORE_FIELDS,
        TASK_FULL_FIELDS,
        TASK_SUMMARY_FIELDS,
        TASK_COMMENT_FIELDS,
        TASK_TIME_ENTRY_FIELDS,
        TASK_TEMPLATE_FIELDS,
        KB_COLLECTION_CORE_FIELDS,
        KB_COLLECTION_FULL_FIELDS,
        KB_ARTICLE_CORE_FIELDS,
        KB_ARTICLE_FULL_FIELDS,
        KB_ARTICLE_SUMMARY_FIELDS,
    ]
}

CLIENT_FRAGMENTS = {
    "core": CLIENT_CORE_FIELDS,
    "full": CLIENT_FULL_FIELDS,
    "summary": CLIENT_SUMMARY_FIELDS,
}

CONTACT_FRAGMENTS = {
    "core": CONTACT_CORE_FIELDS,
    "full": CONTACT_FULL_FIELDS,
}

SITE_FRAGMENTS = {
    "core": SITE_CORE_FIELDS,
    "full": SITE_FULL_FIELDS,
}

ASSET_FRAGMENTS = {
    "core": ASSET_CORE_FIELDS,
    "full": ASSET_FULL_FIELDS,
    "summary": ASSET_SUMMARY_FIELDS,
}

TICKET_FRAGMENTS = {
    "core": TICKET_CORE_FIELDS,
    "full": TICKET_FULL_FIELDS,
    "summary": TICKET_SUMMARY_FIELDS,
    "comment": TICKET_COMMENT_FIELDS,
}

TASK_FRAGMENTS = {
    "core": TASK_CORE_FIELDS,
    "full": TASK_FULL_FIELDS,
    "summary": TASK_SUMMARY_FIELDS,
    "comment": TASK_COMMENT_FIELDS,
    "time_entry": TASK_TIME_ENTRY_FIELDS,
    "template": TASK_TEMPLATE_FIELDS,
}

KB_FRAGMENTS = {
    "collection_core": KB_COLLECTION_CORE_FIELDS,
    "collection_full": KB_COLLECTION_FULL_FIELDS,
    "article_core": KB_ARTICLE_CORE_FIELDS,
    "article_full": KB_ARTICLE_FULL_FIELDS,
    "article_summary": KB_ARTICLE_SUMMARY_FIELDS,
}


def resolve_dependencies(fragment_names: Set[str]) -> Set[str]:
    """Resolve fragment dependencies to get all required fragments.

    Args:
        fragment_names: Set of fragment names to resolve

    Returns:
        Set of all fragment names including dependencies
    """
    resolved = set()
    to_resolve = set(fragment_names)

    while to_resolve:
        current = to_resolve.pop()
        if current in resolved:
            continue

        resolved.add(current)

        if current in ALL_FRAGMENTS:
            dependencies = ALL_FRAGMENTS[current].dependencies
            to_resolve.update(dep for dep in dependencies if dep not in resolved)

    return resolved


def build_fragments_string(fragment_names: Set[str]) -> str:
    """Build a string containing all required fragment definitions.

    Args:
        fragment_names: Set of fragment names to include

    Returns:
        String containing all fragment definitions
    """
    resolved_names = resolve_dependencies(fragment_names)

    # Sort to ensure consistent output
    sorted_names = sorted(resolved_names)

    fragments = []
    for name in sorted_names:
        if name in ALL_FRAGMENTS:
            fragments.append(str(ALL_FRAGMENTS[name]))

    return "\n\n".join(fragments)


def get_fragment_spreads(fragment_names: Set[str]) -> str:
    """Get fragment spreads for use in queries.

    Args:
        fragment_names: Set of fragment names

    Returns:
        String containing fragment spreads
    """
    spreads = []
    for name in sorted(fragment_names):
        if name in ALL_FRAGMENTS:
            spreads.append(ALL_FRAGMENTS[name].get_spread())

    return "\n".join(spreads)


def create_query_with_fragments(query: str, fragment_names: Set[str]) -> str:
    """Create a complete GraphQL query with fragments.

    Args:
        query: The main query string
        fragment_names: Set of fragment names to include

    Returns:
        Complete GraphQL query with fragment definitions
    """
    fragments_string = build_fragments_string(fragment_names)

    if fragments_string:
        return f"{query}\n\n{fragments_string}"
    else:
        return query


# Convenience functions for common fragment combinations
def get_client_fields(detail_level: str = "core") -> Set[str]:
    """Get client fragment names for specified detail level.

    Args:
        detail_level: Level of detail (summary, core, full)

    Returns:
        Set of fragment names
    """
    mapping = {
        "summary": {"ClientSummaryFields"},
        "core": {"ClientCoreFields"},
        "full": {"ClientFullFields"},
    }
    return mapping.get(detail_level, {"ClientCoreFields"})


def get_ticket_fields(detail_level: str = "core", include_comments: bool = False) -> Set[str]:
    """Get ticket fragment names for specified detail level.

    Args:
        detail_level: Level of detail (summary, core, full)
        include_comments: Whether to include comment fields

    Returns:
        Set of fragment names
    """
    mapping = {
        "summary": {"TicketSummaryFields"},
        "core": {"TicketCoreFields"},
        "full": {"TicketFullFields"},
    }

    fragments = mapping.get(detail_level, {"TicketCoreFields"})

    if include_comments:
        fragments.add("TicketCommentFields")

    return fragments


def get_asset_fields(detail_level: str = "core") -> Set[str]:
    """Get asset fragment names for specified detail level.

    Args:
        detail_level: Level of detail (summary, core, full)

    Returns:
        Set of fragment names
    """
    mapping = {
        "summary": {"AssetSummaryFields"},
        "core": {"AssetCoreFields"},
        "full": {"AssetFullFields"},
    }
    return mapping.get(detail_level, {"AssetCoreFields"})


def get_task_fields(
    detail_level: str = "core",
    include_comments: bool = False,
    include_time_entries: bool = False,
    include_template: bool = False,
) -> Set[str]:
    """Get task fragment names for specified detail level.

    Args:
        detail_level: Level of detail (summary, core, full)
        include_comments: Whether to include comment fields
        include_time_entries: Whether to include time entry fields
        include_template: Whether to include template fields

    Returns:
        Set of fragment names
    """
    mapping = {
        "summary": {"TaskSummaryFields"},
        "core": {"TaskCoreFields"},
        "full": {"TaskFullFields"},
    }

    fragments = mapping.get(detail_level, {"TaskCoreFields"})

    if include_comments:
        fragments.add("TaskCommentFields")

    if include_time_entries:
        fragments.add("TaskTimeEntryFields")

    if include_template:
        fragments.add("TaskTemplateFields")

    return fragments


def get_kb_fields(collection_detail: str = "core", article_detail: str = "core") -> Set[str]:
    """Get knowledge base fragment names for specified detail levels.

    Args:
        collection_detail: Level of detail for collections (core, full)
        article_detail: Level of detail for articles (summary, core, full)

    Returns:
        Set of fragment names
    """
    collection_mapping = {
        "core": "KBCollectionCoreFields",
        "full": "KBCollectionFullFields",
    }

    article_mapping = {
        "summary": "KBArticleSummaryFields",
        "core": "KBArticleCoreFields",
        "full": "KBArticleFullFields",
    }

    fragments = set()

    if collection_detail in collection_mapping:
        fragments.add(collection_mapping[collection_detail])

    if article_detail in article_mapping:
        fragments.add(article_mapping[article_detail])

    return fragments
