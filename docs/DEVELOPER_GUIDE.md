# Developer Getting Started Guide

## Getting Started

## Prerequisites

- Python 3.11+
- Workato account with API token
- Git (optional, for version control)

### Getting Your API Token
1. Log into your Workato account
1. Navigate to **Workspace Admin** → **API clients**
1. Click **Create API client**
1. Fill out information about the client, click **Create client**
1. Copy the generated token (starts with `wrkatrial-` for trial accounts or `wrkprod-` for production)

## Installation Options

### Standard Method
```bash
make install
```

## Initial Setup
```bash
# Initialize CLI configuration (sets up API credentials)
workato init

# Verify installation and see available commands
workato --help
```

## Key Development Workflow
1. **Initialize** - Configure API credentials with `workato init`
2. **Manage Projects** - Use `workato project list` and `workato project use <name>`
3. **Build Recipes** - Develop JSON recipe files locally
4. **Validate** - Run `workato recipes validate` to check syntax
5. **Setup Connections** - Create OAuth connections with `workato connections create`
6. **Deploy** - Push changes with `workato push`
7. **Monitor** - Track execution with `workato recipes jobs`

## Project Structure
- `workato_platform/` - Main package with API client and utilities
- `workato_platform/cli/commands/` - Individual CLI command implementations
- `workato_platform/client/` - API client and data models
- `setup.py` - Package configuration with dependencies (click, requests, inquirer, pydantic)

This CLI is specifically designed for AI-assisted development of Workato automation recipes, providing validation, connection management, and deployment capabilities.

## Common Issues & Solutions

### Installation Issues

**Python Version Error**
```
ERROR: Python 3.11+ required
```
**Solution:** Update Python to version 3.11 or higher:
```bash
python --version  # Check current version
# Install Python 3.11+ from python.org or your package manager
```

**Package Installation Fails**
```bash
pip install -e .
# If this fails with externally-managed-environment error, use virtual environment:
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -e .
```

### Authentication Issues

**API Credentials Error**
```
ERROR: Could not resolve API credentials
```
**Solution:** Run the initialization command:
```bash
workato init
# Follow prompts to enter your API token from the Prerequisites section above
```

### Command Not Found

**"workato: command not found"**
**Solution:** Ensure proper installation:
```bash
# Check if installed correctly:
pip show workato-platform-cli

# If command still not found, try running directly:
python -m workato_platform.cli.main --help
```

## Contributing to the CLI

If you want to contribute to the Workato CLI codebase itself, use these development commands:

### Development Commands
```bash
make test      # Run tests and check code style
```

These commands are for CLI maintainers and contributors, not for developers using the CLI to build Workato integrations.
