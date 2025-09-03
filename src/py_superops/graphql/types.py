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
from typing import Any, Dict, List, Optional, TypedDict


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


class ProjectStatus(str, Enum):
    """Project status enumeration."""

    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    ON_HOLD = "ON_HOLD"


class TaskStatus(str, Enum):
    """Task status enumeration."""

    NEW = "NEW"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    ON_HOLD = "ON_HOLD"
    UNDER_REVIEW = "UNDER_REVIEW"


class ProjectPriority(str, Enum):
    """Project priority enumeration."""

    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"
    CRITICAL = "CRITICAL"


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


class ContractStatus(str, Enum):
    """Contract status enumeration."""

    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    SUSPENDED = "SUSPENDED"
    RENEWAL_PENDING = "RENEWAL_PENDING"


class ContractType(str, Enum):
    """Contract type enumeration."""

    SERVICE_AGREEMENT = "SERVICE_AGREEMENT"
    MAINTENANCE_CONTRACT = "MAINTENANCE_CONTRACT"
    PROJECT_BASED = "PROJECT_BASED"
    SUPPORT_CONTRACT = "SUPPORT_CONTRACT"
    MSP_CONTRACT = "MSP_CONTRACT"


class BillingCycle(str, Enum):
    """Billing cycle enumeration."""

    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    SEMI_ANNUAL = "SEMI_ANNUAL"
    ANNUAL = "ANNUAL"
    ONE_TIME = "ONE_TIME"


class SLALevel(str, Enum):
    """SLA level enumeration."""

    BASIC = "BASIC"
    STANDARD = "STANDARD"
    PREMIUM = "PREMIUM"
    ENTERPRISE = "ENTERPRISE"
    CUSTOM = "CUSTOM"


class UserRole(str, Enum):
    """User role enumeration."""

    ADMIN = "ADMIN"
    TECHNICIAN = "TECHNICIAN"
    USER = "USER"
    MANAGER = "MANAGER"
    READONLY = "READONLY"
    BILLING = "BILLING"
    DISPATCHER = "DISPATCHER"


