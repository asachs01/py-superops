#!/usr/bin/env python3
# # Copyright (c) 2025 Aaron Sachs
# # Licensed under the MIT License.
# # See LICENSE file in the project root for full license information.

"""SuperOps CLI - Command line interface for the py-superops library."""

import argparse
import asyncio
import json
import sys
from typing import Optional

from . import __version__, create_client
from .config import SuperOpsConfig
from .exceptions import SuperOpsError


def get_version() -> str:
    """Get version string."""
    return f"superops-cli {__version__}"


async def test_connection(config: SuperOpsConfig) -> None:
    """Test connection to SuperOps API."""
    try:
        client = create_client(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout,
            debug=config.debug,
        )
        async with client:
            result = await client.test_connection()
            if result.get("connected"):
                print("✅ Successfully connected to SuperOps API")
                print(f"API Version: {result.get('api_version', 'Unknown')}")
                print(f"User: {result.get('user', 'Unknown')}")
            else:
                print("❌ Failed to connect to SuperOps API")
                sys.exit(1)
    except SuperOpsError as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)


async def execute_query(
    config: SuperOpsConfig, query: str, variables: Optional[str] = None
) -> None:
    """Execute a GraphQL query."""
    try:
        query_variables = {}
        if variables:
            query_variables = json.loads(variables)

        client = create_client(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout,
            debug=config.debug,
        )
        async with client:
            result = await client.execute_query(query, variables=query_variables)
            print(json.dumps(result, indent=2))
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in variables: {e}")
        sys.exit(1)
    except SuperOpsError as e:
        print(f"❌ Query failed: {e}")
        sys.exit(1)


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="SuperOps CLI - Command line interface for the py-superops library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  superops-cli --version
  superops-cli test-connection
  superops-cli query "query { clients { id name } }"
  superops-cli query "query GetClient($id: ID!) { client(id: $id) { name } }" --variables '{"id": "123"}'
        """,
    )

    parser.add_argument("--version", action="version", version=get_version())

    parser.add_argument(
        "--api-key",
        help="SuperOps API key (can also be set via SUPEROPS_API_KEY environment variable)",
    )

    parser.add_argument(
        "--base-url",
        help="SuperOps API base URL (can also be set via SUPEROPS_BASE_URL environment variable)",
    )

    parser.add_argument("--debug", action="store_true", help="Enable debug output")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Test connection command
    subparsers.add_parser("test-connection", help="Test connection to SuperOps API")

    # Query command
    query_parser = subparsers.add_parser("query", help="Execute a GraphQL query")
    query_parser.add_argument("query", help="GraphQL query string")
    query_parser.add_argument("--variables", help="Query variables as JSON string")

    return parser


def main() -> None:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()

    # If no command specified, show help
    if not args.command:
        parser.print_help()
        return

    # Create configuration
    config_kwargs = {}
    if args.api_key:
        config_kwargs["api_key"] = args.api_key
    if args.base_url:
        config_kwargs["base_url"] = args.base_url
    if args.debug:
        config_kwargs["debug"] = True

    try:
        if config_kwargs:
            config = SuperOpsConfig(**config_kwargs)
        else:
            config = SuperOpsConfig.from_env()
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)

    # Execute command
    try:
        if args.command == "test-connection":
            asyncio.run(test_connection(config))
        elif args.command == "query":
            asyncio.run(execute_query(config, args.query, args.variables))
        else:
            print(f"❌ Unknown command: {args.command}")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
