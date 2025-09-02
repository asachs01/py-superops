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
    get_ticket_fields,
    get_time_entry_fields,
    get_time_entry_template_fields,
    get_timer_fields,
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
    TicketFilter,
    TicketInput,
    TimeEntryApprovalInput,
    TimeEntryFilter,
    TimeEntryInput,
    TimeEntryTemplateInput,
    TimerFilter,
    TimerInput,
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


# Time Entry Builders
class TimeEntryQueryBuilder(SelectionQueryBuilder):
    """Builder for time entry-related queries."""

    def __init__(self, detail_level: str = "core"):
        """Initialize time entry query builder.

        Args:
            detail_level: Level of detail (summary, core, full)
        """
        super().__init__()
        self._detail_level = detail_level

        # Add fragments for time entries
        fragments = get_time_entry_fields(detail_level)
        self.add_fragments(fragments)

    def build_get(self, time_entry_id: str) -> str:
        """Build query to get a single time entry.

        Args:
            time_entry_id: Time entry ID

        Returns:
            GraphQL query string
        """
        self.add_variable("id", "ID!", time_entry_id)

        fragments_str = build_fragments_string(self._fragments)
        spreads = "\n  ".join(f"...{name}" for name in sorted(self._fragments))

        query = f"""query GetTimeEntry($id: ID!) {{
  timeEntry(id: $id) {{
    {spreads}
  }}
}}

{fragments_str}"""

        return query

    def build_list(
        self,
        filter_obj: Optional[TimeEntryFilter] = None,
        pagination: Optional[PaginationArgs] = None,
        sort: Optional[SortArgs] = None,
    ) -> str:
        """Build query to list time entries.

        Args:
            filter_obj: Filter conditions
            pagination: Pagination settings
            sort: Sort settings

        Returns:
            GraphQL query string
        """
        # Add variables
        if filter_obj:
            self.add_variable("filters", "TimeEntryFilter", serialize_input(filter_obj))

        if pagination:
            self.add_variable("page", "Int!", pagination.page)
            self.add_variable("pageSize", "Int!", pagination.pageSize)
        else:
            self.add_variable("page", "Int!", 1)
            self.add_variable("pageSize", "Int!", 50)

        if sort:
            self.add_variable("sortBy", "String", sort.field)
            self.add_variable("sortOrder", "SortOrder", sort.direction)

        fragments_str = build_fragments_string(self._fragments)
        spreads = "\n      ".join(f"...{name}" for name in sorted(self._fragments))

        query = f"""query ListTimeEntries($page: Int!, $pageSize: Int!, $filters: TimeEntryFilter, $sortBy: String, $sortOrder: SortOrder) {{
  timeEntries(page: $page, pageSize: $pageSize, filters: $filters, sortBy: $sortBy, sortOrder: $sortOrder) {{
    items {{
      {spreads}
    }}
    pagination {{
      page
      pageSize
      total
      hasNextPage
      hasPreviousPage
    }}
  }}
}}

{fragments_str}"""

        return query

    def build_search(self, search_query: str, pagination: Optional[PaginationArgs] = None) -> str:
        """Build query to search time entries.

        Args:
            search_query: Search query string
            pagination: Pagination settings

        Returns:
            GraphQL query string
        """
        self.add_variable("query", "String!", search_query)

        if pagination:
            self.add_variable("page", "Int!", pagination.page)
            self.add_variable("pageSize", "Int!", pagination.pageSize)
        else:
            self.add_variable("page", "Int!", 1)
            self.add_variable("pageSize", "Int!", 50)

        fragments_str = build_fragments_string(self._fragments)
        spreads = "\n      ".join(f"...{name}" for name in sorted(self._fragments))

        query = f"""query SearchTimeEntries($query: String!, $page: Int!, $pageSize: Int!) {{
  searchTimeEntries(query: $query, page: $page, pageSize: $pageSize) {{
    items {{
      {spreads}
    }}
    pagination {{
      page
      pageSize
      total
      hasNextPage
      hasPreviousPage
    }}
  }}
}}

{fragments_str}"""

        return query