class UserStatus(str, Enum):
    """User status enumeration."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    PENDING = "PENDING"


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


# Project Types
@dataclass
class Project(BaseModel):
    """Project model."""

    client_id: str
    name: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.OPEN
    priority: ProjectPriority = ProjectPriority.NORMAL
    contract_id: Optional[str] = None
    site_id: Optional[str] = None
    assigned_to: Optional[str] = None
    manager_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    budget: Optional[float] = None
    billing_rate: Optional[float] = None
    progress_percentage: Optional[int] = None  # 0-100
    estimated_hours: Optional[int] = None
    actual_hours: Optional[int] = None
    notes: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectMilestone(BaseModel):
    """Project milestone model."""

    project_id: str
    name: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    is_completed: bool = False
    progress_percentage: Optional[int] = None  # 0-100
    order_index: int = 0
    notes: Optional[str] = None


@dataclass
class ProjectTask(BaseModel):
    """Project task model."""

    # Required fields first
    project_id: str
    name: str
    
    # Optional fields with defaults
    milestone_id: Optional[str] = None
    description: Optional[str] = None
    status: TicketStatus = TicketStatus.OPEN
    priority: TicketPriority = TicketPriority.NORMAL
    assigned_to: Optional[str] = None
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    estimated_hours: Optional[int] = None
    actual_hours: Optional[int] = None
    progress_percentage: Optional[int] = None  # 0-100
    order_index: int = 0
    notes: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class ProjectTimeEntry(BaseModel):
    """Project time entry model."""

    # Required fields first
    project_id: str
    user_id: str
    user_name: str
    description: str
    hours: float
    start_time: datetime
    
    # Optional fields with defaults
    task_id: Optional[str] = None
    billable_hours: Optional[float] = None
    rate: Optional[float] = None
    end_time: Optional[datetime] = None
    is_billable: bool = True
    notes: Optional[str] = None


# User Types
@dataclass
class User(BaseModel):
    """User model."""

    # Required fields first (from BaseModel and User-specific)
    email: str
    first_name: str
    last_name: str
    role: UserRole
    
    # Optional fields with defaults
    status: UserStatus = UserStatus.ACTIVE
    department: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    job_title: Optional[str] = None
    is_technician: bool = False
    hourly_rate: Optional[float] = None
    last_login_time: Optional[datetime] = None
    last_login: Optional[str] = None  # Alternative field name for compatibility
    timezone: Optional[str] = None
    language: Optional[str] = None
    avatar_url: Optional[str] = None
    is_primary: bool = False
    is_active_session: bool = False
    employee_id: Optional[str] = None
    hire_date: Optional[str] = None
    manager_id: Optional[str] = None
    notification_preferences: Dict[str, Any] = field(default_factory=dict)
    permissions: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)

    @property
    def full_name(self) -> str:
        """Get full name."""
        return f"{self.first_name} {self.last_name}".strip()


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


# Contract Types
@dataclass
class ContractSLA(BaseModel):
    """Contract SLA model."""

    contract_id: str
    level: SLALevel
    response_time_minutes: Optional[int] = None
    resolution_time_hours: Optional[int] = None
    availability_percentage: Optional[float] = None
    description: Optional[str] = None
    penalties: Optional[str] = None


@dataclass
class ContractRate(BaseModel):
    """Contract billing rate model."""

    contract_id: str
    service_type: str
    rate_type: str  # HOURLY, FIXED, TIERED
    rate_amount: float
    currency: str = "USD"
    description: Optional[str] = None
    effective_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


@dataclass
class Contract(BaseModel):
    """Contract model."""

    client_id: str
    name: str
    contract_number: str
    contract_type: ContractType
    start_date: datetime
    status: ContractStatus = ContractStatus.DRAFT
    end_date: Optional[datetime] = None
    renewal_date: Optional[datetime] = None
    auto_renew: bool = False
    billing_cycle: BillingCycle = BillingCycle.MONTHLY
    contract_value: Optional[float] = None
    currency: str = "USD"
    description: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    renewal_terms: Optional[str] = None
    cancellation_terms: Optional[str] = None
    signed_by_client: Optional[str] = None
    signed_by_provider: Optional[str] = None
    signed_date: Optional[datetime] = None
    notification_days: int = 30
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    # Related data
    slas: List[ContractSLA] = field(default_factory=list)
    rates: List[ContractRate] = field(default_factory=list)


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
class ProjectFilter:
    """Project query filter."""

    client_id: Optional[str] = None
    contract_id: Optional[str] = None
    site_id: Optional[str] = None
    name: Optional[str] = None
    status: Optional[ProjectStatus] = None
    priority: Optional[ProjectPriority] = None
    assigned_to: Optional[str] = None
    manager_id: Optional[str] = None
    tags: Optional[List[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    start_after: Optional[datetime] = None
    start_before: Optional[datetime] = None
    due_after: Optional[datetime] = None
    due_before: Optional[datetime] = None


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


@dataclass
class UserFilter:
    """User query filter."""

    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    department: Optional[str] = None
    job_title: Optional[str] = None
    is_technician: Optional[bool] = None
    is_primary: Optional[bool] = None
    tags: Optional[List[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    last_login_after: Optional[datetime] = None
    last_login_before: Optional[datetime] = None


@dataclass
class ContractFilter:
    """Contract query filter."""

    client_id: Optional[str] = None
    name: Optional[str] = None
    contract_number: Optional[str] = None
    contract_type: Optional[ContractType] = None
    status: Optional[ContractStatus] = None
    billing_cycle: Optional[BillingCycle] = None
    auto_renew: Optional[bool] = None
    start_date_after: Optional[datetime] = None
    start_date_before: Optional[datetime] = None
    end_date_after: Optional[datetime] = None
    end_date_before: Optional[datetime] = None
    renewal_date_after: Optional[datetime] = None
    renewal_date_before: Optional[datetime] = None
    value_min: Optional[float] = None
    value_max: Optional[float] = None
    tags: Optional[List[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


# Pagination Types
@dataclass
class PaginationArgs:
    """Pagination arguments."""

    page: int = 1
    pageSize: int = 50

    def __post_init__(self) -> None:
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

    def __post_init__(self) -> None:
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
class ProjectsResponse(PaginatedResponse):
    """Projects query response."""

    items: List[Project]


@dataclass
class ProjectMilestonesResponse(PaginatedResponse):
    """Project milestones query response."""

    items: List[ProjectMilestone]


@dataclass
class ProjectTasksResponse(PaginatedResponse):
    """Project tasks query response."""

    items: List[ProjectTask]


@dataclass
class ProjectTimeEntriesResponse(PaginatedResponse):
    """Project time entries query response."""

    items: List[ProjectTimeEntry]


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


@dataclass
class ContractsResponse(PaginatedResponse):
    """Contracts query response."""

    items: List[Contract]


@dataclass
class ContractSLAsResponse(PaginatedResponse):
    """Contract SLAs query response."""

    items: List[ContractSLA]


@dataclass
class ContractRatesResponse(PaginatedResponse):
    """Contract rates query response."""

    items: List[ContractRate]


@dataclass
class UsersResponse(PaginatedResponse):
    """Users query response."""

    items: List[User]


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
class ProjectInput:
    """Project creation/update input."""

    client_id: str
    name: str
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    priority: Optional[ProjectPriority] = None
    contract_id: Optional[str] = None
    site_id: Optional[str] = None
    assigned_to: Optional[str] = None
    manager_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    budget: Optional[float] = None
    billing_rate: Optional[float] = None
    progress_percentage: Optional[int] = None
    estimated_hours: Optional[int] = None
    notes: Optional[str] = None


@dataclass
class ContractSLAInput:
    """Contract SLA creation/update input."""

    contract_id: str
    level: SLALevel
    response_time_minutes: Optional[int] = None
    resolution_time_hours: Optional[int] = None
    availability_percentage: Optional[float] = None
    description: Optional[str] = None
    penalties: Optional[str] = None


@dataclass
class ContractRateInput:
    """Contract rate creation/update input."""

    contract_id: str
    service_type: str
    rate_type: str
    rate_amount: float
    currency: Optional[str] = None
    description: Optional[str] = None
    effective_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


@dataclass
class ContractInput:
    """Contract creation/update input."""

    client_id: str
    name: str
    contract_type: ContractType
    start_date: datetime
    contract_number: Optional[str] = None
    status: Optional[ContractStatus] = None
    end_date: Optional[datetime] = None
    renewal_date: Optional[datetime] = None
    auto_renew: Optional[bool] = None
    billing_cycle: Optional[BillingCycle] = None
    contract_value: Optional[float] = None
    currency: Optional[str] = None
    description: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    renewal_terms: Optional[str] = None
    cancellation_terms: Optional[str] = None
    signed_by_client: Optional[str] = None
    signed_by_provider: Optional[str] = None
    signed_date: Optional[datetime] = None
    notification_days: Optional[int] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


@dataclass
class ProjectMilestoneInput:
    """Project milestone creation/update input."""

    project_id: str
    name: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    is_completed: Optional[bool] = None
    progress_percentage: Optional[int] = None
    order_index: Optional[int] = None
    notes: Optional[str] = None


@dataclass
class ProjectTaskInput:
    """Project task creation/update input."""

    # Required fields first
    project_id: str
    name: str
    
    # Optional fields with defaults
    milestone_id: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    assigned_to: Optional[str] = None
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    estimated_hours: Optional[int] = None
    progress_percentage: Optional[int] = None
    order_index: Optional[int] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


@dataclass
class ProjectTimeEntryInput:
    """Project time entry creation/update input."""

    # Required fields first
    project_id: str
    user_id: str
    description: str
    hours: float
    start_time: datetime
    
    # Optional fields with defaults
    task_id: Optional[str] = None
    billable_hours: Optional[float] = None
    rate: Optional[float] = None
    end_time: Optional[datetime] = None
    is_billable: Optional[bool] = None
    notes: Optional[str] = None


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


@dataclass
class UserInput:
    """User creation/update input."""

    email: str
    first_name: str
    last_name: str
    role: UserRole
    status: Optional[UserStatus] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    is_technician: Optional[bool] = None
    hourly_rate: Optional[float] = None
    timezone: Optional[str] = None
    is_primary: Optional[bool] = None
    notification_preferences: Optional[Dict[str, Any]] = None
    permissions: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


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
        # Cast to maintain type safety for mypy
        return serialize_filter_value(input_obj)  # type: ignore[no-any-return]
