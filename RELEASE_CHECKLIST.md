# PyPI Release Checklist for py-superops

This document outlines the steps required to prepare and publish py-superops to PyPI.

## Pre-Release Validation ✅

### Package Structure and Configuration
- [x] **pyproject.toml** is complete and correct
  - Build system configured (hatchling)
  - Project metadata properly set
  - Dependencies correctly specified
  - Entry points defined (superops-cli)
  - Author/maintainer information updated
  - URLs point to correct repository
- [x] **README.md** is properly formatted for PyPI display
- [x] **LICENSE** file exists and is correct
- [x] **CHANGELOG.md** follows Keep a Changelog format
- [x] **CLI module** exists and functions properly

### Package Building and Testing
- [x] **Package builds cleanly** with `python -m build`
  - No build errors or warnings
  - Both wheel (.whl) and source distribution (.tar.gz) created
- [x] **Package structure is correct**
  - All modules included in wheel
  - Entry points properly configured
  - License file included
- [x] **Installation from wheel works**
  - Dependencies resolve correctly
  - Package installs without errors
- [x] **CLI entry point functions**
  - `superops-cli --version` works
  - `superops-cli --help` shows usage
  - Command-line interface is functional
- [x] **PyPI compliance validated**
  - `twine check dist/*` passes all checks
  - Package metadata is complete and valid

### Dependencies and Compatibility
- [x] **Core dependencies are minimal and correct**
  - httpx>=0.24.0,<1.0.0 (HTTP client)
  - pydantic>=2.0.0,<3.0.0 (data validation)
  - pydantic-settings>=2.0.0,<3.0.0 (configuration)
  - typing-extensions>=4.0.0 (for Python <3.10)
- [x] **Python version compatibility**
  - Supports Python 3.8+
  - Version classifiers are correct
- [x] **Optional dependencies properly configured**
  - dev, docs, examples, yaml extras defined

## Release Process

### 1. Version Management
- [ ] Update version in `src/py_superops/__init__.py`
- [ ] Update CHANGELOG.md with new version and release date
- [ ] Commit version changes: `git commit -sam "Release v{version}"`
- [ ] Create and push tag: `git tag v{version} && git push origin v{version}`

### 2. Final Build and Test
```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build package
python -m build

# Validate package
twine check dist/*

# Test installation in clean environment
python -m venv test_env
source test_env/bin/activate
pip install dist/*.whl
superops-cli --version
deactivate
rm -rf test_env
```

### 3. Publish to PyPI

#### Test PyPI (Recommended first)
```bash
# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install -i https://test.pypi.org/simple/ py-superops

# Verify functionality
python -c "from py_superops import __version__; print(__version__)"
superops-cli --version
```

#### Production PyPI
```bash
# Upload to PyPI
twine upload dist/*

# Verify on PyPI
# Visit: https://pypi.org/project/py-superops/

# Test installation from PyPI
pip install py-superops
```

## Post-Release

### 1. Verification
- [ ] Package appears correctly on PyPI
- [ ] Installation works: `pip install py-superops`
- [ ] CLI works after installation: `superops-cli --version`
- [ ] Documentation links are accessible
- [ ] GitHub release created (if using automated releases)

### 2. Communication
- [ ] Update project documentation if needed
- [ ] Announce release (if applicable)
- [ ] Update any dependent projects

## Environment Setup

### Required Tools
```bash
# Install build tools
pip install build twine

# Verify tools are available
python -m build --version
twine --version
```

### PyPI Authentication
Set up PyPI credentials using one of these methods:

#### Option 1: API Token (Recommended)
1. Generate API token at https://pypi.org/manage/account/token/
2. Create `~/.pypirc`:
```ini
[testpypi]
  username = __token__
  password = <your-test-pypi-token>

[pypi]
  username = __token__
  password = <your-pypi-token>
```

#### Option 2: Environment Variables
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=<your-pypi-token>
```

## Common Issues and Solutions

### Build Issues
- **Missing files**: Check `pyproject.toml` includes section
- **Import errors**: Verify all dependencies are specified
- **Version conflicts**: Check dependency version constraints

### Upload Issues
- **Authentication failure**: Verify PyPI credentials
- **File already exists**: Version already published (increment version)
- **Package name conflict**: Name already taken on PyPI

### Installation Issues
- **Missing dependencies**: Check `requires-dist` in metadata
- **Entry point not found**: Verify `[project.scripts]` configuration
- **Import errors**: Check package structure and imports

## Automated Release (Optional)

Consider setting up GitHub Actions for automated releases:
- Triggered on tag push (`v*`)
- Runs tests, builds package, uploads to PyPI
- Creates GitHub release with changelog

## Package Status: READY FOR PYPI ✅

The py-superops package has passed all validation checks and is ready for PyPI publication:

- ✅ Package builds successfully
- ✅ All metadata is complete and valid
- ✅ Dependencies are correctly specified
- ✅ CLI entry point works correctly
- ✅ PyPI compliance validated
- ✅ Installation tested successfully
- ✅ README formatted for PyPI display

**Next Steps:**
1. Choose appropriate version number
2. Update CHANGELOG.md
3. Follow release process above
4. Publish to Test PyPI first, then production PyPI
