# Contributing to py-superops

Thank you for your interest in contributing to py-superops! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

## Code of Conduct

This project adheres to the Contributor Covenant Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to support@superops.com.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- A GitHub account

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/py-superops.git
   cd py-superops
   ```

3. **Set up the development environment**:
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install development dependencies
   pip install -e .[dev]
   ```

4. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

5. **Verify the setup**:
   ```bash
   # Run tests
   pytest

   # Run code quality checks
   pre-commit run --all-files
   ```

## Development Workflow

### Creating a Feature Branch

1. **Create a new branch** from `main`:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code standards
3. **Test your changes** thoroughly
4. **Commit your changes** with clear, descriptive messages
5. **Push to your fork** and create a pull request

### Branch Naming Convention

Use descriptive branch names with prefixes:
- `feature/` - New features
- `bugfix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test improvements

Examples:
- `feature/add-async-client-support`
- `bugfix/fix-authentication-timeout`
- `docs/update-api-examples`

## Code Standards

### Code Style

This project uses several tools to maintain code quality:

- **Black** - Code formatting
- **isort** - Import sorting
- **flake8** - Linting with multiple plugins
- **mypy** - Type checking
- **pydocstyle** - Docstring style checking

All code must pass these checks before being merged.

### Type Hints

- All new code must include proper type hints
- Use `typing` module annotations for Python < 3.10 compatibility
- Generic types should be properly parameterized

Example:
```python
from typing import Dict, List, Optional, Union
from httpx import AsyncClient

async def fetch_data(
    client: AsyncClient,
    endpoint: str,
    params: Optional[Dict[str, Union[str, int]]] = None
) -> List[Dict[str, Any]]:
    """Fetch data from the API endpoint."""
    # Implementation here
```

### Docstrings

Use Google-style docstrings for all public functions, classes, and modules:

```python
def calculate_total(items: List[float], tax_rate: float = 0.1) -> float:
    """Calculate the total cost including tax.

    Args:
        items: List of item costs.
        tax_rate: Tax rate as a decimal. Defaults to 0.1 (10%).

    Returns:
        The total cost including tax.

    Raises:
        ValueError: If tax_rate is negative.

    Example:
        >>> calculate_total([10.0, 20.0], 0.05)
        31.5
    """
    if tax_rate < 0:
        raise ValueError("Tax rate cannot be negative")

    subtotal = sum(items)
    return subtotal * (1 + tax_rate)
```

### Error Handling

- Use specific exception types
- Provide clear error messages
- Log errors appropriately
- Handle async exceptions properly

### Async/Await Guidelines

- Use `async`/`await` consistently
- Properly handle async context managers
- Use `asyncio.gather()` for concurrent operations
- Always close async resources

## Testing

### Test Structure

Tests are organized in the `tests/` directory mirroring the source structure:

```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── fixtures/       # Test fixtures and data
└── conftest.py     # Pytest configuration
```

### Writing Tests

- Write tests for all new features
- Maintain or improve test coverage (minimum 90%)
- Use descriptive test names
- Follow the Arrange-Act-Assert pattern
- Use fixtures for common test data

Example:
```python
import pytest
from unittest.mock import AsyncMock
from py_superops.client import SuperOpsClient

@pytest.fixture
async def mock_client():
    """Create a mock SuperOps client for testing."""
    client = SuperOpsClient(api_key="test-key", base_url="https://test.api")
    client._http_client = AsyncMock()
    return client

@pytest.mark.asyncio
async def test_fetch_devices_success(mock_client):
    """Test successful device fetching."""
    # Arrange
    expected_devices = [{"id": 1, "name": "Device 1"}]
    mock_client._http_client.post.return_value.json.return_value = {
        "data": {"devices": expected_devices}
    }

    # Act
    devices = await mock_client.get_devices()

    # Assert
    assert devices == expected_devices
    mock_client._http_client.post.assert_called_once()
```

### Test Categories

Mark tests with appropriate categories:
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow tests (> 1 second)
- `@pytest.mark.network` - Tests requiring network access

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m "unit"
pytest -m "not slow"

# Run with coverage
pytest --cov=py_superops --cov-report=html

# Run specific test file
pytest tests/unit/test_client.py
```

## Documentation

### API Documentation

- Document all public APIs
- Include usage examples
- Keep examples up to date
- Use type hints that generate good docs

### README Updates

When adding new features, update the README.md with:
- Installation instructions (if changed)
- Usage examples
- Configuration options

### Changelog

Update `CHANGELOG.md` for all changes:
- Follow [Keep a Changelog](https://keepachangelog.com/) format
- Add entries under `## [Unreleased]`
- Use appropriate categories: Added, Changed, Deprecated, Removed, Fixed, Security

## Submitting Changes

### Pre-submission Checklist

Before submitting a pull request, ensure:

- [ ] All tests pass locally
- [ ] Pre-commit hooks pass
- [ ] Code coverage is maintained or improved
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] Type hints are included
- [ ] Commit messages are clear and descriptive

### Pull Request Process

1. **Ensure your branch is up to date**:
   ```bash
   git checkout main
   git pull origin main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Push your changes**:
   ```bash
   git push origin your-feature-branch
   ```

3. **Create a pull request** on GitHub with:
   - Clear title and description
   - Reference to related issues
   - Screenshots (if applicable)
   - Test results

4. **Address review feedback** promptly
5. **Ensure all CI checks pass**

### Commit Message Guidelines

Use clear, descriptive commit messages:

```
type(scope): short description

Longer description if necessary explaining what changed and why.

Fixes #123
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
- `feat(client): add support for async batch operations`
- `fix(auth): handle token refresh race condition`
- `docs(readme): update installation instructions`

## Release Process

Releases are handled by maintainers:

1. **Version Update**: Update version in `src/py_superops/__init__.py`
2. **Changelog**: Move unreleased changes to new version section
3. **Tag**: Create and push version tag
4. **GitHub Release**: Automated via GitHub Actions
5. **PyPI**: Automated publishing via GitHub Actions

### Versioning

We use [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- Breaking changes increment MAJOR
- New features increment MINOR
- Bug fixes increment PATCH

## Getting Help

- **Documentation**: Check existing docs and examples
- **Issues**: Search existing issues on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact support@superops.com for sensitive issues

## Recognition

Contributors are recognized in:
- GitHub contributors list
- Release notes for significant contributions
- Special mentions in documentation

Thank you for contributing to py-superops! 🚀
