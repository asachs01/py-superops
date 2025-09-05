# CI/CD Setup Guide

This document outlines the required configuration for the GitHub Actions workflows in this repository.

## Required Secrets

### Repository Secrets (Settings → Secrets and variables → Actions)

#### Required for CI/CD Operations:
- `CODECOV_TOKEN` - Token for uploading coverage reports to Codecov
- `SUPEROPS_API_KEY` - API key for integration tests (if applicable)  
- `SUPEROPS_API_URL` - API URL for integration tests (if applicable)

#### Required for Release Operations:
The release workflow uses GitHub's trusted publishing to PyPI, which requires:
1. Setting up the PyPI project for trusted publishing
2. Configuring the `pypi` environment in repository settings
3. No additional secrets needed (uses OIDC)

For TestPyPI (pre-releases):
1. Setting up the TestPyPI project for trusted publishing
2. Configuring the `testpypi` environment in repository settings

## Environment Configuration

### PyPI Environments

#### Production PyPI (Environment: `pypi`)
- **Environment URL**: `https://pypi.org/p/py-superops`
- **Required for**: Production releases
- **Protection rules**: Require reviewers for production releases
- **Trusted publishing**: Configure with PyPI project settings

#### Test PyPI (Environment: `testpypi`)  
- **Environment URL**: `https://test.pypi.org/p/py-superops`
- **Required for**: Pre-release testing
- **Trusted publishing**: Configure with TestPyPI project settings

## Workflow Triggers

### CI Workflow (`ci.yml`)
- **Triggers**: Push to `main`/`develop`, Pull Requests, Manual dispatch
- **Jobs**: Security checks, code quality, tests (matrix), integration tests, build, docs, benchmarks
- **Matrix**: Python 3.8-3.12 on Ubuntu, macOS, Windows

### Release Workflow (`release.yml`)
- **Triggers**: Published releases, Manual dispatch with version input
- **Jobs**: Validate release, build artifacts, create GitHub release, publish to PyPI
- **Requires**: All CI checks to pass

### Security Workflow (`security.yml`)  
- **Triggers**: Push to `main`/`develop`, Pull Requests, Daily schedule (2 AM UTC), Manual dispatch
- **Jobs**: CodeQL analysis, dependency review, security scanning, license compliance, SBOM generation

## Pre-commit Hooks

The repository uses pre-commit hooks for code quality. Install with:

```bash
pip install pre-commit
pre-commit install
```

## Local Development

### Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install development dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

### Running Tests Locally
```bash
# Run all tests
pytest

# Run specific test categories
pytest -m "unit"
pytest -m "integration"
pytest -m "not slow"

# Run with coverage
pytest --cov=py_superops --cov-report=html
```

### Code Quality Checks
```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint code  
flake8 src/ tests/
mypy src/

# Security scan
bandit -r src/
safety check
```

## Troubleshooting

### Common Issues

1. **Coverage upload fails**: Ensure `CODECOV_TOKEN` is set correctly
2. **PyPI publish fails**: Verify trusted publishing is configured properly
3. **Integration tests fail**: Check `SUPEROPS_API_KEY` and `SUPEROPS_API_URL` secrets
4. **Security scans fail**: Review and update security baselines if needed

### Workflow Dependencies

The workflows are designed with proper dependencies:
- Release workflow requires CI success
- Security workflow runs independently  
- Integration tests only run on push/manual dispatch (not PRs)

### Performance Optimizations

- Pip caching enabled on all Python setup steps
- Matrix builds exclude some combinations to reduce resource usage
- Parallel test execution with pytest-xdist
- Artifacts uploaded for debugging failed runs

## Maintenance

### Regular Tasks
- Review and update action versions monthly
- Update security tool versions quarterly  
- Review and update Python version matrix annually
- Update dependency pins in pre-commit config

### Security Updates
- Monitor security alerts from GitHub/dependabot
- Review SARIF uploads in Security tab
- Update security baselines as needed
- Review license compliance reports
