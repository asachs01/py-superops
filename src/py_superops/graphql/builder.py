# # Copyright (c) 2024 SuperOps Team
# # Licensed under the MIT License.
# # See LICENSE file in the project root for full license information.

"""Type-safe GraphQL query and mutation builder classes for SuperOps API.

This module provides builder classes that construct GraphQL operations with type safety,
field selection, filtering, and pagination support.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Type, Union

from .fragments import (
    ALL_FRAGMENTS,
    build_fragments_string,
    get_asset_fields,
    get_client_fields,
    get_kb_fields,
    get_task_fields,
    get_ticket_fields,
)
from .types import (
    AssetFilter,
    AssetInput,
    ClientFilter,
    ClientInput,
    ContactInput,
    KnowledgeBaseArticleInput,
    KnowledgeBaseCollectionInput,
    PaginationArgs,
    SiteInput,
    SortArgs,
    TaskFilter,
    TaskInput,
    TicketFilter,
    TicketInput,
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
