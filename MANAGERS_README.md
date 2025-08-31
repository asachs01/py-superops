# SuperOps Resource Managers

This document describes the high-level resource managers that provide Pythonic interfaces for SuperOps API operations.

## Overview

The SuperOps Python client includes domain-specific managers that abstract GraphQL complexity and provide intuitive methods for common business operations. Each manager handles a specific type of resource and includes both basic CRUD operations and specialized business logic.

## Available Managers

### ClientManager
Manages SuperOps clients (customers) and their related operations.

**Key Features:**
- Client lifecycle management
- Status updates and workflows  
- Contact and site relationship management
- Bulk operations for efficiency

**Common Operations:**
```python
# Get active clients
active_clients = await client.clients.get_active_clients(page_size=50)

# Find client by email
customer = await client.clients.get_by_email("admin@example.com")

# Activate/deactivate clients
await client.clients.activate_client(client_id)
await client.clients.deactivate_client(client_id)

# Bulk status updates
await client.clients.bulk_update_status(client_ids, ClientStatus.ACTIVE)

# Tag management
await client.clients.add_tag(client_id, "premium")
await client.clients.remove_tag(client_id, "trial")
```

### TicketManager  
Manages support tickets and their complete lifecycle.

**Key Features:**
- Ticket workflow and status management
- Assignment and escalation
- Time tracking and comments
- SLA monitoring and reporting

**Common Operations:**
```python
# Get overdue tickets
overdue = await client.tickets.get_overdue_tickets()

# Assign ticket to technician
await client.tickets.assign_ticket(ticket_id, technician_id)

# Change ticket status with automatic comments
await client.tickets.change_status(
    ticket_id,
    TicketStatus.IN_PROGRESS,
    add_comment=True
)

# Add time-tracked comment
await client.tickets.add_comment(
    ticket_id,
    "Diagnosed network connectivity issue",
    time_spent=45  # minutes
)

# Bulk operations
await client.tickets.bulk_assign(ticket_ids, technician_id)
```

### AssetManager
Manages IT assets and equipment tracking.

**Key Features:**
- Asset lifecycle and status management
- Warranty tracking and expiration alerts
- Location and site management
- Maintenance scheduling

**Common Operations:**
```python
# Get assets by client
client_assets = await client.assets.get_by_client(client_id)

# Check warranty status
expiring_soon = await client.assets.get_warranty_expiring_soon(days_threshold=30)
expired = await client.assets.get_expired_warranty()

# Asset status management
await client.assets.activate_asset(asset_id)
await client.assets.set_maintenance_mode(asset_id)
await client.assets.retire_asset(asset_id)

# Move asset between sites
await client.assets.move_to_site(asset_id, new_site_id, "Conference Room A")

# Bulk status updates
await client.assets.bulk_update_status(asset_ids, AssetStatus.ACTIVE)
```

### SiteManager
Manages client sites and locations.

**Key Features:**
- Site organization and hierarchy
- Geographic and timezone management
- Asset and contact relationships
- Site-specific statistics

**Common Operations:**
```python
# Get sites for a client
client_sites = await client.sites.get_by_client(client_id)

# Find site by name
site = await client.sites.get_by_name("Main Office", client_id)

# Timezone management
await client.sites.set_timezone(site_id, "America/New_York")
await client.sites.bulk_update_timezone(site_ids, "America/Los_Angeles")

# Get comprehensive site statistics
stats = await client.sites.get_site_statistics(site_id)
print(f"Site has {stats['assets']['total']} assets")

# Address management
await client.sites.update_address(site_id, "123 New Address St")
```

### ContactManager
Manages customer contacts and relationships.

**Key Features:**
- Contact organization by client
- Primary contact designation
- Role and title management
- Communication preferences

**Common Operations:**
```python
# Get contacts for a client
contacts = await client.contacts.get_by_client(client_id)

# Find contact by email
contact = await client.contacts.get_by_email("admin@client.com")

# Primary contact management
await client.contacts.set_primary_contact(contact_id)
await client.contacts.unset_primary_contact(contact_id)

# Update contact information
await client.contacts.update_contact_info(
    contact_id,
    email="new@email.com",
    phone="+1-555-0199",
    title="Senior IT Manager"
)

# Get contact statistics
stats = await client.contacts.get_contact_statistics_for_client(client_id)
```

### KnowledgeBaseManager
Manages knowledge base articles and collections.

**Key Features:**
- Article and collection organization
- Publishing and visibility control
- Search across all content
- View tracking and analytics

**Common Operations:**
```python
# Search across knowledge base
results = await client.knowledge_base.search_all(
    "password reset",
    published_only=True
)

# Work with collections
collections = await client.knowledge_base.collections.get_public_collections()
await client.knowledge_base.collections.make_public(collection_id)

# Article management
featured = await client.knowledge_base.articles.get_featured_articles()
await client.knowledge_base.articles.publish_article(article_id)
await client.knowledge_base.articles.feature_article(article_id)

# View tracking
await client.knowledge_base.articles.increment_view_count(article_id)

# Tag management
await client.knowledge_base.articles.add_tag(article_id, "troubleshooting")
```

## Error Handling

All managers use consistent error handling patterns:

```python
from py_superops.exceptions import (
    SuperOpsAPIError,
    SuperOpsValidationError,
    SuperOpsResourceNotFoundError
)

try:
    client_data = await client.clients.get(client_id)
except SuperOpsResourceNotFoundError:
    print("Client not found")
except SuperOpsValidationError as e:
    print(f"Invalid parameters: {e}")
except SuperOpsAPIError as e:
    print(f"API error: {e}")
```

## Pagination

All list operations support pagination:

```python
# Basic pagination
page_1 = await client.tickets.get_by_status(
    TicketStatus.OPEN,
    page=1,
    page_size=25
)

# Check for more pages
if page_1["pagination"]["hasNextPage"]:
    page_2 = await client.tickets.get_by_status(
        TicketStatus.OPEN,
        page=2,
        page_size=25
    )

# Process all pages
page = 1
while True:
    result = await client.clients.get_active_clients(
        page=page,
        page_size=50
    )

    # Process items
    for client_item in result["items"]:
        print(f"Client: {client_item.name}")

    # Check if we need to continue
    if not result["pagination"]["hasNextPage"]:
        break
    page += 1
```

## Filtering and Sorting

Most list operations support filtering and sorting:

```python
# Filtered results
high_priority_tickets = await client.tickets.get_by_status(
    TicketStatus.OPEN,
    sort_by="created_at",
    sort_order="desc"  # newest first
)

# Custom date filters (implementation depends on specific manager)
recent_assets = await client.assets.get_by_client(
    client_id,
    sort_by="created_at",
    sort_order="desc"
)
```

## Bulk Operations

Many managers support bulk operations for efficiency:

```python
# Bulk ticket assignment
updated_tickets = await client.tickets.bulk_assign(
    ticket_ids=["t1", "t2", "t3"],
    assignee_id="tech_123"
)

# Bulk status updates
updated_clients = await client.clients.bulk_update_status(
    client_ids=["c1", "c2", "c3"],
    status=ClientStatus.ACTIVE
)

# Process results
successful_updates = len(updated_tickets)
print(f"Successfully updated {successful_updates} tickets")
```

## Advanced Workflows

Combine multiple managers for complex workflows:

```python
async def escalate_overdue_tickets():
    """Example workflow: Escalate overdue tickets."""

    # Get overdue tickets
    overdue = await client.tickets.get_overdue_tickets()

    for ticket in overdue["items"]:
        # Escalate priority
        await client.tickets.change_priority(
            ticket.id,
            TicketPriority.HIGH,
            add_comment=True,
            comment_text="Auto-escalated due to overdue status"
        )

        # Get client information
        ticket_client = await client.clients.get(ticket.client_id)

        # Find primary contact
        contacts = await client.contacts.get_by_client(ticket.client_id)
        primary_contacts = [c for c in contacts["items"] if c.is_primary]

        if primary_contacts:
            print(f"Escalated ticket {ticket.title} for {ticket_client.name}")


async def warranty_renewal_workflow():
    """Example workflow: Create tickets for expiring warranties."""

    # Find assets with warranties expiring soon
    expiring = await client.assets.get_warranty_expiring_soon(days_threshold=30)

    for asset in expiring["items"]:
        # Get asset client
        asset_client = await client.clients.get(asset.client_id)

        # Create renewal ticket
        ticket_data = {
            "title": f"Warranty Renewal Required: {asset.name}",
            "description": f"Asset warranty expires on {asset.warranty_expiry}",
            "client_id": asset.client_id,
            "asset_id": asset.id,
            "priority": TicketPriority.NORMAL.value,
            "tags": ["warranty", "renewal"]
        }

        new_ticket = await client.tickets.create(ticket_data)
        print(f"Created warranty renewal ticket: {new_ticket.id}")
```

## Best Practices

### 1. Use Context Managers
Always use the client within an async context manager:

```python
async with SuperOpsClient(config) as client:
    # Your operations here
    pass
```

### 2. Handle Errors Gracefully  
Always wrap API calls in try-except blocks:

```python
try:
    result = await client.tickets.get_overdue_tickets()
    # Process result
except SuperOpsAPIError as e:
    logger.error(f"Failed to get overdue tickets: {e}")
    # Handle error appropriately
```

### 3. Use Bulk Operations
When processing multiple items, use bulk operations when available:

```python
# Good: Bulk operation
await client.tickets.bulk_assign(ticket_ids, technician_id)

# Avoid: Individual operations in loop
for ticket_id in ticket_ids:
    await client.tickets.assign_ticket(ticket_id, technician_id)
```

### 4. Implement Pagination
Always handle pagination for large datasets:

```python
async def process_all_clients():
    page = 1
    while True:
        result = await client.clients.get_active_clients(
            page=page,
            page_size=100
        )

        # Process page
        for client_item in result["items"]:
            # Process each client
            pass

        if not result["pagination"]["hasNextPage"]:
            break
        page += 1
```

### 5. Use Type Hints
Leverage the built-in type safety:

```python
from py_superops.graphql import TicketStatus, TicketPriority

async def handle_urgent_tickets():
    urgent_tickets = await client.tickets.get_by_status(
        TicketStatus.OPEN  # Type-safe enum
    )
```

This completes the comprehensive resource manager implementation for the SuperOps Python client! The managers provide intuitive, high-level interfaces that abstract GraphQL complexity while maintaining all the power and flexibility of the underlying API.
