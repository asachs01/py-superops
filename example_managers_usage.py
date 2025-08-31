#!/usr/bin/env python3
# # Copyright (c) 2024 SuperOps Team
# # Licensed under the MIT License.
# # See LICENSE file in the project root for full license information.

"""Example demonstrating comprehensive usage of SuperOps managers."""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the path so we can import our package
sys.path.insert(0, str(Path(__file__).parent / "src"))

from py_superops import SuperOpsClient, SuperOpsConfig
from py_superops.graphql import AssetStatus, ClientStatus, TicketPriority, TicketStatus


async def demonstrate_client_management(client: SuperOpsClient):
    """Demonstrate client management operations."""
    print("\n📋 Client Management Operations:")
    print("-" * 40)

    try:
        # Get active clients
        print("Getting active clients...")
        active_clients = await client.clients.get_active_clients(page_size=5)
        print(f"✓ Found {len(active_clients['items'])} active clients")

        # Example client operations (commented out since we won't actually create data)
        """
        # Create a new client
        new_client_data = {
            "name": "Example Corp",
            "email": "contact@example.com",
            "phone": "+1-555-0123",
            "address": "123 Business St, City, State 12345"
        }
        new_client = await client.clients.create(new_client_data)
        print(f"✓ Created client: {new_client.name}")

        # Find client by email
        found_client = await client.clients.get_by_email("contact@example.com")
        if found_client:
            print(f"✓ Found client by email: {found_client.name}")

        # Bulk status update
        client_ids = [new_client.id]
        updated_clients = await client.clients.bulk_update_status(
            client_ids, ClientStatus.INACTIVE
        )
        print(f"✓ Updated status for {len(updated_clients)} clients")
        """

    except Exception as e:
        print(f"⚠️ Client operations demo: {e}")


async def demonstrate_ticket_workflow(client: SuperOpsClient):
    """Demonstrate ticket workflow operations."""
    print("\n🎫 Ticket Workflow Operations:")
    print("-" * 40)

    try:
        # Get overdue tickets
        print("Checking for overdue tickets...")
        overdue_tickets = await client.tickets.get_overdue_tickets(page_size=5)
        print(f"✓ Found {len(overdue_tickets['items'])} overdue tickets")

        # Get high priority tickets
        print("Getting high priority tickets...")
        high_priority = await client.tickets.get_high_priority_tickets(page_size=5)
        print(f"✓ Found {len(high_priority['items'])} high priority tickets")

        # Example ticket operations (commented out since we won't actually create data)
        """
        # Create a new ticket
        new_ticket_data = {
            "title": "Password Reset Issue",
            "description": "User cannot reset password via email",
            "client_id": "client_123",
            "priority": TicketPriority.NORMAL.value,
            "status": TicketStatus.OPEN.value
        }
        new_ticket = await client.tickets.create(new_ticket_data)
        print(f"✓ Created ticket: {new_ticket.title}")

        # Assign ticket
        assigned_ticket = await client.tickets.assign_ticket(
            new_ticket.id,
            "technician_456",
            add_comment=True
        )
        print(f"✓ Assigned ticket to technician")

        # Change priority
        escalated_ticket = await client.tickets.change_priority(
            new_ticket.id,
            TicketPriority.HIGH,
            add_comment=True
        )
        print(f"✓ Escalated ticket priority")

        # Add time tracking comment
        comment = await client.tickets.add_comment(
            new_ticket.id,
            "Investigated issue - appears to be email server problem",
            time_spent=30  # 30 minutes
        )
        print(f"✓ Added comment with time tracking")

        # Close ticket with resolution
        resolved_ticket = await client.tickets.change_status(
            new_ticket.id,
            TicketStatus.RESOLVED,
            resolution_notes="Email server configuration fixed"
        )
        print(f"✓ Resolved ticket")
        """

    except Exception as e:
        print(f"⚠️ Ticket workflow demo: {e}")


