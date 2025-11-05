# Quick Start Guide

Get the Workato CLI running in 5 minutes.

## Prerequisites

- Python 3.11+
- Workato account with API token

### Getting Your API Token

1. Log into your Workato account
1. Navigate to **Workspace Admin** → **API clients**
1. Click **Create API client**
1. Fill out information about the client, click **Create client**
1. Copy the generated token (starts with `wrkatrial-` for trial accounts or `wrkprod-` for production)

## Installation

There are multiple methods of installing Python packages, depending on how your local environment is setup. Below we cover a few possible methods based on common configurations.

### Standard Installation - Try this first (Mac/Windows/Linux)

```bash
python3 --version # Ensure your Python version is >= 3.11
pip install workato-platform-cli
workato --version  # Verify installation
```

### Homebrew (Mac)

Workato-platform-cli is not available in Homebrew yet. If your Python versions are managed in Homebrew, use the following method.

```bash
python3 --version # Ensure your Python version is >= 3.11
brew install pipx
pipx install workato-platform-cli
workato --version  # Verify installation
```

### Alternative Installation

Workato recommends using [UV](https://docs.astral.sh/uv/) to install and manage alternative versions of Python.

Install UV [Other Install Options](https://docs.astral.sh/uv/getting-started/installation/)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install
uv pip install workato-platform-cli
workato --version  # Verify installation
```

Having issues? See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for troubleshooting.

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

- **Need detailed commands?** → See [COMMAND_REFERENCE.md](COMMAND_REFERENCE.md)
- **Want real-world examples?** → See [USE_CASES.md](USE_CASES.md)
- **Looking for sample recipes?** → See [examples/](examples/)
- **Installation issues?** → See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)

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
