# # Copyright (c) 2024 SuperOps Team
# # Licensed under the MIT License.
# # See LICENSE file in the project root for full license information.

"""Type-safe GraphQL query and mutation builder classes for SuperOps API.

This module provides builder classes that construct GraphQL operations with type safety,
field selection, filtering, and pagination support.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from .fragments import (
    build_fragments_string,
    get_asset_fields,
    get_client_fields,
    get_kb_fields,
    get_project_fields,
    get_task_fields,
    get_ticket_fields,
    get_user_fields,
)
from .types import (
    AssetFilter,
    ClientFilter,
    ClientInput,
    PaginationArgs,
    ProjectFilter,
    ProjectInput,
    ProjectMilestoneInput,
    ProjectTaskInput,
    ProjectTimeEntryInput,
    SortArgs,
    TaskFilter,
    TaskInput,
    TicketFilter,
    TicketInput,
    UserFilter,
    UserInput,
    serialize_filter_value,
    serialize_input,
)


class QueryBuilder:
    """Base class for building GraphQL queries."""

    def __init__(self):
        """Initialize the query builder."""
        self._operation_name: Optional[str] = None
        self._variables: Dict[str, Any] = {}
        self._variable_definitions: Dict[str, str] = {}
        self._fragments: Set[str] = set()

    def operation_name(self, name: str) -> QueryBuilder:
        """Set the operation name.

        Args:
            name: Operation name

        Returns:
            Self for chaining
        """
        self._operation_name = name
        return self

    def add_variable(self, name: str, type_def: str, value: Any = None) -> QueryBuilder:
        """Add a variable definition.

        Args:
            name: Variable name (without $)
            type_def: GraphQL type definition (e.g., "String!", "[ID!]")
            value: Variable value for query execution

        Returns:
            Self for chaining
        """
        self._variable_definitions[name] = type_def
        if value is not None:
            self._variables[name] = serialize_filter_value(value)
        return self

    def add_fragment(self, fragment_name: str) -> QueryBuilder:
        """Add a fragment to the query.

        Args:
            fragment_name: Name of the fragment

        Returns:
            Self for chaining
        """
        self._fragments.add(fragment_name)
        return self

    def add_fragments(self, fragment_names: Set[str]) -> QueryBuilder:
        """Add multiple fragments to the query.

        Args:
            fragment_names: Set of fragment names

        Returns:
            Self for chaining
        """
        self._fragments.update(fragment_names)
        return self

    def _build_variable_definitions(self) -> str:
        """Build variable definitions string."""
        if not self._variable_definitions:
            return ""

        definitions = []
        for name, type_def in self._variable_definitions.items():
            definitions.append(f"${name}: {type_def}")

        return f"({', '.join(definitions)})"

    def _build_operation_header(self, operation_type: str) -> str:
        """Build operation header with name and variables."""
        header = operation_type

        if self._operation_name:
            header += f" {self._operation_name}"

        var_defs = self._build_variable_definitions()
        if var_defs:
            header += var_defs

        return header

    def get_variables(self) -> Dict[str, Any]:
        """Get variables for query execution."""
        return self._variables.copy()

    def build(self) -> str:
        """Build the complete query string.

        This method must be implemented by subclasses.

        Returns:
            Complete GraphQL query string
        """
        raise NotImplementedError("Subclasses must implement build()")


class SelectionQueryBuilder(QueryBuilder):
    """Builder for queries with field selection."""

    def __init__(self):
        """Initialize the selection query builder."""
        super().__init__()
        self._selections: List[str] = []

    def add_selection(self, selection: str) -> SelectionQueryBuilder:
        """Add a field selection.

        Args:
            selection: Field selection string

        Returns:
            Self for chaining
        """
        self._selections.append(selection.strip())
        return self

    def _build_selections(self) -> str:
        """Build selections string."""
        return "\n".join(f"  {selection}" for selection in self._selections)

    def build_query_body(self, query_field: str, args: str = "") -> str:
        """Build the query body.

        Args:
            query_field: The main query field name
            args: Query arguments string

        Returns:
            Query body string
        """
        selections = self._build_selections()

        if args:
            return f"""{query_field}({args}) {{
{selections}
}}"""
        else:
            return f"""{query_field} {{
{selections}
}}"""

    def build(self, query_field: str, args: str = "") -> str:
        """Build the complete query.

        Args:
            query_field: The main query field name
            args: Query arguments string

        Returns:
            Complete GraphQL query string
        """
        header = self._build_operation_header("query")
        body = self.build_query_body(query_field, args)

        query = f"""{header} {{
{body}
}}"""

        # Add fragments if any
        if self._fragments:
            fragments_str = build_fragments_string(self._fragments)
            query = f"{query}\n\n{fragments_str}"

        return query


class MutationBuilder(QueryBuilder):
    """Builder for GraphQL mutations."""

    def __init__(self):
        """Initialize the mutation builder."""
        super().__init__()
        self._mutation_field: Optional[str] = None
        self._mutation_args: Optional[str] = None
        self._return_fields: List[str] = []

    def mutation_field(self, field: str, args: str = "") -> MutationBuilder:
        """Set the mutation field and arguments.

        Args:
            field: Mutation field name
            args: Mutation arguments string

        Returns:
            Self for chaining
        """
        self._mutation_field = field
        self._mutation_args = args
        return self

    def return_field(self, field: str) -> MutationBuilder:
        """Add a return field.

        Args:
            field: Return field selection

        Returns:
            Self for chaining
        """
        self._return_fields.append(field.strip())
        return self

    def build(self) -> str:
        """Build the complete mutation.

        Returns:
            Complete GraphQL mutation string
        """
        if not self._mutation_field:
            raise ValueError("Mutation field must be set")

        header = self._build_operation_header("mutation")

        # Build mutation body
        args_str = f"({self._mutation_args})" if self._mutation_args else ""
        returns_str = "\n".join(f"  {field}" for field in self._return_fields)

        body = f"""{self._mutation_field}{args_str} {{
{returns_str}
}}"""

        mutation = f"""{header} {{
{body}
}}"""

        # Add fragments if any
        if self._fragments:
            fragments_str = build_fragments_string(self._fragments)
            mutation = f"{mutation}\n\n{fragments_str}"

        return mutation


class ClientQueryBuilder(SelectionQueryBuilder):
    """Builder for client-related queries."""

    def __init__(self, detail_level: str = "core"):
        """Initialize client query builder.

        Args:
            detail_level: Level of detail (summary, core, full)
        """
        super().__init__()
        self.detail_level = detail_level
        self.add_fragments(get_client_fields(detail_level))

    def list_clients(
        self,
        filter_obj: Optional[ClientFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> ClientQueryBuilder:
        """Build a list clients query.

        Args:
            filter_obj: Client filter
            pagination: Pagination arguments
            sort: Sort arguments

        Returns:
            Self for chaining
        """
        # Build arguments
        args = []

        if filter_obj:
            self.add_variable("filter", "ClientFilter", serialize_input(filter_obj))
            args.append("filter: $filter")

        if pagination:
            self.add_variable("page", "Int", pagination.page)
            self.add_variable("pageSize", "Int", pagination.pageSize)
            args.append("page: $page, pageSize: $pageSize")

        if sort:
            self.add_variable("sortField", "String", sort.field)
            self.add_variable("sortDirection", "SortDirection", sort.direction)
            args.append("sortField: $sortField, sortDirection: $sortDirection")

        # Add selections
        fragment_name = get_client_fields(self.detail_level)
        fragment_spread = f"...{list(fragment_name)[0]}"

        return (
            self.add_selection(
                f"""items {{
  {fragment_spread}
}}"""
            )
            .add_selection(
                """pagination {
  ...PaginationInfo
}"""
            )
            .add_fragment("PaginationInfo")
        )

    def get_client(self, client_id: str) -> ClientQueryBuilder:
        """Build a get client by ID query.

        Args:
            client_id: Client ID

        Returns:
            Self for chaining
        """
        self.add_variable("id", "ID!", client_id)

        fragment_name = get_client_fields(self.detail_level)
        fragment_spread = f"...{list(fragment_name)[0]}"

        return self.add_selection(fragment_spread)

    def build_list(
        self,
        filter_obj: Optional[ClientFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> str:
        """Build complete list clients query.

        Args:
            filter_obj: Client filter
            pagination: Pagination arguments
            sort: Sort arguments

        Returns:
            Complete GraphQL query string
        """
        self.list_clients(filter_obj, pagination, sort)
        args = ", ".join(
            [
                arg
                for arg in [
                    "filter: $filter",
                    "page: $page",
                    "pageSize: $pageSize",
                    "sortField: $sortField",
                    "sortDirection: $sortDirection",
                ]
                if any(var in self._variables for var in arg.split("$")[1:] if "$" in arg)
            ]
        )
        return self.build("clients", args)

    def build_get(self, client_id: str) -> str:
        """Build complete get client query.

        Args:
            client_id: Client ID

        Returns:
            Complete GraphQL query string
        """
        self.get_client(client_id)
        return self.build("client", "id: $id")


class TicketQueryBuilder(SelectionQueryBuilder):
    """Builder for ticket-related queries."""

    def __init__(self, detail_level: str = "core", include_comments: bool = False):
        """Initialize ticket query builder.

        Args:
            detail_level: Level of detail (summary, core, full)
            include_comments: Whether to include comment fields
        """
        super().__init__()
        self.detail_level = detail_level
        self.include_comments = include_comments
        self.add_fragments(get_ticket_fields(detail_level, include_comments))

    def list_tickets(
        self,
        filter_obj: Optional[TicketFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> TicketQueryBuilder:
        """Build a list tickets query.

        Args:
            filter_obj: Ticket filter
            pagination: Pagination arguments
            sort: Sort arguments

        Returns:
            Self for chaining
        """
        # Build arguments
        args = []

        if filter_obj:
            self.add_variable("filter", "TicketFilter", serialize_input(filter_obj))
            args.append("filter: $filter")

        if pagination:
            self.add_variable("page", "Int", pagination.page)
            self.add_variable("pageSize", "Int", pagination.pageSize)
            args.append("page: $page, pageSize: $pageSize")

        if sort:
            self.add_variable("sortField", "String", sort.field)
            self.add_variable("sortDirection", "SortDirection", sort.direction)
            args.append("sortField: $sortField, sortDirection: $sortDirection")

        # Add selections
        fragment_names = get_ticket_fields(self.detail_level, self.include_comments)
        main_fragment = [name for name in fragment_names if "Comment" not in name][0]
        fragment_spread = f"...{main_fragment}"

        selection = f"""items {{
  {fragment_spread}"""

        if self.include_comments:
            selection += """
  comments {
    ...TicketCommentFields
  }"""

        selection += "\n}"

        return (
            self.add_selection(selection)
            .add_selection(
                """pagination {
  ...PaginationInfo
}"""
            )
            .add_fragment("PaginationInfo")
        )

    def get_ticket(self, ticket_id: str) -> TicketQueryBuilder:
        """Build a get ticket by ID query.

        Args:
            ticket_id: Ticket ID

        Returns:
            Self for chaining
        """
        self.add_variable("id", "ID!", ticket_id)

        fragment_names = get_ticket_fields(self.detail_level, self.include_comments)
        main_fragment = [name for name in fragment_names if "Comment" not in name][0]
        fragment_spread = f"...{main_fragment}"

        selection = fragment_spread

        if self.include_comments:
            selection += """
comments {
  ...TicketCommentFields
}"""

        return self.add_selection(selection)

    def build_list(
        self,
        filter_obj: Optional[TicketFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> str:
        """Build complete list tickets query.

        Args:
            filter_obj: Ticket filter
            pagination: Pagination arguments
            sort: Sort arguments

        Returns:
            Complete GraphQL query string
        """
        self.list_tickets(filter_obj, pagination, sort)
        args_list = []

        if "filter" in self._variables:
            args_list.append("filter: $filter")
        if "page" in self._variables:
            args_list.append("page: $page, pageSize: $pageSize")
        if "sortField" in self._variables:
            args_list.append("sortField: $sortField, sortDirection: $sortDirection")

        args = ", ".join(args_list)
        return self.build("tickets", args)

    def build_get(self, ticket_id: str) -> str:
        """Build complete get ticket query.

        Args:
            ticket_id: Ticket ID

        Returns:
            Complete GraphQL query string
        """
        self.get_ticket(ticket_id)
        return self.build("ticket", "id: $id")


class TaskQueryBuilder(SelectionQueryBuilder):
    """Builder for task-related queries."""

    def __init__(
        self,
        detail_level: str = "core",
        include_comments: bool = False,
        include_time_entries: bool = False,
        include_template: bool = False,
    ):
        """Initialize task query builder.

        Args:
            detail_level: Level of detail (summary, core, full)
            include_comments: Whether to include comment fields
            include_time_entries: Whether to include time entry fields
            include_template: Whether to include template fields
        """
        super().__init__()
        self.detail_level = detail_level
        self.include_comments = include_comments
        self.include_time_entries = include_time_entries
        self.include_template = include_template
        self.add_fragments(
            get_task_fields(detail_level, include_comments, include_time_entries, include_template)
        )

    def list_tasks(
        self,
        filter_obj: Optional[TaskFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> "TaskQueryBuilder":
        """Build a list tasks query.

        Args:
            filter_obj: Task filter
            pagination: Pagination arguments
            sort: Sort arguments

        Returns:
            Self for chaining
        """
        # Build arguments
        args = []

        if filter_obj:
            self.add_variable("filter", "TaskFilter", serialize_input(filter_obj))
            args.append("filter: $filter")

        if pagination:
            self.add_variable("page", "Int", pagination.page)
            self.add_variable("pageSize", "Int", pagination.pageSize)
            args.append("page: $page, pageSize: $pageSize")

        if sort:
            self.add_variable("sortField", "String", sort.field)
            self.add_variable("sortDirection", "SortDirection", sort.direction)
            args.append("sortField: $sortField, sortDirection: $sortDirection")

        # Add selections
        fragment_name = get_task_fields(
            self.detail_level,
            self.include_comments,
            self.include_time_entries,
            self.include_template,
        )
        fragment_spread = f"...{list(fragment_name)[0]}"

        return (
            self.add_selection(
                f"""items {{
  {fragment_spread}
}}"""
            )
            .add_selection(
                """pagination {
  ...PaginationInfo
}"""
            )
            .add_fragment("PaginationInfo")
        )

    def get_task(self, task_id: str) -> "TaskQueryBuilder":
        """Build a get task by ID query.

        Args:
            task_id: Task ID

        Returns:
            Self for chaining
        """
        self.add_variable("id", "ID!", task_id)

        fragment_name = get_task_fields(
            self.detail_level,
            self.include_comments,
            self.include_time_entries,
            self.include_template,
        )
        fragment_spread = f"...{list(fragment_name)[0]}"

        return self.add_selection(fragment_spread)

    def build_list(
        self,
        filter_obj: Optional[TaskFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> str:
        """Build complete list tasks query.

        Args:
            filter_obj: Task filter
            pagination: Pagination arguments
            sort: Sort arguments

        Returns:
            Complete GraphQL query string
        """
        self.list_tasks(filter_obj, pagination, sort)
        args = ", ".join(
            [
                arg
                for arg in [
                    "filter: $filter",
                    "page: $page",
                    "pageSize: $pageSize",
                    "sortField: $sortField",
                    "sortDirection: $sortDirection",
                ]
                if any(var in self._variables for var in arg.split("$")[1:] if "$" in arg)
            ]
        )
        return self.build("tasks", args)

    def build_get(self, task_id: str) -> str:
        """Build complete get task query.

        Args:
            task_id: Task ID

        Returns:
            Complete GraphQL query string
        """
        self.get_task(task_id)
        return self.build("task", "id: $id")


class AssetQueryBuilder(SelectionQueryBuilder):
    """Builder for asset-related queries."""

    def __init__(self, detail_level: str = "core"):
        """Initialize asset query builder.

        Args:
            detail_level: Level of detail (summary, core, full)
        """
        super().__init__()
        self.detail_level = detail_level
        self.add_fragments(get_asset_fields(detail_level))

    def list_assets(
        self,
        filter_obj: Optional[AssetFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> AssetQueryBuilder:
        """Build a list assets query.

        Args:
            filter_obj: Asset filter
            pagination: Pagination arguments
            sort: Sort arguments

        Returns:
            Self for chaining
        """
        if filter_obj:
            self.add_variable("filter", "AssetFilter", serialize_input(filter_obj))

        if pagination:
            self.add_variable("page", "Int", pagination.page)
            self.add_variable("pageSize", "Int", pagination.pageSize)

        if sort:
            self.add_variable("sortField", "String", sort.field)
            self.add_variable("sortDirection", "SortDirection", sort.direction)

        # Add selections
        fragment_name = get_asset_fields(self.detail_level)
        fragment_spread = f"...{list(fragment_name)[0]}"

        return (
            self.add_selection(
                f"""items {{
  {fragment_spread}
}}"""
            )
            .add_selection(
                """pagination {
  ...PaginationInfo
}"""
            )
            .add_fragment("PaginationInfo")
        )

    def get_asset(self, asset_id: str) -> AssetQueryBuilder:
        """Build a get asset by ID query.

        Args:
            asset_id: Asset ID

        Returns:
            Self for chaining
        """
        self.add_variable("id", "ID!", asset_id)

        fragment_name = get_asset_fields(self.detail_level)
        fragment_spread = f"...{list(fragment_name)[0]}"

        return self.add_selection(fragment_spread)

    def build_list(
        self,
        filter_obj: Optional[AssetFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> str:
        """Build complete list assets query."""
        self.list_assets(filter_obj, pagination, sort)
        args_list = []

        if "filter" in self._variables:
            args_list.append("filter: $filter")
        if "page" in self._variables:
            args_list.append("page: $page, pageSize: $pageSize")
        if "sortField" in self._variables:
            args_list.append("sortField: $sortField, sortDirection: $sortDirection")

        args = ", ".join(args_list)
        return self.build("assets", args)

    def build_get(self, asset_id: str) -> str:
        """Build complete get asset query."""
        self.get_asset(asset_id)
        return self.build("asset", "id: $id")


class UserQueryBuilder(SelectionQueryBuilder):
    """Builder for user-related queries."""

    def __init__(self, detail_level: str = "core"):
        """Initialize user query builder.

        Args:
            detail_level: Level of detail (summary, core, full)
        """
        super().__init__()
        self.detail_level = detail_level
        self.add_fragments(get_user_fields(detail_level))

    def list_users(
        self,
        filter_obj: Optional[UserFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> "UserQueryBuilder":
        """Build a list users query.

        Args:
            filter_obj: User filter
            pagination: Pagination arguments
            sort: Sort arguments

        Returns:
            Self for chaining
        """
        # Build arguments
        args = []

        if filter_obj:
            self.add_variable("filter", "UserFilter", serialize_input(filter_obj))
            args.append("filter: $filter")

        if pagination:
            self.add_variable("page", "Int", pagination.page)
            self.add_variable("pageSize", "Int", pagination.pageSize)
            args.append("page: $page, pageSize: $pageSize")

        if sort:
            self.add_variable("sortField", "String", sort.field)
            self.add_variable("sortDirection", "SortDirection", sort.direction)
            args.append("sortField: $sortField, sortDirection: $sortDirection")

        # Add selections
        fragment_name = list(get_user_fields(self.detail_level))[0]
        fragment_spread = f"...{fragment_name}"

        return (
            self.add_selection(
                f"""items {{
  {fragment_spread}
}}"""
            )
            .add_selection(
                """pagination {
  ...PaginationInfo
}"""
            )
            .add_fragment("PaginationInfo")
        )

    def get_user(self, user_id: str) -> "UserQueryBuilder":
        """Build a get user by ID query.

        Args:
            user_id: User ID

        Returns:
            Self for chaining
        """
        self.add_variable("id", "ID!", user_id)
        fragment_name = list(get_user_fields(self.detail_level))[0]
        fragment_spread = f"...{fragment_name}"
        return self.add_selection(fragment_spread)

    def build_list(
        self,
        filter_obj: Optional[UserFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> str:
        """Build complete list users query.

        Args:
            filter_obj: User filter
            pagination: Pagination arguments
            sort: Sort arguments

        Returns:
            Complete GraphQL query string
        """
        self.list_users(filter_obj, pagination, sort)

        # Build args list for query
        args_list = []
        if filter_obj:
            args_list.append("filter: $filter")
        if pagination:
            args_list.extend(["page: $page", "pageSize: $pageSize"])
        if sort:
            args_list.extend(["sortField: $sortField", "sortDirection: $sortDirection"])

        args = ", ".join(args_list)
        return self.build("users", args)

    def build_get(self, user_id: str) -> str:
        """Build complete get user query.

        Args:
            user_id: User ID

        Returns:
            Complete GraphQL query string
        """
        self.get_user(user_id)
        return self.build("user", "id: $id")


class ProjectQueryBuilder(SelectionQueryBuilder):
    """Builder for project-related queries."""

    def __init__(
        self,
        detail_level: str = "core",
        include_milestones: bool = False,
        include_tasks: bool = False,
        include_time_entries: bool = False,
        task_detail: str = "core",
    ):
        """Initialize project query builder.

        Args:
            detail_level: Level of detail (summary, core, full)
            include_milestones: Whether to include milestone fields
            include_tasks: Whether to include task fields
            include_time_entries: Whether to include time entry fields
            task_detail: Level of detail for tasks (core, full)
        """
        super().__init__()
        self.detail_level = detail_level
        self.include_milestones = include_milestones
        self.include_tasks = include_tasks
        self.include_time_entries = include_time_entries
        self.task_detail = task_detail

        project_fragments = get_project_fields(
            detail_level=detail_level,
            include_milestones=include_milestones,
            include_tasks=include_tasks,
            include_time_entries=include_time_entries,
            task_detail=task_detail,
        )
        self.add_fragments(project_fragments)

    def list_projects(
        self,
        filter_obj: Optional[ProjectFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> ProjectQueryBuilder:
        """Build a list projects query.

        Args:
            filter_obj: Project filter
            pagination: Pagination arguments
            sort: Sort arguments

        Returns:
            Self for chaining
        """
        # Build arguments
        args = []

        if filter_obj:
            self.add_variable("filter", "ProjectFilter", serialize_input(filter_obj))
            args.append("filter: $filter")

        if pagination:
            self.add_variable("page", "Int", pagination.page)
            self.add_variable("pageSize", "Int", pagination.pageSize)
            args.append("page: $page, pageSize: $pageSize")

        if sort:
            self.add_variable("sortField", "String", sort.field)
            self.add_variable("sortDirection", "SortDirection", sort.direction)
            args.append("sortField: $sortField, sortDirection: $sortDirection")

        # Add selections
        project_fragments = get_project_fields(
            detail_level=self.detail_level,
            include_milestones=self.include_milestones,
            include_tasks=self.include_tasks,
            include_time_entries=self.include_time_entries,
            task_detail=self.task_detail,
        )

        # Get main project fragment
        main_fragment = None
        for fragment in project_fragments:
            if (
                "ProjectSummaryFields" in fragment
                or "ProjectCoreFields" in fragment
                or "ProjectFullFields" in fragment
            ):
                main_fragment = fragment
                break

        if not main_fragment:
            main_fragment = "ProjectCoreFields"

        items_selection = f"""items {{
  ...{main_fragment}"""

        # Add nested selections for milestones, tasks, etc.
        if self.include_milestones:
            items_selection += """
  milestones {
    ...ProjectMilestoneFields
  }"""

        if self.include_tasks:
            task_fragment = (
                "ProjectTaskCoreFields" if self.task_detail == "core" else "ProjectTaskFullFields"
            )
            items_selection += f"""
  tasks {{
    ...{task_fragment}
  }}"""

        if self.include_time_entries:
            items_selection += """
  timeEntries {
    ...ProjectTimeEntryFields
  }"""

        items_selection += "\n}"

        return (
            self.add_selection(items_selection)
            .add_selection(
                """pagination {
  ...PaginationInfo
}"""
            )
            .add_fragment("PaginationInfo")
        )

    def get_project(self, project_id: str) -> ProjectQueryBuilder:
        """Build a get project by ID query.

        Args:
            project_id: Project ID

        Returns:
            Self for chaining
        """
        self.add_variable("id", "ID!", project_id)

        project_fragments = get_project_fields(
            detail_level=self.detail_level,
            include_milestones=self.include_milestones,
            include_tasks=self.include_tasks,
            include_time_entries=self.include_time_entries,
            task_detail=self.task_detail,
        )

        # Get main project fragment
        main_fragment = None
        for fragment in project_fragments:
            if (
                "ProjectSummaryFields" in fragment
                or "ProjectCoreFields" in fragment
                or "ProjectFullFields" in fragment
            ):
                main_fragment = fragment
                break

        if not main_fragment:
            main_fragment = "ProjectCoreFields"

        selection = f"...{main_fragment}"

        # Add nested selections
        if self.include_milestones:
            selection += """
milestones {
  ...ProjectMilestoneFields
}"""

        if self.include_tasks:
            task_fragment = (
                "ProjectTaskCoreFields" if self.task_detail == "core" else "ProjectTaskFullFields"
            )
            selection += f"""
tasks {{
  ...{task_fragment}
}}"""

        if self.include_time_entries:
            selection += """
timeEntries {
  ...ProjectTimeEntryFields
}"""

        return self.add_selection(selection)

    def build_list(
        self,
        filter_obj: Optional[ProjectFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> str:
        """Build list projects query string."""
        self.list_projects(filter_obj, pagination, sort)
        args = ", ".join(
            f"{k}: ${k}" for k in self._variable_definitions.keys() if k in self._variables
        )
        return self.build("projects", args)

    def build_get(self, project_id: str) -> str:
        """Build get project query string."""
        self.get_project(project_id)
        return self.build("project", "id: $id")


class ClientMutationBuilder(MutationBuilder):
    """Builder for client mutations."""

    def __init__(self, detail_level: str = "core"):
        """Initialize client mutation builder.

        Args:
            detail_level: Level of detail for returned fields
        """
        super().__init__()
        self.detail_level = detail_level
        self.add_fragments(get_client_fields(detail_level))

        # Add return fields
        fragment_name = list(get_client_fields(detail_level))[0]
        self.return_field(f"...{fragment_name}")

    def create_client(self, input_data: ClientInput) -> str:
        """Build create client mutation.

        Args:
            input_data: Client input data

        Returns:
            Complete GraphQL mutation string
        """
        self.add_variable("input", "ClientInput!", serialize_input(input_data))
        return self.mutation_field("createClient", "input: $input").build()

    def update_client(self, client_id: str, input_data: ClientInput) -> str:
        """Build update client mutation.

        Args:
            client_id: Client ID
            input_data: Client input data

        Returns:
            Complete GraphQL mutation string
        """
        self.add_variable("id", "ID!", client_id)
        self.add_variable("input", "ClientInput!", serialize_input(input_data))
        return self.mutation_field("updateClient", "id: $id, input: $input").build()

    def delete_client(self, client_id: str) -> str:
        """Build delete client mutation.

        Args:
            client_id: Client ID

        Returns:
            Complete GraphQL mutation string
        """
        self.add_variable("id", "ID!", client_id)
        self._return_fields = ["success", "message"]  # Override return fields
        return self.mutation_field("deleteClient", "id: $id").build()


class TicketMutationBuilder(MutationBuilder):
    """Builder for ticket mutations."""

    def __init__(self, detail_level: str = "core"):
        """Initialize ticket mutation builder.

        Args:
            detail_level: Level of detail for returned fields
        """
        super().__init__()
        self.detail_level = detail_level
        fragment_names = get_ticket_fields(detail_level)
        self.add_fragments(fragment_names)

        # Add return fields
        main_fragment = [name for name in fragment_names if "Comment" not in name][0]
        self.return_field(f"...{main_fragment}")

    def create_ticket(self, input_data: TicketInput) -> str:
        """Build create ticket mutation."""
        self.add_variable("input", "TicketInput!", serialize_input(input_data))
        return self.mutation_field("createTicket", "input: $input").build()

    def update_ticket(self, ticket_id: str, input_data: TicketInput) -> str:
        """Build update ticket mutation."""
        self.add_variable("id", "ID!", ticket_id)
        self.add_variable("input", "TicketInput!", serialize_input(input_data))
        return self.mutation_field("updateTicket", "id: $id, input: $input").build()

    def delete_ticket(self, ticket_id: str) -> str:
        """Build delete ticket mutation."""
        self.add_variable("id", "ID!", ticket_id)
        self._return_fields = ["success", "message"]
        return self.mutation_field("deleteTicket", "id: $id").build()


class ProjectMutationBuilder(MutationBuilder):
    """Builder for project mutations."""

    def __init__(self, detail_level: str = "core"):
        """Initialize project mutation builder.

        Args:
            detail_level: Level of detail for returned fields
        """
        super().__init__()
        self.detail_level = detail_level

        project_fragments = get_project_fields(detail_level)
        self.add_fragments(project_fragments)

        # Set return fields based on fragment
        main_fragment = None
        for fragment in project_fragments:
            if (
                "ProjectSummaryFields" in fragment
                or "ProjectCoreFields" in fragment
                or "ProjectFullFields" in fragment
            ):
                main_fragment = fragment
                break

        if not main_fragment:
            main_fragment = "ProjectCoreFields"

        self._return_fields = [f"...{main_fragment}"]

    def create_project(self, input_data: ProjectInput) -> str:
        """Build create project mutation."""
        self.add_variable("input", "ProjectInput!", serialize_input(input_data))
        return self.mutation_field("createProject", "input: $input").build()

    def update_project(self, project_id: str, input_data: ProjectInput) -> str:
        """Build update project mutation."""
        self.add_variable("id", "ID!", project_id)
        self.add_variable("input", "ProjectInput!", serialize_input(input_data))
        return self.mutation_field("updateProject", "id: $id, input: $input").build()

    def delete_project(self, project_id: str) -> str:
        """Build delete project mutation."""
        self.add_variable("id", "ID!", project_id)
        self._return_fields = ["success", "message"]
        return self.mutation_field("deleteProject", "id: $id").build()

    def create_milestone(self, input_data: ProjectMilestoneInput) -> str:
        """Build create project milestone mutation."""
        self.add_variable("input", "ProjectMilestoneInput!", serialize_input(input_data))
        self._return_fields = ["...ProjectMilestoneFields"]
        self.add_fragment("ProjectMilestoneFields")
        return self.mutation_field("createProjectMilestone", "input: $input").build()

    def update_milestone(self, milestone_id: str, input_data: ProjectMilestoneInput) -> str:
        """Build update project milestone mutation."""
        self.add_variable("id", "ID!", milestone_id)
        self.add_variable("input", "ProjectMilestoneInput!", serialize_input(input_data))
        self._return_fields = ["...ProjectMilestoneFields"]
        self.add_fragment("ProjectMilestoneFields")
        return self.mutation_field("updateProjectMilestone", "id: $id, input: $input").build()

    def delete_milestone(self, milestone_id: str) -> str:
        """Build delete project milestone mutation."""
        self.add_variable("id", "ID!", milestone_id)
        self._return_fields = ["success", "message"]
        return self.mutation_field("deleteProjectMilestone", "id: $id").build()

    def create_task(self, input_data: ProjectTaskInput) -> str:
        """Build create project task mutation."""
        self.add_variable("input", "ProjectTaskInput!", serialize_input(input_data))
        self._return_fields = ["...ProjectTaskFullFields"]
        self.add_fragment("ProjectTaskFullFields")
        return self.mutation_field("createProjectTask", "input: $input").build()

    def update_task(self, task_id: str, input_data: ProjectTaskInput) -> str:
        """Build update project task mutation."""
        self.add_variable("id", "ID!", task_id)
        self.add_variable("input", "ProjectTaskInput!", serialize_input(input_data))
        self._return_fields = ["...ProjectTaskFullFields"]
        self.add_fragment("ProjectTaskFullFields")
        return self.mutation_field("updateProjectTask", "id: $id, input: $input").build()

    def delete_task(self, task_id: str) -> str:
        """Build delete project task mutation."""
        self.add_variable("id", "ID!", task_id)
        self._return_fields = ["success", "message"]
        return self.mutation_field("deleteProjectTask", "id: $id").build()

    def create_time_entry(self, input_data: ProjectTimeEntryInput) -> str:
        """Build create project time entry mutation."""
        self.add_variable("input", "ProjectTimeEntryInput!", serialize_input(input_data))
        self._return_fields = ["...ProjectTimeEntryFields"]
        self.add_fragment("ProjectTimeEntryFields")
        return self.mutation_field("createProjectTimeEntry", "input: $input").build()

    def update_time_entry(self, time_entry_id: str, input_data: ProjectTimeEntryInput) -> str:
        """Build update project time entry mutation."""
        self.add_variable("id", "ID!", time_entry_id)
        self.add_variable("input", "ProjectTimeEntryInput!", serialize_input(input_data))
        self._return_fields = ["...ProjectTimeEntryFields"]
        self.add_fragment("ProjectTimeEntryFields")
        return self.mutation_field("updateProjectTimeEntry", "id: $id, input: $input").build()

    def delete_time_entry(self, time_entry_id: str) -> str:
        """Build delete project time entry mutation."""
        self.add_variable("id", "ID!", time_entry_id)
        self._return_fields = ["success", "message"]
        return self.mutation_field("deleteProjectTimeEntry", "id: $id").build()


class UserMutationBuilder(MutationBuilder):
    """Builder for user mutations."""

    def __init__(self, detail_level: str = "core"):
        """Initialize user mutation builder.

        Args:
            detail_level: Level of detail for returned fields
        """
        super().__init__()
        self.detail_level = detail_level
        fragment_names = get_user_fields(detail_level)
        self.add_fragments(fragment_names)

        # Add return fields
        main_fragment = list(fragment_names)[0]
        self.return_field(f"...{main_fragment}")

    def create_user(self, input_data: UserInput) -> str:
        """Build create user mutation.

        Args:
            input_data: User input data

        Returns:
            Complete GraphQL mutation string
        """
        self.add_variable("input", "UserInput!", serialize_input(input_data))
        return self.mutation_field("createUser", "input: $input").build()

    def update_user(self, user_id: str, input_data: UserInput) -> str:
        """Build update user mutation.

        Args:
            user_id: User ID
            input_data: User input data

        Returns:
            Complete GraphQL mutation string
        """
        self.add_variable("id", "ID!", user_id)
        self.add_variable("input", "UserInput!", serialize_input(input_data))
        return self.mutation_field("updateUser", "id: $id, input: $input").build()

    def delete_user(self, user_id: str) -> str:
        """Build delete user mutation.

        Args:
            user_id: User ID

        Returns:
            Complete GraphQL mutation string
        """
        self.add_variable("id", "ID!", user_id)
        self._return_fields = ["success", "message"]  # Override return fields
        return self.mutation_field("deleteUser", "id: $id").build()


# Factory functions for easy builder creation
def create_client_query_builder(detail_level: str = "core") -> ClientQueryBuilder:
    """Create a client query builder.

    Args:
        detail_level: Level of detail (summary, core, full)

    Returns:
        ClientQueryBuilder instance
    """
    return ClientQueryBuilder(detail_level)


def create_ticket_query_builder(
    detail_level: str = "core", include_comments: bool = False
) -> TicketQueryBuilder:
    """Create a ticket query builder.

    Args:
        detail_level: Level of detail (summary, core, full)
        include_comments: Whether to include comment fields

    Returns:
        TicketQueryBuilder instance
    """
    return TicketQueryBuilder(detail_level, include_comments)


def create_asset_query_builder(detail_level: str = "core") -> AssetQueryBuilder:
    """Create an asset query builder.

    Args:
        detail_level: Level of detail (summary, core, full)

    Returns:
        AssetQueryBuilder instance
    """
    return AssetQueryBuilder(detail_level)


def create_project_query_builder(
    detail_level: str = "core",
    include_milestones: bool = False,
    include_tasks: bool = False,
    include_time_entries: bool = False,
    task_detail: str = "core",
) -> ProjectQueryBuilder:
    """Create a project query builder.

    Args:
        detail_level: Level of detail for projects (summary, core, full)
        include_milestones: Whether to include milestone fields
        include_tasks: Whether to include task fields
        include_time_entries: Whether to include time entry fields
        task_detail: Level of detail for tasks (core, full)

    Returns:
        ProjectQueryBuilder instance
    """
    return ProjectQueryBuilder(
        detail_level=detail_level,
        include_milestones=include_milestones,
        include_tasks=include_tasks,
        include_time_entries=include_time_entries,
        task_detail=task_detail,
    )


def create_client_mutation_builder(detail_level: str = "core") -> ClientMutationBuilder:
    """Create a client mutation builder.

    Args:
        detail_level: Level of detail for returned fields

    Returns:
        ClientMutationBuilder instance
    """
    return ClientMutationBuilder(detail_level)


def create_ticket_mutation_builder(detail_level: str = "core") -> TicketMutationBuilder:
    """Create a ticket mutation builder.

    Args:
        detail_level: Level of detail for returned fields

    Returns:
        TicketMutationBuilder instance
    """
    return TicketMutationBuilder(detail_level)


def create_project_mutation_builder(detail_level: str = "core") -> ProjectMutationBuilder:
    """Create a project mutation builder.

    Args:
        detail_level: Level of detail for returned fields

    Returns:
        ProjectMutationBuilder instance
    """
    return ProjectMutationBuilder(detail_level)


def create_task_query_builder(
    detail_level: str = "core",
    include_comments: bool = False,
    include_time_entries: bool = False,
    include_template: bool = False,
) -> TaskQueryBuilder:
    """Create a task query builder.

    Args:
        detail_level: Level of detail (summary, core, full)
        include_comments: Whether to include comment fields
        include_time_entries: Whether to include time entry fields
        include_template: Whether to include template fields

    Returns:
        TaskQueryBuilder instance
    """
    return TaskQueryBuilder(detail_level, include_comments, include_time_entries, include_template)


def create_user_query_builder(detail_level: str = "core") -> UserQueryBuilder:
    """Create a user query builder.

    Args:
        detail_level: Level of detail (summary, core, full)

    Returns:
        UserQueryBuilder instance
    """
    return UserQueryBuilder(detail_level)


def create_user_mutation_builder(detail_level: str = "core") -> UserMutationBuilder:
    """Create a user mutation builder.

    Args:
        detail_level: Level of detail for returned fields

    Returns:
        UserMutationBuilder instance
    """
    return UserMutationBuilder(detail_level)