async def demonstrate_asset_tracking(client: SuperOpsClient):
    """Demonstrate asset tracking operations."""
    print("\n💻 Asset Tracking Operations:")
    print("-" * 40)

    try:
        # Get active assets
        print("Getting active assets...")
        active_assets = await client.assets.get_active_assets(page_size=5)
        print(f"✓ Found {len(active_assets['items'])} active assets")

        # Check warranty status
        print("Checking warranty expiration...")
        expiring_soon = await client.assets.get_warranty_expiring_soon(
            days_threshold=30, page_size=5
        )
        print(f"✓ Found {len(expiring_soon['items'])} assets with warranties expiring in 30 days")

        expired = await client.assets.get_expired_warranty(page_size=5)
        print(f"✓ Found {len(expired['items'])} assets with expired warranties")

        # Example asset operations (commented out since we won't actually create data)
        """
        # Create a new asset
        new_asset_data = {
            "name": "Dell Laptop - Marketing",
            "client_id": "client_123",
            "site_id": "site_456",
            "asset_type": "Laptop",
            "manufacturer": "Dell",
            "model": "Latitude 5520",
            "serial_number": "ABC123DEF456",
            "status": AssetStatus.ACTIVE.value
        }
        new_asset = await client.assets.create(new_asset_data)
        print(f"✓ Created asset: {new_asset.name}")

        # Move asset to maintenance
        maintenance_asset = await client.assets.set_maintenance_mode(new_asset.id)
        print(f"✓ Set asset to maintenance mode")

        # Move asset to different site
        moved_asset = await client.assets.move_to_site(
            new_asset.id,
            "site_789",
            update_location="Conference Room A"
        )
        print(f"✓ Moved asset to new location")
        """

    except Exception as e:
        print(f"⚠️ Asset tracking demo: {e}")


async def demonstrate_site_management(client: SuperOpsClient):
    """Demonstrate site management operations."""
    print("\n🏢 Site Management Operations:")
    print("-" * 40)

    try:
        # Example site operations (commented out since we won't make real API calls)
        """
        # Get sites for a client
        client_sites = await client.sites.get_by_client("client_123")
        print(f"✓ Found {len(client_sites['items'])} sites for client")

        # Create a new site
        new_site_data = {
            "name": "Downtown Office",
            "client_id": "client_123",
            "address": "456 Main St, Downtown, State 12345",
            "timezone": "America/New_York",
            "description": "Main downtown office location"
        }
        new_site = await client.sites.create(new_site_data)
        print(f"✓ Created site: {new_site.name}")

        # Get site statistics
        stats = await client.sites.get_site_statistics(new_site.id)
        print(f"✓ Site has {stats['assets']['total']} assets and {stats['tickets']['total']} tickets")

        # Update timezone
        updated_site = await client.sites.set_timezone(new_site.id, "America/Los_Angeles")
        print(f"✓ Updated site timezone")
        """

        print("⚠️ Site operations demo (simulated - no actual API calls)")

    except Exception as e:
        print(f"⚠️ Site management demo: {e}")


async def demonstrate_contact_management(client: SuperOpsClient):
    """Demonstrate contact management operations."""
    print("\n👥 Contact Management Operations:")
    print("-" * 40)

    try:
        # Example contact operations (commented out since we won't make real API calls)
        """
        # Get contacts for a client
        client_contacts = await client.contacts.get_by_client("client_123")
        print(f"✓ Found {len(client_contacts['items'])} contacts for client")

        # Create a new contact
        new_contact_data = {
            "client_id": "client_123",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "+1-555-0199",
            "title": "IT Manager",
            "is_primary": True
        }
        new_contact = await client.contacts.create(new_contact_data)
        print(f"✓ Created contact: {new_contact.first_name} {new_contact.last_name}")

        # Find contact by email
        found_contact = await client.contacts.get_by_email("john.doe@example.com")
        if found_contact:
            print(f"✓ Found contact by email: {found_contact.first_name} {found_contact.last_name}")

        # Set as primary contact
        primary_contact = await client.contacts.set_primary_contact(new_contact.id)
        print(f"✓ Set as primary contact")

        # Get statistics
        stats = await client.contacts.get_contact_statistics_for_client("client_123")
        print(f"✓ Client has {stats['total_contacts']} total contacts")
        """

        print("⚠️ Contact operations demo (simulated - no actual API calls)")

    except Exception as e:
        print(f"⚠️ Contact management demo: {e}")


