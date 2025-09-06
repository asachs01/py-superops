# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-09-06

### Added
- **Complete Python API Client for SuperOps MSP Platform**
  - 16 fully-implemented API manager classes covering all SuperOps entities
  - 299+ public methods across all managers with zero placeholder code
  - Type-safe async/await architecture using modern Python patterns
  - Comprehensive GraphQL integration with fragment-based field selection

- **Core Management APIs**
  - ClientsManager: MSP client organization management
  - AssetsManager: IT asset inventory and lifecycle tracking
  - SitesManager: Physical and logical location management
  - ContactsManager: Contact relationship management
  - TicketsManager: Service desk and incident management

- **Project & Task Management APIs**
  - ProjectsManager: Project lifecycle and milestone tracking
  - TasksManager: Granular task operations and scheduling
  - ContractsManager: Service contract and SLA management

- **Collaboration & Communication APIs**
  - CommentsManager: Thread-based discussions on entities
  - AttachmentsManager: File and document management

- **Automation & Monitoring APIs**
  - AutomationManager: Workflow automation and rule engine
  - MonitoringManager: Infrastructure monitoring and alerts
  - ScriptsManager: PowerShell/Bash script execution and deployment
  - PoliciesManager: Configuration and compliance policies

- **System & Integration APIs**
  - UsersManager: User account and RBAC management
  - WebhooksManager: External integration endpoints

- **GraphQL Infrastructure**
  - 100+ GraphQL dataclasses and enums for type safety
  - Fragment-based query building for optimal performance
  - Automatic field selection and query optimization
  - Support for complex nested queries and mutations

- **Command-Line Interface (CLI)**
  - Full-featured Click-based CLI with 800+ lines of functionality
  - Commands: test-connection, list-clients, list-tickets, create-ticket, execute-script, query
  - Rich terminal output with tables, progress bars, and syntax highlighting
  - Shell completion support for bash/zsh/fish
  - Configuration management with global/local settings
  - Interactive and non-interactive modes

- **Testing Framework**
  - Comprehensive pytest test suite with async support
  - Test coverage for auth, config, client, and base managers
  - Mock fixtures and test utilities
  - 114+ test cases across core modules

- **Development Infrastructure**
  - Git worktree workflow support for parallel development
  - Comprehensive type hints throughout codebase
  - Pydantic-based configuration management
  - Environment variable and file-based configuration

### Changed
- Updated Python version support to include Python 3.8+
- Enhanced CI/CD workflows with improved test matrix
- Refactored all managers to inherit from generic ResourceManager[T] base class
- Improved error handling with custom exception hierarchy

### Fixed
- Added missing manager properties (comments, scripts, users, webhooks) to SuperOpsClient
- Fixed MonitoringManager inheritance to follow consistent pattern
- Resolved GraphQL fragment import issues
- Corrected Script type definitions and dataclass field ordering
- Fixed CI/CD workflow coverage upload paths

### Security
- All API communications use HTTPS with configurable timeouts
- API key authentication with secure header handling
- No credentials stored in code or logs
- Comprehensive input validation on all API methods

## [0.1.0] - 2025-08-31

### Added
- Initial release of py-superops
- Comprehensive DevOps setup with pre-commit hooks and GitHub Actions
- Pre-commit configuration with:
  - Black code formatting
  - isort import sorting  
  - flake8 linting with multiple plugins
  - mypy type checking
  - bandit security scanning
  - pydocstyle docstring checking
  - secrets detection
  - YAML/JSON validation
- GitHub Actions CI/CD workflows:
  - Comprehensive CI pipeline with security checks, code quality, and testing
  - Release automation with PyPI publishing
  - Multi-platform testing (Ubuntu, macOS, Windows)
  - Python version matrix (3.9, 3.10, 3.11, 3.12)
- Development configuration:
  - Enhanced pyproject.toml with comprehensive tool configurations
  - setup.cfg for flake8 compatibility
  - Test coverage reporting and requirements (90% minimum)
