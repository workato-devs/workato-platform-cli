# Block Structure and Attributes

## Overview

Blocks are the fundamental building units of Workato recipes. Each block represents a single operation (trigger or action) and contains all the configuration, input/output schemas, and metadata needed for execution.

## Block Anatomy

### Basic Block Structure

```json
{
  "number": 0,
  "provider": "connector_name",
  "name": "action_or_trigger_name",
  "as": "unique_identifier",
  "keyword": "trigger|action",
  "input": { /* configuration */ },
  "extended_output_schema": [ /* output structure */ ],
  "extended_input_schema": [ /* input structure */ ],
  "comment": "Optional description",
  "block": [ /* child blocks */ ]
}
```

### Required Attributes

| Attribute | Required | Description | Example |
|-----------|----------|-------------|---------|
| `number` | ✅ | Sequential block number (0 for trigger, 1+ for actions) | `0`, `1`, `2` |
| `provider` | ✅ | Connector or provider name | `"google_drive"`, `"mysql"` |
| `name` | ✅ | Specific action/trigger name | `"download_file_contents"` |
| `as` | ✅ | Unique identifier for data references | `"download_action"` |
| `keyword` | ✅ | Must be "trigger" or "action" | `"trigger"` |

### Optional Attributes

| Attribute | Required | Description | Example |
|-----------|----------|-------------|---------|
| `input` | ❌ | Block configuration and parameters | `{"file_id": "123"}` |
| `extended_output_schema` | ❌ | Output data structure definition | `[{ "name": "file", "type": "object" }]` |
| `extended_input_schema` | ❌ | Input data structure definition | `[{ "name": "file_id", "type": "string" }]` |
| `comment` | ❌ | Human-readable description | `"Downloads file content"` |
| `block` | ❌ | Child execution blocks | `[{ "number": 1, ... }]` |

## Block Numbering System

### Sequential Execution Order

```json
{
  "code": {
    "number": 0,  // Trigger - executes first
    "provider": "google_drive",
    "name": "new_file",
    "keyword": "trigger",
    "block": [
      {
        "number": 1,  // Action 1 - executes second
        "provider": "utility",
        "name": "transform",
        "keyword": "action"
      },
      {
        "number": 2,  // Action 2 - executes third
        "provider": "mysql",
        "name": "insert_record",
        "keyword": "action"
      }
    ]
  }
}
```

### Numbering Rules

1. **Block 0**: Must be a trigger (root block)
2. **Blocks 1+**: Must be actions (child blocks)
3. **Sequential**: Numbers must be consecutive (0, 1, 2, 3...)
4. **Unique**: Each block number must be unique within the recipe
5. **Child Blocks**: Can have their own numbering system

## Extended Schemas

### Extended Output Schema

Defines the structure of data that a block produces for subsequent blocks to consume.

```json
"extended_output_schema": [
  {
    "label": "File Information",
    "name": "file",
    "type": "object",
    "properties": [
      {
        "name": "id",
        "type": "string",
        "label": "File ID"
      },
      {
        "name": "name",
        "type": "string",
        "label": "File Name"
      },
      {
        "name": "size",
        "type": "integer",
        "label": "File Size (bytes)"
      }
    ]
  }
]
```

### Extended Input Schema

Defines the structure of data that a block expects to receive.

```json
"extended_input_schema": [
  {
    "label": "File Parameters",
    "name": "file_params",
    "type": "object",
    "properties": [
      {
        "name": "file_id",
        "type": "string",
        "label": "File ID to process",
        "optional": false
      },
      {
        "name": "process_type",
        "type": "string",
        "label": "Processing type",
        "optional": true,
        "default": "standard"
      }
    ]
  }
]
```

### Schema Types

| Type | Description | Example |
|------|-------------|---------|
| `string` | Text data | `"Hello World"` |
| `integer` | Whole numbers | `42`, `-5` |
| `number` | Decimal numbers | `3.14`, `-2.5` |
| `boolean` | True/false values | `true`, `false` |
| `object` | Key-value pairs | `{"key": "value"}` |
| `array` | Ordered lists | `["item1", "item2"]` |
| `null` | Empty/undefined values | `null` |

### Schema Properties

| Property | Required | Description | Example |
|----------|----------|-------------|---------|
| `name` | ✅ | Field identifier | `"file_id"` |
| `type` | ✅ | Data type | `"string"` |
| `label` | ❌ | Human-readable name | `"File ID"` |
| `optional` | ❌ | Whether field is required | `false` |
| `default` | ❌ | Default value if not provided | `"standard"` |
| `control_type` | ❌ | UI control type | `"text"`, `"select"` |

## Block Configuration (Input)

### Input Structure

The `input` object contains all configuration parameters for the block:

```json
"input": {
  "file_id": "#{_dp('data.google_drive.file_trigger.file.id')}",
  "folder": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
  "file_types": ["pdf", "doc", "docx"],
  "include_subfolders": true,
  "max_results": 100
}
```

### Input Types

1. **Static Values**: Direct configuration
   ```json
   "folder": "folder_id_here",
   "max_results": 100
   ```

2. **Data Pills**: References to previous block data
   ```json
   "file_id": "#{_dp('data.google_drive.file_trigger.file.id')}"
   ```

