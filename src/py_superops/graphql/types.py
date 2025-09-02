# # Copyright (c) 2024 SuperOps Team
# # Licensed under the MIT License.
# # See LICENSE file in the project root for full license information.

"""GraphQL type definitions and response models for SuperOps API.

This module provides type-safe models for GraphQL queries, mutations, and responses,
enabling better IDE support and runtime validation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict, Union
from uuid import UUID


# Base Types
class GraphQLResponse(TypedDict, total=False):
    """Base GraphQL response structure."""

    data: Optional[Dict[str, Any]]
    errors: Optional[List[Dict[str, Any]]]
    extensions: Optional[Dict[str, Any]]


class PaginationInfo(TypedDict):
    """Pagination information for GraphQL queries."""

    page: int
    pageSize: int
    total: int
    hasNextPage: bool
    hasPreviousPage: bool


# Enums
class TicketStatus(str, Enum):
    """Ticket status enumeration."""

    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class TicketPriority(str, Enum):
    """Ticket priority enumeration."""

    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"
    CRITICAL = "CRITICAL"


class AssetStatus(str, Enum):
    """Asset status enumeration."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    RETIRED = "RETIRED"
    UNDER_MAINTENANCE = "UNDER_MAINTENANCE"


class ClientStatus(str, Enum):
    """Client status enumeration."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class TaskStatus(str, Enum):
    """Task status enumeration."""

    NEW = "NEW"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    ON_HOLD = "ON_HOLD"
    UNDER_REVIEW = "UNDER_REVIEW"


class TaskPriority(str, Enum):
    """Task priority enumeration."""

    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"
    CRITICAL = "CRITICAL"


class TaskRecurrenceType(str, Enum):
    """Task recurrence type enumeration."""

    NONE = "NONE"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"
    CUSTOM = "CUSTOM"


# Base Models
@dataclass
class BaseModel:
    """Base model with common fields."""

    id: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BaseModel:
        """Create instance from dictionary."""
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert instance to dictionary."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, Enum):
                result[key] = value.value
            else:
                result[key] = value
        return result


# Client Types
@dataclass
class Client(BaseModel):
    """Client/Customer model."""

    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    status: ClientStatus = ClientStatus.ACTIVE
    billing_address: Optional[str] = None
    notes: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Contact(BaseModel):
    """Contact model."""

    client_id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    title: Optional[str] = None
    is_primary: bool = False
    notes: Optional[str] = None


@dataclass
class Site(BaseModel):
    """Site model."""

    client_id: str
    name: str
    address: Optional[str] = None
    description: Optional[str] = None
    timezone: Optional[str] = None
    notes: Optional[str] = None


# Asset Types
@dataclass
class Asset(BaseModel):
    """Asset model."""

    client_id: str
    name: str
    site_id: Optional[str] = None
    asset_type: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    status: AssetStatus = AssetStatus.ACTIVE
    purchase_date: Optional[datetime] = None
    warranty_expiry: Optional[datetime] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    custom_fields: Dict[str, Any] = field(default_factory=dict)


# Ticket Types
@dataclass
class Ticket(BaseModel):
    """Ticket model."""

    client_id: str
    title: str
    site_id: Optional[str] = None
    asset_id: Optional[str] = None
    contact_id: Optional[str] = None
    description: Optional[str] = None
    status: TicketStatus = TicketStatus.OPEN
    priority: TicketPriority = TicketPriority.NORMAL
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    resolution: Optional[str] = None
    time_spent: Optional[int] = None  # minutes
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TicketComment(BaseModel):
    """Ticket comment model."""

    ticket_id: str
    author_id: str
    author_name: str
    content: str
    is_internal: bool = False
    time_spent: Optional[int] = None  # minutes


# Knowledge Base Types
@dataclass
class KnowledgeBaseCollection(BaseModel):
    """Knowledge base collection model."""

    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    is_public: bool = False
    article_count: int = 0


@dataclass
class KnowledgeBaseArticle(BaseModel):
    """Knowledge base article model."""

    collection_id: str
    title: str
    content: str
    author_id: str
    author_name: str
    summary: Optional[str] = None
    is_published: bool = False
    is_featured: bool = False
    view_count: int = 0
    tags: List[str] = field(default_factory=list)


# Task Types
@dataclass
class Task(BaseModel):
    """Task model."""

    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.NEW
    priority: TaskPriority = TaskPriority.NORMAL

    # Project linking - tasks can be standalone or linked to projects
    project_id: Optional[str] = None

    # Assignment and delegation
    assigned_to: Optional[str] = None
    assigned_to_team: Optional[str] = None
    creator_id: Optional[str] = None

    # Hierarchy support
    parent_task_id: Optional[str] = None
    subtask_count: int = 0

    # Due dates and scheduling
    due_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None

    # Recurring task support
    recurrence_type: TaskRecurrenceType = TaskRecurrenceType.NONE
    recurrence_interval: Optional[int] = None  # e.g., every 2 weeks
    recurrence_end_date: Optional[datetime] = None
    parent_recurring_task_id: Optional[str] = None

    # Time tracking
    time_entries_count: int = 0
    total_time_logged: Optional[float] = None  # hours
    billable_time: Optional[float] = None  # hours

    # Categorization and metadata
    labels: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)

    # Additional metadata
    progress_percentage: Optional[int] = None  # 0-100
    is_milestone: bool = False
    is_template: bool = False
    template_id: Optional[str] = None

    # Attachments and links
    attachment_count: int = 0
    comment_count: int = 0

    # Alert settings
    overdue_alert_sent: bool = False
    reminder_sent: bool = False


@dataclass
class TaskComment(BaseModel):
    """Task comment model."""

    task_id: str
    author_id: str
    author_name: str
    content: str
    is_internal: bool = False
    time_logged: Optional[float] = None  # hours logged with this comment


@dataclass
class TaskTimeEntry(BaseModel):
    """Task time entry model."""

    task_id: str
    user_id: str
    user_name: str
    hours: float
    date_logged: datetime
    description: Optional[str] = None
    is_billable: bool = True
    hourly_rate: Optional[float] = None


@dataclass
class TaskTemplate(BaseModel):
    """Task template model."""

    name: str
    description: Optional[str] = None
    default_priority: TaskPriority = TaskPriority.NORMAL
    estimated_hours: Optional[float] = None
    default_assignee_id: Optional[str] = None
    default_tags: List[str] = field(default_factory=list)
    default_custom_fields: Dict[str, Any] = field(default_factory=dict)
    checklist_items: List[str] = field(default_factory=list)


# Query Filter Types
@dataclass
class ClientFilter:
    """Client query filter."""

    name: Optional[str] = None
    email: Optional[str] = None
    status: Optional[ClientStatus] = None
    tags: Optional[List[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


@dataclass
class TicketFilter:
    """Ticket query filter."""

    client_id: Optional[str] = None
    site_id: Optional[str] = None
    asset_id: Optional[str] = None
    contact_id: Optional[str] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    assigned_to: Optional[str] = None
    tags: Optional[List[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    due_after: Optional[datetime] = None
    due_before: Optional[datetime] = None


@dataclass
class AssetFilter:
    """Asset query filter."""

    client_id: Optional[str] = None
    site_id: Optional[str] = None
    name: Optional[str] = None
    asset_type: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    status: Optional[AssetStatus] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


@dataclass
class TaskFilter:
    """Task query filter."""

    # Basic filtering
    title: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None

    # Project and hierarchy
    project_id: Optional[str] = None
    parent_task_id: Optional[str] = None
    is_subtask: Optional[bool] = None  # has parent_task_id
    is_parent: Optional[bool] = None  # has subtasks

    # Assignment
    assigned_to: Optional[str] = None
    assigned_to_team: Optional[str] = None
    creator_id: Optional[str] = None
    unassigned: Optional[bool] = None

    # Date filtering
    due_after: Optional[datetime] = None
    due_before: Optional[datetime] = None
    start_after: Optional[datetime] = None
    start_before: Optional[datetime] = None
    completed_after: Optional[datetime] = None
    completed_before: Optional[datetime] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None

    # Status filtering
    is_overdue: Optional[bool] = None
    is_completed: Optional[bool] = None
    is_active: Optional[bool] = None  # not completed or cancelled

    # Recurring tasks
    recurrence_type: Optional[TaskRecurrenceType] = None
    is_recurring: Optional[bool] = None
    is_recurring_instance: Optional[bool] = None

    # Metadata
    tags: Optional[List[str]] = None
    labels: Optional[List[str]] = None
    is_milestone: Optional[bool] = None
    is_template: Optional[bool] = None
    template_id: Optional[str] = None

    # Time tracking
    has_time_entries: Optional[bool] = None
    estimated_hours_min: Optional[float] = None
    estimated_hours_max: Optional[float] = None
    actual_hours_min: Optional[float] = None
    actual_hours_max: Optional[float] = None


# Pagination Types
@dataclass
class PaginationArgs:
    """Pagination arguments."""

    page: int = 1
    pageSize: int = 50

    def __post_init__(self):
        """Validate pagination arguments."""
        if self.page < 1:
            raise ValueError("Page must be >= 1")
        if self.pageSize < 1 or self.pageSize > 1000:
            raise ValueError("Page size must be between 1 and 1000")


@dataclass
class SortArgs:
    """Sort arguments."""

    field: str
    direction: str = "ASC"  # ASC or DESC

    def __post_init__(self):
        """Validate sort arguments."""
        if self.direction not in ("ASC", "DESC"):
            raise ValueError("Direction must be ASC or DESC")


# Response Types
@dataclass
class PaginatedResponse:
    """Base paginated response."""

    items: List[Any]
    pagination: PaginationInfo

    @classmethod
    def from_graphql_response(
        cls, data: Dict[str, Any], item_type: type, items_key: str = "items"
    ) -> PaginatedResponse:
        """Create paginated response from GraphQL data."""
        items_data = data.get(items_key, [])
        items = [
            item_type.from_dict(item) if hasattr(item_type, "from_dict") else item
            for item in items_data
        ]

        pagination = data.get("pagination", {})

        return cls(items=items, pagination=pagination)


@dataclass
class ClientsResponse(PaginatedResponse):
    """Clients query response."""

    items: List[Client]


@dataclass
class TicketsResponse(PaginatedResponse):
    """Tickets query response."""

    items: List[Ticket]


@dataclass
class AssetsResponse(PaginatedResponse):
    """Assets query response."""

    items: List[Asset]


@dataclass
class ContactsResponse(PaginatedResponse):
    """Contacts query response."""

    items: List[Contact]


@dataclass
class SitesResponse(PaginatedResponse):
    """Sites query response."""

    items: List[Site]


@dataclass
class KnowledgeBaseCollectionsResponse(PaginatedResponse):
    """Knowledge base collections query response."""

    items: List[KnowledgeBaseCollection]


@dataclass
class KnowledgeBaseArticlesResponse(PaginatedResponse):
    """Knowledge base articles query response."""

    items: List[KnowledgeBaseArticle]


@dataclass
class TasksResponse(PaginatedResponse):
    """Tasks query response."""

    items: List[Task]


@dataclass
class TaskCommentsResponse(PaginatedResponse):
    """Task comments query response."""

    items: List[TaskComment]


@dataclass
class TaskTimeEntriesResponse(PaginatedResponse):
    """Task time entries query response."""

    items: List[TaskTimeEntry]


@dataclass
class TaskTemplatesResponse(PaginatedResponse):
    """Task templates query response."""

    items: List[TaskTemplate]


# Mutation Input Types
@dataclass
class ClientInput:
    """Client creation/update input."""

    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    status: Optional[ClientStatus] = None
    billing_address: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


@dataclass
class TicketInput:
    """Ticket creation/update input."""

    client_id: str
    title: str
    site_id: Optional[str] = None
    asset_id: Optional[str] = None
    contact_id: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


@dataclass
class AssetInput:
    """Asset creation/update input."""

    client_id: str
    name: str
    site_id: Optional[str] = None
    asset_type: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    status: Optional[AssetStatus] = None
    purchase_date: Optional[datetime] = None
    warranty_expiry: Optional[datetime] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None


@dataclass
class ContactInput:
    """Contact creation/update input."""

    client_id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    title: Optional[str] = None
    is_primary: Optional[bool] = None
    notes: Optional[str] = None


@dataclass
class SiteInput:
    """Site creation/update input."""

    client_id: str
    name: str
    address: Optional[str] = None
    description: Optional[str] = None
    timezone: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class KnowledgeBaseCollectionInput:
    """Knowledge base collection creation/update input."""

    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    is_public: Optional[bool] = None


@dataclass
class KnowledgeBaseArticleInput:
    """Knowledge base article creation/update input."""

    collection_id: str
    title: str
    content: str
    summary: Optional[str] = None
    is_published: Optional[bool] = None
    is_featured: Optional[bool] = None
    tags: Optional[List[str]] = None


@dataclass
class TaskInput:
    """Task creation/update input."""

    title: str
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None

    # Project linking
    project_id: Optional[str] = None

    # Assignment
    assigned_to: Optional[str] = None
    assigned_to_team: Optional[str] = None

    # Hierarchy
    parent_task_id: Optional[str] = None

    # Scheduling
    due_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None

    # Recurring tasks
    recurrence_type: Optional[TaskRecurrenceType] = None
    recurrence_interval: Optional[int] = None
    recurrence_end_date: Optional[datetime] = None

    # Metadata
    labels: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    progress_percentage: Optional[int] = None
    is_milestone: Optional[bool] = None

    # Template
    template_id: Optional[str] = None


@dataclass
class TaskCommentInput:
    """Task comment creation input."""

    task_id: str
    content: str
    is_internal: Optional[bool] = None
    time_logged: Optional[float] = None


@dataclass
class TaskTimeEntryInput:
    """Task time entry creation input."""

    task_id: str
    hours: float
    description: Optional[str] = None
    date_logged: Optional[datetime] = None
    is_billable: Optional[bool] = None
    hourly_rate: Optional[float] = None


@dataclass
class TaskTemplateInput:
    """Task template creation/update input."""

    name: str
    description: Optional[str] = None
    default_priority: Optional[TaskPriority] = None
    estimated_hours: Optional[float] = None
    default_assignee_id: Optional[str] = None
    default_tags: Optional[List[str]] = None
    default_custom_fields: Optional[Dict[str, Any]] = None
    checklist_items: Optional[List[str]] = None


@dataclass
class TaskStatusUpdateInput:
    """Task status update input for workflow operations."""

    status: TaskStatus
    comment: Optional[str] = None
    time_logged: Optional[float] = None


@dataclass
class TaskAssignmentInput:
    """Task assignment input."""

    assigned_to: Optional[str] = None
    assigned_to_team: Optional[str] = None
    notify_assignee: Optional[bool] = True
    comment: Optional[str] = None


@dataclass
class TaskRecurrenceInput:
    """Task recurrence configuration input."""

    recurrence_type: TaskRecurrenceType
    recurrence_interval: Optional[int] = None
    recurrence_end_date: Optional[datetime] = None
    recurrence_count: Optional[int] = None  # end after N occurrences


# Utility Functions
def convert_datetime_to_iso(dt: Optional[datetime]) -> Optional[str]:
    """Convert datetime to ISO string."""
    return dt.isoformat() if dt else None


def convert_iso_to_datetime(iso_string: Optional[str]) -> Optional[datetime]:
    """Convert ISO string to datetime."""
    if not iso_string:
        return None
    try:
        return datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
    except ValueError:
        return None


def serialize_filter_value(value: Any) -> Any:
    """Serialize filter value for GraphQL variables."""
    if isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, Enum):
        return value.value
    elif isinstance(value, list):
        return [serialize_filter_value(item) for item in value]
    elif isinstance(value, dict):
        return {k: serialize_filter_value(v) for k, v in value.items()}
    else:
        return value


def snake_to_camel(snake_str: str) -> str:
    """Convert snake_case to camelCase."""
    components = snake_str.split("_")
    return components[0] + "".join(word.capitalize() for word in components[1:])


def serialize_input(input_obj: Any) -> Dict[str, Any]:
    """Serialize input object for GraphQL variables."""
    if hasattr(input_obj, "__dict__"):
        result = {}
        for key, value in input_obj.__dict__.items():
            if value is not None:
                # Convert snake_case to camelCase for GraphQL
                camel_key = snake_to_camel(key)
                result[camel_key] = serialize_filter_value(value)
        return result
    else:
        return serialize_filter_value(input_obj)
