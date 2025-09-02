# # Copyright (c) 2024 SuperOps Team
# # Licensed under the MIT License.
# # See LICENSE file in the project root for full license information.

"""Resource managers for SuperOps API operations.

This package provides high-level, Pythonic interfaces for managing SuperOps resources.
Each manager abstracts the complexity of GraphQL operations and provides intuitive
methods for common business operations.

Example:
    ```python
    import asyncio
    from py_superops import SuperOpsClient, SuperOpsConfig

    async def main():
        # Create client
        config = SuperOpsConfig.from_env()
        client = SuperOpsClient(config)

        # Use managers for high-level operations
        async with client:
            # Client management
            active_clients = await client.clients.get_active_clients()

            # Ticket workflow
            overdue_tickets = await client.tickets.get_overdue_tickets()
            for ticket in overdue_tickets['items']:
                await client.tickets.change_priority(
                    ticket.id,
                    TicketPriority.HIGH
                )

            # Asset tracking
            expiring_warranties = await client.assets.get_warranty_expiring_soon(
                days_threshold=30
            )

    asyncio.run(main())
    ```

Available Managers:
    - ClientManager: Client/customer management and workflows
    - TicketManager: Ticket lifecycle and workflow operations
    - AssetManager: Asset tracking and warranty management
    - SiteManager: Site/location management
    - ContactManager: Contact organization and management
    - KnowledgeBaseManager: Knowledge base articles and collections
"""

from .assets import AssetManager
from .base import ResourceManager
from .clients import ClientManager
from .contacts import ContactManager
from .knowledge_base import (
    KnowledgeBaseArticleManager,
    KnowledgeBaseCollectionManager,
    KnowledgeBaseManager,
)
from .sites import SiteManager
from .tickets import TicketManager
from .time_entries import TimeEntriesManager

__all__ = [
    # Base manager
    "ResourceManager",
    # Domain-specific managers
    "ClientManager",
    "TicketManager",
    "AssetManager",
    "SiteManager",
    "ContactManager",
    "KnowledgeBaseManager",
    "KnowledgeBaseArticleManager",
    "KnowledgeBaseCollectionManager",
    "TimeEntriesManager",
]

# Manager registry for dynamic access
MANAGER_REGISTRY = {
    "clients": ClientManager,
    "tickets": TicketManager,
    "assets": AssetManager,
    "sites": SiteManager,
    "contacts": ContactManager,
    "knowledge_base": KnowledgeBaseManager,
    "time_entries": TimeEntriesManager,
}


def get_manager_class(manager_name: str) -> type:
    """Get a manager class by name.

    Args:
        manager_name: Name of the manager ('clients', 'tickets', etc.)

    Returns:
        Manager class

    Raises:
        KeyError: If manager name is not found

    Example:
        ```python
        ClientManagerClass = get_manager_class('clients')
        manager = ClientManagerClass(client)
        ```
    """
    if manager_name not in MANAGER_REGISTRY:
        available = ", ".join(MANAGER_REGISTRY.keys())
        raise KeyError(f"Unknown manager '{manager_name}'. Available: {available}")

    return MANAGER_REGISTRY[manager_name]


def list_available_managers() -> list[str]:
    """Get list of available manager names.

    Returns:
        List of manager names

    Example:
        ```python
        managers = list_available_managers()
        print(f"Available managers: {', '.join(managers)}")
        ```
    """
    return list(MANAGER_REGISTRY.keys())