class TimerQueryBuilder(SelectionQueryBuilder):
    """Builder for timer-related queries."""

    def __init__(self):
        """Initialize timer query builder."""
        super().__init__()

        # Add fragments for timers
        fragments = get_timer_fields()
        self.add_fragments(fragments)

    def build_get(self, timer_id: str) -> str:
        """Build query to get a single timer.

        Args:
            timer_id: Timer ID

        Returns:
            GraphQL query string
        """
        self.add_variable("id", "ID!", timer_id)

        fragments_str = build_fragments_string(self._fragments)
        spreads = "\n  ".join(f"...{name}" for name in sorted(self._fragments))

        query = f"""query GetTimer($id: ID!) {{
  timer(id: $id) {{
    {spreads}
  }}
}}

{fragments_str}"""

        return query

    def build_list(
        self,
        filter_obj: Optional[TimerFilter] = None,
        pagination: Optional[PaginationArgs] = None,
    ) -> str:
        """Build query to list timers.

        Args:
            filter_obj: Filter conditions
            pagination: Pagination settings

        Returns:
            GraphQL query string
        """
        # Add variables
        if filter_obj:
            self.add_variable("filters", "TimerFilter", serialize_input(filter_obj))

        if pagination:
            self.add_variable("page", "Int!", pagination.page)
            self.add_variable("pageSize", "Int!", pagination.pageSize)
        else:
            self.add_variable("page", "Int!", 1)
            self.add_variable("pageSize", "Int!", 50)

        fragments_str = build_fragments_string(self._fragments)
        spreads = "\n      ".join(f"...{name}" for name in sorted(self._fragments))

        query = f"""query ListTimers($page: Int!, $pageSize: Int!, $filters: TimerFilter) {{
  timers(page: $page, pageSize: $pageSize, filters: $filters) {{
    items {{
      {spreads}
    }}
    pagination {{
      page
      pageSize
      total
      hasNextPage
      hasPreviousPage
    }}
  }}
}}

{fragments_str}"""

        return query

    def build_active_timer(self, user_id: str) -> str:
        """Build query to get active timer for a user.

        Args:
            user_id: User ID

        Returns:
            GraphQL query string
        """
        self.add_variable("userId", "ID!", user_id)

        fragments_str = build_fragments_string(self._fragments)
        spreads = "\n  ".join(f"...{name}" for name in sorted(self._fragments))

        query = f"""query GetActiveTimer($userId: ID!) {{
  activeTimer(userId: $userId) {{
    {spreads}
  }}
}}

{fragments_str}"""

        return query


class TimeEntryMutationBuilder(MutationBuilder):
    """Builder for time entry mutations."""

    def __init__(self, detail_level: str = "core"):
        """Initialize time entry mutation builder.

        Args:
            detail_level: Level of detail for returned fields
        """
        super().__init__()
        self._detail_level = detail_level

        # Add fragments for time entries
        fragments = get_time_entry_fields(detail_level)
        self.add_fragments(fragments)

    def build_create(self, input_data: TimeEntryInput) -> str:
        """Build mutation to create a time entry.

        Args:
            input_data: Time entry input data

        Returns:
            GraphQL mutation string
        """
        self.add_variable("input", "CreateTimeEntryInput!", serialize_input(input_data))

        fragments_str = build_fragments_string(self._fragments)
        spreads = "\n  ".join(f"...{name}" for name in sorted(self._fragments))

        mutation = f"""mutation CreateTimeEntry($input: CreateTimeEntryInput!) {{
  createTimeEntry(input: $input) {{
    {spreads}
  }}
}}

{fragments_str}"""

        return mutation

    def build_update(self, time_entry_id: str, input_data: TimeEntryInput) -> str:
        """Build mutation to update a time entry.

        Args:
            time_entry_id: Time entry ID
            input_data: Time entry input data

        Returns:
            GraphQL mutation string
        """
        self.add_variable("id", "ID!", time_entry_id)
        self.add_variable("input", "UpdateTimeEntryInput!", serialize_input(input_data))

        fragments_str = build_fragments_string(self._fragments)
        spreads = "\n  ".join(f"...{name}" for name in sorted(self._fragments))

        mutation = f"""mutation UpdateTimeEntry($id: ID!, $input: UpdateTimeEntryInput!) {{
  updateTimeEntry(id: $id, input: $input) {{
    {spreads}
  }}
}}

{fragments_str}"""

        return mutation

    def build_delete(self, time_entry_id: str) -> str:
        """Build mutation to delete a time entry.

        Args:
            time_entry_id: Time entry ID

        Returns:
            GraphQL mutation string
        """
        self.add_variable("id", "ID!", time_entry_id)

        mutation = """mutation DeleteTimeEntry($id: ID!) {
  deleteTimeEntry(id: $id) {
    success
    message
  }
}"""

        return mutation

    def build_bulk_approve(self, approval_input: TimeEntryApprovalInput) -> str:
        """Build mutation to bulk approve/reject time entries.

        Args:
            approval_input: Approval input data

        Returns:
            GraphQL mutation string
        """
        self.add_variable("input", "TimeEntryApprovalInput!", serialize_input(approval_input))

        fragments_str = build_fragments_string(self._fragments)
        spreads = "\n      ".join(f"...{name}" for name in sorted(self._fragments))

        mutation = f"""mutation BulkApproveTimeEntries($input: TimeEntryApprovalInput!) {{
  bulkApproveTimeEntries(input: $input) {{
    timeEntries {{
      {spreads}
    }}
    success
    message
  }}
}}

{fragments_str}"""

        return mutation


