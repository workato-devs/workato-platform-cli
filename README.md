# Workato Platform CLI

A modern, type-safe command-line interface for the Workato API, designed for automation and AI agent interaction. **Perfect for AI agents helping developers build, validate, and manage Workato recipes, connections, and projects.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Type Checked](https://img.shields.io/badge/type--checked-mypy-blue.svg)](https://mypy.readthedocs.io/)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-black.svg)](https://docs.astral.sh/ruff/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Project Management**: Create, push, pull, and manage Workato projects
- **Recipe Operations**: Validate, start, stop, and manage recipes
- **Connection Management**: Create and manage OAuth connections
- **API Integration**: Manage API clients, collections, and endpoints
- **AI Agent Support**: Built-in documentation and guide system

# Quick Start Guide

Get the Workato CLI running in 5 minutes.

## Prerequisites

- Python 3.11+
- Workato account with API token

### Getting Your API Token
1. Log into your Workato account
1. Navigate to **Workspace Admin** → **API clients**
1. Click **Create API client**
1. **Grant the necessary permissions** - For standard development, you'll need:
   - Workspace Details (Get details)
   - Projects & Folders (List, Create)
   - Recipes (List, Create, Update, Start, Stop)
   - Connections (List, Create, Update)
   - Recipe Lifecycle Management (all permissions)
   - Export Manifests (Create, Show, Get folder assets)

   See [PERMISSIONS.md](/docs/PERMISSIONS.md) for the complete list of available scopes and recommendations.
1. Fill out information about the client, click **Create client**
1. Copy the generated token (starts with `wrkatrial-` for trial accounts or `wrkprod-` for production)

## Installation

### From PyPI (Coming Soon)
```bash
pip install workato-platform-cli
```

### From Source
```bash
git clone https://github.com/workato-devs/workato-platform-cli.git
cd workato-platform-cli
make install
```

Having issues? See [DEVELOPER_GUIDE.md](/docs/DEVELOPER_GUIDE.md) for troubleshooting.

## Setup

```bash
# Initialize CLI (will prompt for API token and region)
workato init

# Verify your workspace
workato workspace
```


## First Commands

```bash
# List available commands
workato --help

# List your recipes
workato recipes list

# List your connections
workato connections list

# Check project status
workato workspace
```

## Next Steps

- **Need detailed commands?** → See [COMMAND_REFERENCE.md](/docs/COMMAND_REFERENCE.md)
- **Want real-world examples?** → See [USE_CASES.md](/docs/USE_CASES.md)
- **Looking for sample recipes?** → See [examples/](/docs/examples/)
- **Setting up API token permissions?** → See [PERMISSIONS.md](/docs/PERMISSIONS.md)
- **Installation issues?** → See [DEVELOPER_GUIDE.md](/docs/DEVELOPER_GUIDE.md)
- **Looking for all documentation?** → See [INDEX.md](/docs/INDEX.md)


## Quick Recipe Workflow

```bash
# 1. Validate a recipe file
workato recipes validate --path ./my-recipe.json

# 2. Push changes to Workato
workato push

# 3. Pull latest from remote
workato pull
```

You're ready to go!


## Contributing to the CLI

These commands are for CLI maintainers and contributors, not for developers using the CLI to build Workato integrations.

### For Development
```bash
# Setup (with uv - recommended)
make install-dev

# Run all checks
make check          # linting, formatting, type checking
make test          # run tests
make test-cov      # run tests with coverage

# Development workflow
make format        # auto-format code
make lint         # check code quality
make build        # build distribution packages
```


### Tech Stack
- **🐍 Python 3.11+** with full type annotations
- **⚡ uv** for fast dependency management
- **🔍 mypy** for static type checking
- **🧹 ruff** for linting and formatting
- **✅ pytest** for testing
- **🔧 pre-commit** for git hooks

## License

MIT License