3. **Formulas**: Data processing expressions
   ```json
   "file_name": "=_dp('data.google_drive.file_trigger.file.name').upcase"
   ```

4. **Conditional Values**: Dynamic configuration
   ```json
   "status": "#{_dp('data.mysql.check.success') == true ? 'active' : 'inactive'}"
   ```

## Child Blocks

### Nested Execution

Blocks can contain child blocks for complex workflows:

```json
{
  "number": 1,
  "provider": "utility",
  "name": "if",
  "keyword": "action",
  "input": {
    "condition": "#{_dp('data.google_drive.file_trigger.file.size') > 1000000"
  },
  "block": [
    {
      "number": 1,
      "provider": "utility",
      "name": "transform",
      "keyword": "action",
      "input": {
        "data": "#{_dp('data.google_drive.file_trigger.file')}",
        "transformation": "compress"
      }
    }
  ]
}
```

### Child Block Rules

1. **Numbering**: Child blocks can use their own numbering system
2. **Execution**: Execute only when parent block conditions are met
3. **Data Access**: Can reference data from parent and sibling blocks
4. **Scope**: Limited to parent block's execution context

## Block Validation Rules

### Trigger Block Requirements

1. **Block Number**: Must be 0
2. **Keyword**: Must be "trigger"
3. **Provider**: Must be valid connector
4. **Name**: Must be valid trigger for the provider
5. **Input**: Must contain required configuration

### Action Block Requirements

1. **Block Number**: Must be 1 or higher
2. **Keyword**: Must be "action"
3. **Provider**: Must be valid connector
4. **Name**: Must be valid action for the provider
5. **Input**: Must contain required configuration
6. **Data References**: All data pill references must be valid

### Schema Validation

1. **Output Schema**: Must match actual data produced
2. **Input Schema**: Must match data expected by the block
3. **Type Consistency**: Data types must match schema definitions
4. **Required Fields**: All required fields must be provided

## Common Block Patterns

### 1. Simple Action Block

```json
{
  "number": 1,
  "provider": "google_drive",
  "name": "download_file_contents",
  "as": "download_action",
  "keyword": "action",
  "input": {
    "file_id": "#{_dp('data.google_drive.file_trigger.file.id')}"
  },
  "comment": "Download file content for processing"
}
```

### 2. Block with Extended Schema

```json
{
  "number": 2,
  "provider": "utility",
  "name": "transform",
  "as": "transform_action",
  "keyword": "action",
  "input": {
    "data": "#{_dp('data.google_drive.download_action.content')}",
    "transformation": "uppercase"
  },
  "extended_output_schema": [
    {
      "label": "Transformed Data",
      "name": "result",
      "type": "string"
    }
  ]
}
```

### 3. Conditional Block

```json
{
  "number": 3,
  "provider": "utility",
  "name": "if",
  "as": "conditional_action",
  "keyword": "action",
  "input": {
    "condition": "#{_dp('data.utility.transform_action.result').length > 100"
  },
  "block": [
    {
      "number": 1,
      "provider": "slack",
      "name": "send_message",
      "keyword": "action",
      "input": {
        "channel": "#alerts",
        "message": "Large file processed: #{_dp('data.google_drive.file_trigger.file.name')}"
      }
    }
  ]
}
```

## Block Best Practices

### 1. Descriptive Identifiers

```json
// ✅ Good - clear and descriptive
"as": "download_file_action"

// ❌ Bad - unclear and hard to reference
"as": "abc123"
```

### 2. Consistent Naming

```json
// ✅ Good - consistent pattern
"as": "google_drive_download",
"as": "mysql_insert_record",
"as": "slack_notification"

// ❌ Bad - inconsistent patterns
"as": "download",
"as": "insert",
"as": "notify"
```

### 3. Clear Comments

```json
"comment": "Downloads file content for processing in next block",
"input": {
  "file_id": "#{_dp('data.google_drive.file_trigger.file.id')}"
}
```

### 4. Proper Schema Definitions

```json
"extended_output_schema": [
  {
    "label": "File Data",
    "name": "file",
    "type": "object",
    "properties": [
      {
        "name": "id",
        "type": "string",
        "label": "File ID"
      }
    ]
  }
]
```

## Block Troubleshooting

### Common Issues

1. **Invalid Block Number**: Ensure sequential numbering (0, 1, 2...)
2. **Missing Required Fields**: Check provider documentation for requirements
3. **Schema Mismatch**: Verify extended schemas match actual data
4. **Invalid Data References**: Ensure data pill paths are correct
5. **Provider Errors**: Check connector availability and configuration

### Validation Commands

```bash
# Validate entire recipe
workato recipes validate --file recipe.json

# Check specific block
workato recipes validate --file recipe.json --verbose

# List available connectors
workato connectors list --platform

# Check connector details
workato connectors code --id {connector_id}
```

## Next Steps

- [Triggers](./03-triggers.md) - Trigger types, requirements, and examples
- [Actions](./04-actions.md) - Action types, requirements, and patterns
- [Data Mapping](./05-data-mapping.md) - Data pill references and cross-block data flow
- [Formulas](./06-formulas.md) - Formula syntax, categories, and best practices
- [Naming Conventions](./07-naming-conventions.md) - Project and asset naming standards