class TimerMutationBuilder(MutationBuilder):
    """Builder for timer mutations."""

    def __init__(self):
        """Initialize timer mutation builder."""
        super().__init__()

        # Add fragments for timers
        fragments = get_timer_fields()
        self.add_fragments(fragments)

    def build_start(self, input_data: TimerInput) -> str:
        """Build mutation to start a timer.

        Args:
            input_data: Timer input data

        Returns:
            GraphQL mutation string
        """
        self.add_variable("input", "StartTimerInput!", serialize_input(input_data))

        fragments_str = build_fragments_string(self._fragments)
        spreads = "\n  ".join(f"...{name}" for name in sorted(self._fragments))

        mutation = f"""mutation StartTimer($input: StartTimerInput!) {{
  startTimer(input: $input) {{
    {spreads}
  }}
}}

{fragments_str}"""

        return mutation

    def build_stop(self, timer_id: str) -> str:
        """Build mutation to stop a timer.

        Args:
            timer_id: Timer ID

        Returns:
            GraphQL mutation string
        """
        self.add_variable("timerId", "ID!", timer_id)

        fragments_str = build_fragments_string(self._fragments)
        time_entry_fragments = get_time_entry_fields("core")
        combined_fragments = self._fragments.union(time_entry_fragments)
        all_fragments_str = build_fragments_string(combined_fragments)

        timer_spreads = "\n    ".join(f"...{name}" for name in sorted(self._fragments))
        time_entry_spreads = "\n    ".join(f"...{name}" for name in sorted(time_entry_fragments))

        mutation = f"""mutation StopTimer($timerId: ID!) {{
  stopTimer(timerId: $timerId) {{
    timer {{
      {timer_spreads}
    }}
    timeEntry {{
      {time_entry_spreads}
    }}
  }}
}}

{all_fragments_str}"""

        return mutation

    def build_pause(self, timer_id: str) -> str:
        """Build mutation to pause a timer.

        Args:
            timer_id: Timer ID

        Returns:
            GraphQL mutation string
        """
        self.add_variable("timerId", "ID!", timer_id)

        fragments_str = build_fragments_string(self._fragments)
        spreads = "\n  ".join(f"...{name}" for name in sorted(self._fragments))

        mutation = f"""mutation PauseTimer($timerId: ID!) {{
  pauseTimer(timerId: $timerId) {{
    {spreads}
  }}
}}

{fragments_str}"""

        return mutation

    def build_resume(self, timer_id: str) -> str:
        """Build mutation to resume a timer.

        Args:
            timer_id: Timer ID

        Returns:
            GraphQL mutation string
        """
        self.add_variable("timerId", "ID!", timer_id)

        fragments_str = build_fragments_string(self._fragments)
        spreads = "\n  ".join(f"...{name}" for name in sorted(self._fragments))

        mutation = f"""mutation ResumeTimer($timerId: ID!) {{
  resumeTimer(timerId: $timerId) {{
    {spreads}
  }}
}}

{fragments_str}"""

        return mutation


# Factory functions for time entry builders
def create_time_entry_query_builder(detail_level: str = "core") -> TimeEntryQueryBuilder:
    """Create a time entry query builder.

    Args:
        detail_level: Level of detail (summary, core, full)

    Returns:
        TimeEntryQueryBuilder instance
    """
    return TimeEntryQueryBuilder(detail_level)


def create_timer_query_builder() -> TimerQueryBuilder:
    """Create a timer query builder.

    Returns:
        TimerQueryBuilder instance
    """
    return TimerQueryBuilder()


def create_time_entry_mutation_builder(detail_level: str = "core") -> TimeEntryMutationBuilder:
    """Create a time entry mutation builder.

    Args:
        detail_level: Level of detail for returned fields

    Returns:
        TimeEntryMutationBuilder instance
    """
    return TimeEntryMutationBuilder(detail_level)


def create_timer_mutation_builder() -> TimerMutationBuilder:
    """Create a timer mutation builder.

    Returns:
        TimerMutationBuilder instance
    """
    return TimerMutationBuilder()
