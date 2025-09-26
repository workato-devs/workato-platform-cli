# Workato CLI Command Reference

Complete reference for all CLI commands and options.

## Installation & Setup

```bash
# Install
pip install -e .

# Initialize
workato init

# Check status
workato workspace
```

## Core Commands

### Project Management
```bash
workato init                        # Initialize CLI configuration
workato workspace                   # Show current workspace info
workato pull                       # Pull latest from remote
workato push [--restart-recipes]   # Push local changes
```

### Recipe Management
```bash
workato recipes list [--folder-id ID] [--running] [--page N]
workato recipes validate --path FILE
workato recipes start --id ID
workato recipes stop --id ID
workato recipes update-connection RECIPE_ID --adapter-name NAME --connection-id ID
```

### Connection Management
```bash
workato connections list [--folder-id ID]
workato connections create --provider PROVIDER --name NAME
workato connections create-oauth --parent-id ID
workato connections update --connection-id ID --name NAME
workato connections get-oauth-url --id ID
```

### Connectors
```bash
workato connectors list
workato connectors parameters --provider PROVIDER
```

### API Collections
```bash
workato api-collections create --format FORMAT --content PATH --name NAME
# Formats: json, yaml, url
```

### Profiles
```bash
workato init                       # Create new profile interactively
workato profiles list
workato profiles use NAME
workato profiles status
```

### Documentation
```bash
workato guide topics              # List available topics
workato guide search QUERY        # Search documentation
workato guide content TOPIC       # Show topic content
```

## Common Options

- `--help` - Show help for any command
- `--profile NAME` - Use specific profile
- `--page N --per-page N` - Pagination for list commands
- `--folder-id ID` - Filter by folder

## Examples

### Development Workflow
```bash
# Setup
workato init  # Creates profile interactively

# Development
workato recipes validate --path ./recipe.json
workato push --restart-recipes
workato recipes list --running

# Switch environments
workato profiles use production
workato pull
```

### Recipe Management
```bash
# List and filter recipes
workato recipes list --folder-id 123
workato recipes list --running --per-page 10

# Manage recipe lifecycle
workato recipes start --id 456
workato recipes stop --id 456
```

### Connection Setup
```bash
# Create connections
workato connections create --provider salesforce --name "Production SF"
workato connections create-oauth --parent-id 789

# Get OAuth URL for authentication
workato connections get-oauth-url --id 789
```

## Environment Support

**Trial Accounts:** Use `wrkatrial-` tokens with `https://app.trial.workato.com/api`
**Production Accounts:** Use `wrkprod-` tokens with `https://www.workato.com/api`

## Requirements

- Python 3.11+
- Valid Workato account and API token
- Network access to Workato API endpoints

For setup and installation issues, see [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md).
