# Recipe Fundamentals

## Overview
A Workato recipe is a JSON object that defines an automation workflow. Recipes consist of a series of connected blocks that execute sequentially, with each block performing a specific function.

## Core Recipe Structure

### Basic Recipe JSON
```json
{
  "name": "Recipe Name",
  "description": "Recipe description",
  "version": 3,
  "private": true,
  "concurrency": 1,
  "code": {
    "number": 0,
    "provider": "connector_name",
    "name": "trigger_or_action_name",
    "as": "unique_identifier",
    "keyword": "trigger",
    "input": { /* configuration */ },
    "block": [ /* child steps */ ]
  },
  "config": [ /* connection configurations */ ]
}
```

### Key Recipe Attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `name` | ✅ | Human-readable recipe name |
| `description` | ❌ | Recipe description |
| `version` | ❌ | Recipe version, updated automatically by the server |
| `private` | ❌ | Whether recipe is private (default: true) |
| `concurrency` | ❌ | Number of concurrent executions (default: 1) |
| `code` | ✅ | Main recipe logic container |
| `config` | ✅ | Connection configurations |

## Recipe Code Structure

### Code Container
The `code` object contains the main recipe logic:

```json
"code": {
  "number": 0,                    // Block number (0 = root)
  "provider": "connector_name",   // Which connector to use
  "name": "action_name",          // Specific action/trigger name
  "as": "unique_id",             // Unique identifier for this block
  "keyword": "trigger",           // "trigger" or "action"
  "input": { /* config */ },     // Block configuration
  "block": [ /* child blocks */ ] // Child execution blocks
}
```

### Block Numbering
- **Block 0**: Root block (must be a trigger)
- **Block 1+**: Child blocks (must be actions)
- Numbers must be sequential and unique within the recipe

### Block Keywords
Only two keywords exist:
- **`trigger`**: Initiates the recipe execution (only in block 0)
- **`action`**: Performs a specific operation (blocks 1+)

## Provider System

### Provider Types
1. **Platform Connectors**: Built-in integrations (e.g., `jira`, `google_drive`, `slack`)
2. **Custom Connectors**: User-created integrations
3. **Workato Built-ins**: Special providers like `workato_recipe_function`, `workato_api_platform`

### Finding Available Providers
```bash
# List all platform connectors with metadata
workato connectors list --platform

# List custom connectors
workato connectors list --custom
```

### Finding Available Actions/Triggers
```bash
# Platform connectors include metadata in the list command
workato connectors list --platform

# For custom connectors, examine the connector code
workato connectors code --id {connector_id}
```

## Recipe Types

### Recipe Functions
- **Provider**: `workato_recipe_function`
- **Purpose**: Reusable functions that can be called by other recipes
- **Structure**: Has input parameters and returns results
- **Usage**: Called via `call_recipe` action or used as a trigger

### API Endpoints
- **Provider**: `workato_api_platform`
- **Purpose**: Expose recipes as HTTP endpoints
- **Structure**: Receives HTTP requests and returns responses
- **Usage**: External systems can trigger via HTTP calls

### Standard Recipes
- **Purpose**: Direct automation workflows
- **Structure**: Standard trigger → action → action flow
- **Usage**: Scheduled, webhook-triggered, or manually executed

## Data Flow

### Execution Order
1. **Trigger fires** (block 0)
2. **Actions execute sequentially** (blocks 1, 2, 3...)
3. **Data flows** from one block to the next
4. **Recipe completes** when all blocks finish

### Data Reference Pattern
Data from previous blocks is referenced using data pills:
```json
"#{_dp('data.{provider}.{as}.{data_path}')}"
```

Where:
- `{provider}` = Provider name of the source block
- `{as}` = The "as" value from the source block
- `{data_path}` = Path to specific data field

## Connection Configuration

### Config Array
The `config` array defines connections needed by the recipe:

```json
"config": [
  {
    "keyword": "application",
    "provider": "jira",
    "skip_validation": false,
    "personalization": true,
    "account_id": {
      "zip_name": "Base Connections/jira_sandbox.connection.json",
      "name": "Jira Sandbox",
      "folder": "Base Connections"
    }
  }
]
```

### Connection Requirements
- Each provider used in the recipe needs a corresponding config entry
- `account_id` references a connection file in the project
- `personalization` enables user-specific connections when true

## Validation and Testing

### CLI Validation
```bash
# Validate a recipe file
workato recipes validate --file path/to/recipe.json

# List validation errors
workato recipes validate --file path/to/recipe.json --verbose
```

### Common Validation Issues
1. **Missing required fields** in blocks
2. **Invalid provider names**
3. **Missing connection configurations**
4. **Invalid data pill references**
5. **Schema mismatches**

## Next Steps
- [Block Structure and Attributes](./block-structure.md)
- [Trigger Types and Requirements](./triggers.md)
- [Action Types and Requirements](./actions.md)
- [Data Mapping and References](./data-mapping.md)