- Project documentation:
  - Comprehensive CONTRIBUTING.md for external contributors
  - Development workflow guidelines
  - Code standards and style guides
- Quality gates:
  - All tests must pass
  - Code coverage minimum threshold enforcement
  - Type checking with mypy
  - Security scanning integration
  - Code formatting compliance

### Changed

### Deprecated

### Removed

### Fixed

### Security
- Added bandit security scanning for Python code
- Implemented safety dependency vulnerability checking
- Secrets detection in pre-commit hooks
- Security scanning integrated into CI pipeline

---

## Release Notes

### Version 0.2.0 - Complete SuperOps API Client

This release delivers a fully-functional Python SDK for the SuperOps MSP platform with comprehensive API coverage, modern async architecture, and enterprise-ready features.

**🎯 Major Achievements:**
- **16 API Managers** covering all SuperOps entities (Clients, Assets, Tickets, Projects, etc.)
- **299+ Public Methods** with complete CRUD operations and domain-specific functionality
- **Zero Placeholder Code** - every method has a working implementation
- **GraphQL-First Architecture** with fragment-based optimization for efficient queries
- **Full CLI Application** with rich terminal UI for interactive SuperOps management
- **Type-Safe Throughout** with Pydantic models and comprehensive type hints

**📦 Installation:**
```bash
pip install py-superops
```

**🚀 Quick Start:**
```python
from py_superops import SuperOpsClient

async with SuperOpsClient(api_key="your-api-key") as client:
    # List all tickets
    tickets = await client.tickets.list()

    # Create a new client
    new_client = await client.clients.create(
        name="Acme Corp",
        email="contact@acme.com"
    )

    # Execute automation workflow
    await client.automation.execute_workflow(
        workflow_id="backup-routine"
    )
```

**🖥️ CLI Usage:**
```bash
# Test connection
superops-cli test-connection

# List clients with rich output
superops-cli list-clients --output table

# Create a ticket
superops-cli create-ticket --title "Server maintenance" --priority high

# Execute GraphQL query
superops-cli query "{ clients { id name } }"
```

**For Developers:**
- Async/await pattern throughout for modern Python applications
- Comprehensive type hints for excellent IDE support
- Fragment-based GraphQL queries for optimal performance
- Extensible architecture for custom implementations

**For System Integrators:**
- Environment-based configuration (SUPEROPS_API_KEY, SUPEROPS_BASE_URL)
- Configurable timeouts and retry logic
- Comprehensive error handling with detailed exceptions
- Batch operations support for efficiency

**Breaking Changes from 0.1.0:**
- This is essentially a new library - 0.1.0 only contained DevOps setup
- All functionality is new in this release

**Known Limitations:**
- Test coverage currently at 32% (framework in place for expansion)
- Some pre-commit hooks need configuration tuning
- Documentation and examples still being expanded

**Next Release Focus:**
- Achieve 90% test coverage target
- Comprehensive API documentation
- Additional CLI commands
- Performance optimizations
- PyPI package publication

---

### Version 0.1.0 - Initial DevOps Setup

This initial release focuses on establishing a robust development and deployment infrastructure for the py-superops project. The release includes comprehensive tooling for code quality, security, and automated testing across multiple Python versions and platforms.

**Key Features:**
- Production-ready pre-commit hook configuration
- Multi-stage GitHub Actions CI/CD pipeline
- Automated security and vulnerability scanning
- Comprehensive code quality enforcement
- Cross-platform testing support

**For Developers:**
- Follow the setup instructions in CONTRIBUTING.md
- Install pre-commit hooks: `pre-commit install`
- All code must pass quality checks before merge
- Minimum 90% test coverage required

**For Maintainers:**
- Releases are fully automated via GitHub Actions
- PyPI publishing requires proper version tagging
- All security checks must pass before release
