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

## Installation

### From PyPI (Coming Soon)
```bash
pip install workato-platform-cli
```

### From Source
```bash
git clone https://github.com/workato/workato-platform-cli.git
cd workato-platform-cli
pip install -e .
```

### For Development
```bash
# Install uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone https://github.com/workato/workato-platform-cli.git
cd workato-platform-cli
make install-dev
```

## Quick Start

```bash
# Set up your profile and workspace
workato init
workato profiles create --name dev --region us

# List available commands
workato --help

# Explore available connectors
workato connectors list
workato connectors parameters --provider salesforce

# Manage connections
workato connections list
workato connections create-oauth --provider salesforce

# Manage recipes
workato recipes list --folder-id 123
workato recipes validate --project-id 456
workato recipes start --recipe-id 789

# Project operations
workato push --project-id 123
workato pull

# AI agent access to structured documentation
workato guide topics      # (for AI agents)
workato guide search "oauth"  # (for AI agents)
```

## For AI Agents & Developers

This CLI is designed to enable AI agents to assist developers in building Workato assets:

### **Recipe Development Workflow**
1. **Validate Recipes**: `workato recipes validate` to check JSON syntax and structure
2. **Create Connections**: `workato connections create` to set up OAuth authentication
3. **Update Recipe Connections**: `workato recipes update-connection` to link recipes to connections
4. **Deploy**: `workato push` to deploy recipes to Workato
5. **Monitor**: `workato recipes jobs` to track execution

### **AI Agent Capabilities**
- **Recipe Validation**: Catch errors before deployment
- **Connection Management**: Handle OAuth flows automatically
- **Project Synchronization**: Keep local and remote in sync
- **AI Documentation Interface**: `workato guide` provides structured knowledge for AI agents
- **Error Diagnosis**: Detailed error messages and validation feedback

## Key Commands

- `workato init` - Initialize CLI configuration and workspace
- `workato profiles create/use` - Manage multiple environments
- `workato recipes list/validate/start/stop` - Recipe lifecycle management
- `workato connections create-oauth/list` - OAuth connection management
- `workato connectors list/parameters` - Explore available connectors
- `workato push/pull` - Sync projects with Workato workspace
- `workato guide topics/search/content` - AI agent documentation interface

## Use Cases

Perfect for:
- **🤖 AI Agents**: Automated recipe validation, connection management, and troubleshooting assistance
- **👨‍💻 Developers**: Local-first development with git integration and multi-environment support
- **🏢 Teams**: CI/CD pipelines, bulk operations, and standardized workflows
- **🔧 DevOps**: Infrastructure as code, automated deployments, and monitoring

> 📖 **See [resources/use-cases.md](resources/use-cases.md) for detailed scenarios and examples**

## Requirements

- **Python 3.11+** (type hints and modern async support)
- **Workato API token** (from your Workato account settings)
- **Valid Workato account** with API access

## Development

This project uses modern Python tooling for the best developer experience:

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

# See all available commands
make help
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