async def demonstrate_knowledge_base(client: SuperOpsClient):
    """Demonstrate knowledge base operations."""
    print("\n📚 Knowledge Base Operations:")
    print("-" * 40)

    try:
        # Example knowledge base operations (commented out since we won't make real API calls)
        """
        # Search across knowledge base
        search_results = await client.knowledge_base.search_all(
            "password reset",
            page_size=5,
            published_only=True
        )
        articles_found = len(search_results['articles']['items'])
        collections_found = len(search_results['collections']['items'])
        print(f"✓ Found {articles_found} articles and {collections_found} collections")

        # Get public collections
        public_collections = await client.knowledge_base.collections.get_public_collections()
        print(f"✓ Found {len(public_collections['items'])} public collections")

        # Get featured articles
        featured = await client.knowledge_base.articles.get_featured_articles(page_size=5)
        print(f"✓ Found {len(featured['items'])} featured articles")

        # Create new collection
        collection_data = {
            "name": "Network Troubleshooting",
            "description": "Articles related to network connectivity issues",
            "is_public": True
        }
        new_collection = await client.knowledge_base.collections.create(collection_data)
        print(f"✓ Created collection: {new_collection.name}")

        # Create new article
        article_data = {
            "collection_id": new_collection.id,
            "title": "How to Reset Network Settings",
            "content": "Step-by-step guide to reset network settings...",
            "author_id": "user_123",
            "summary": "Quick guide for network reset procedures",
            "is_published": True,
            "tags": ["network", "troubleshooting", "reset"]
        }
        new_article = await client.knowledge_base.articles.create(article_data)
        print(f"✓ Created article: {new_article.title}")

        # Feature the article
        featured_article = await client.knowledge_base.articles.feature_article(new_article.id)
        print(f"✓ Featured the article")
        """

        print("⚠️ Knowledge base operations demo (simulated - no actual API calls)")

    except Exception as e:
        print(f"⚠️ Knowledge base demo: {e}")


async def main():
    """Run comprehensive managers demonstration."""
    print("=" * 60)
    print("SuperOps Managers Comprehensive Usage Example")
    print("=" * 60)
    print("\nThis example demonstrates how to use SuperOps managers for")
    print("common business operations and workflows.")
    print("\nNote: This demo uses simulated operations to avoid making")
    print("actual API calls. In a real application, uncomment the")
    print("relevant code sections.")

    # Create a test configuration
    config = SuperOpsConfig(
        api_key="demo-api-key-1234567890",
        base_url="https://api.superops.com/graphql",
        timeout=30.0,
        debug=False,  # Set to True to see detailed logging
    )

    # Create client and demonstrate operations
    client = SuperOpsClient(config)

    try:
        # Test connection (this would fail in real usage without valid credentials)
        print("\n🔌 Testing connection...")
        try:
            # connection_info = await client.test_connection()
            # print(f"✅ Connected: {connection_info['connected']}")
            print("⚠️ Connection test skipped (demo mode)")
        except Exception:
            print("⚠️ Connection test skipped (no valid credentials)")

        # Demonstrate each manager
        await demonstrate_client_management(client)
        await demonstrate_ticket_workflow(client)
        await demonstrate_asset_tracking(client)
        await demonstrate_site_management(client)
        await demonstrate_contact_management(client)
        await demonstrate_knowledge_base(client)

        # Show cross-manager workflow example
        print("\n🔄 Cross-Manager Workflow Example:")
        print("-" * 40)
        print("In a real application, you might chain operations like:")
        print("1. Find clients with expiring asset warranties")
        print("2. Create tickets for warranty renewal")
        print("3. Assign tickets to appropriate technicians")
        print("4. Add knowledge base articles for procedures")
        print("5. Update client contacts with notifications")
        print("⚠️ Cross-workflow demo (simulated)")

        print("\n" + "=" * 60)
        print("🎉 Demonstration completed successfully!")
        print("✨ SuperOps managers provide intuitive, high-level interfaces")
        print("   for all your SuperOps API operations.")

        return 0

    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
