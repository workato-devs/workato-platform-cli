# Actions

## Overview
Actions are the execution blocks that perform specific operations in a Workato recipe. They execute sequentially after the trigger and can reference data from previous blocks to perform their operations.

## Action Fundamentals

### Key Characteristics
- **Block Numbers**: Must be 1 or higher (never 0)
- **Keyword**: Must use `"keyword": "action"`
- **Execution**: Execute sequentially in order
- **Data Input**: Can reference data from previous blocks
- **Data Output**: Provide data for subsequent blocks

### Action Structure
```json
{
  "number": 1,
  "provider": "connector_name",
  "name": "action_name",
  "as": "unique_identifier",
  "keyword": "action",
  "input": { /* action configuration */ },
  "extended_output_schema": [ /* output data structure */ ]
}
```

## Action Types by Provider

### 1. Platform Connector Actions

#### File Operations
**Provider**: `google_drive`
**Common Actions**: `download_file_contents`, `upload_file`, `search_files`

```json
{
  "number": 1,
  "provider": "google_drive",
  "name": "download_file_contents",
  "as": "9672c97b",
  "keyword": "action",
  "input": {
    "file_id": "#{_dp('data.workato_api_platform.api_trigger.file_id')}"
  },
  "comment": "Download the file by ID"
}
```

#### Database Operations
**Provider**: `mysql`, `postgresql`, `sql_server`
**Common Actions**: `insert_record`, `update_record`, `search_records`

```json
{
  "number": 2,
  "provider": "mysql",
  "name": "insert_record",
  "as": "db_insert",
  "keyword": "action",
  "input": {
    "table": "users",
    "data": {
      "name": "#{_dp('data.google_drive.9672c97b.name')}",
      "email": "#{_dp('data.google_drive.9672c97b.email')}"
    }
  }
}
```

#### HTTP Operations
**Provider**: `rest`
**Common Actions**: `post`, `get`, `put`, `delete`

```json
{
  "number": 3,
  "provider": "rest",
  "name": "post",
  "as": "http_post",
  "keyword": "action",
  "input": {
    "url": "https://api.example.com/webhook",
    "data": {
      "file_processed": "#{_dp('data.google_drive.9672c97b.name')}",
      "status": "completed"
    }
  }
}
```

#### Notification Actions
**Provider**: `slack`, `email`, `microsoft_teams`
**Common Actions**: `send_message`, `send_email`

```json
{
  "number": 4,
  "provider": "slack",
  "name": "send_message",
  "as": "slack_notify",
  "keyword": "action",
  "input": {
    "channel": "#general",
    "message": "File processing completed: #{_dp('data.google_drive.9672c97b.name')}"
  }
}
```

### 2. Workato Built-in Actions

#### Recipe Function Actions
**Provider**: `workato_recipe_function`

##### `return_result` Action
```json
{
  "number": 5,
  "provider": "workato_recipe_function",
  "name": "return_result",
  "as": "0bfec399",
  "keyword": "action",
  "input": {
    "result": {
      "link": "#{_dp('data.jira.748bbf54.attachments.0.self')}",
      "thumbnail": "#{_dp('data.jira.748bbf54.attachments.0.thumbnail')}"
    }
  },
  "extended_output_schema": [
    {
      "label": "Result",
      "name": "result",
      "type": "object",
      "properties": [
        {
          "name": "link",
          "type": "string",
          "control_type": "text",
          "label": "Link"
        },
        {
          "name": "thumbnail",
          "type": "string",
          "control_type": "text",
          "label": "Thumbnail"
        }
      ]
    }
  ],
  "extended_input_schema": [
    /* Same as extended_output_schema */
  ]
}
```

**Critical Requirements**:
- Both schemas must match the trigger's `result_schema_json`
- This defines what the recipe function returns

##### `call_recipe` Action
```json
{
  "number": 6,
  "provider": "workato_recipe_function",
  "name": "call_recipe",
  "as": "call_other_recipe",
  "keyword": "action",
  "input": {
    "recipe_id": "12345",
    "parameters": {
      "file_id": "#{_dp('data.google_drive.9672c97b.id')}",
      "issue_key": "PROJ-123"
    }
  },
  "extended_input_schema": [
    /* Loaded JSON of called recipe's parameters_schema_json */
  ],
  "extended_output_schema": [
    /* Loaded JSON of called recipe's result_schema_json */
  ]
}
```

**Critical Requirements**:
- `extended_input_schema` = called recipe's `parameters_schema_json` (loaded)
- `extended_output_schema` = called recipe's `result_schema_json` (loaded)

#### API Platform Actions
**Provider**: `workato_api_platform`
**Common Actions**: `return_response`, `return_error`

```json
{
  "number": 7,
  "provider": "workato_api_platform",
  "name": "return_response",
  "as": "1966ff4d",
  "keyword": "action",
  "input": {
    "http_status_code": "200",
    "body": {
      "status": "success",
      "message": "File processed successfully"
    }
  }
}
```

#### Utility Actions
**Provider**: `utility`
**Common Actions**: `transform`, `filter`, `map`, `reduce`

```json
{
  "number": 8,
  "provider": "utility",
  "name": "transform",
  "as": "data_transform",
  "keyword": "action",
  "input": {
    "data": "#{_dp('data.mysql.db_insert.id')}",
    "transformation": "uppercase"
  }
}
```

### 3. Custom Connector Actions

**Provider**: Custom connector name
**Name**: Varies by connector
**Purpose**: Perform custom operations

```json
{
  "number": 9,
  "provider": "custom_connector_name",
  "name": "custom_action_name",
  "as": "custom_action",
  "keyword": "action",
  "input": {
    "parameter1": "#{_dp('data.utility.data_transform.result')}",
    "parameter2": "static_value"
  }
}
```

**Finding Available Actions**:
```bash
workato connectors code --id {connector_id}
```

## Action Configuration Patterns

### Data Mapping
Actions commonly map data from previous blocks:

```json
"input": {
  "issue_id": "#{_dp('data.workato_recipe_function.6b031f18.parameters.issue_key')}",
  "file_content": "#{_dp('data.google_drive.9672c97b.content')}",
  "file_name": "#{_dp('data.google_drive.9672c97b.name')}"
}
```

### Conditional Logic
Some actions support conditional execution:

```json
"input": {
  "condition": "#{_dp('data.mysql.db_insert.success')} == true",
  "action": "send_success_notification"
}
```

### Batch Processing
Actions can process multiple items:

```json
"input": {
  "items": "#{_dp('data.google_drive.search_files.files')}",
  "batch_size": 10,
  "process_each": true
}
```

## Action Output Data

### Data Structure
Actions output data that subsequent actions can reference:

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
      },
      {
        "name": "name",
        "type": "string",
        "label": "File Name"
      },
      {
        "name": "size",
        "type": "integer",
        "label": "File Size"
      }
    ]
  }
]
```

### Data Pill References
Subsequent actions reference action data using:
```json
"#{_dp('data.{provider}.{as}.{data_path}')}"
```

**Example**:
```json
"#{_dp('data.google_drive.9672c97b.file.name')}"
```

## Common Action Sequences

### 1. File Processing Pipeline
```json
[
  {
    "number": 1,
    "provider": "google_drive",
    "name": "download_file_contents",
    "as": "download_file",
    "keyword": "action"
  },
  {
    "number": 2,
    "provider": "utility",
    "name": "transform",
    "as": "transform_data",
    "keyword": "action"
  },
  {
    "number": 3,
    "provider": "mysql",
    "name": "insert_record",
    "as": "save_data",
    "keyword": "action"
  }
]
```

### 2. API Response Chain
```json
[
  {
    "number": 1,
    "provider": "rest",
    "name": "get",
    "as": "fetch_data",
    "keyword": "action"
  },
  {
    "number": 2,
    "provider": "utility",
    "name": "filter",
    "as": "filter_data",
    "keyword": "action"
  },
  {
    "number": 3,
    "provider": "workato_api_platform",
    "name": "return_response",
    "as": "return_result",
    "keyword": "action"
  }
]
```

### 3. Recipe Function Chain
```json
[
  {
    "number": 1,
    "provider": "workato_recipe_function",
    "name": "call_recipe",
    "as": "call_helper",
    "keyword": "action"
  },
  {
    "number": 2,
    "provider": "workato_recipe_function",
    "name": "return_result",
    "as": "return_data",
    "keyword": "action"
  }
]
```

## Action Validation

### Required Fields
- `number`: Must be 1 or higher
- `keyword`: Must be "action"
- `provider`: Must be valid connector
- `name`: Must be valid action for the provider
- `as`: Must be unique identifier
- `input`: Must contain required configuration

### Common Validation Errors
1. **Wrong block number**: Actions must be blocks 1+
2. **Invalid provider**: Provider doesn't exist or isn't available
3. **Invalid action name**: Name not supported by the provider
4. **Missing configuration**: Required input parameters missing
5. **Invalid data references**: Data pill references don't exist
6. **Schema mismatch**: Extended schemas don't match actual data

### CLI Validation
```bash
# Validate action configuration
workato recipes validate --file recipe.json

# Check specific action requirements
workato connectors list --platform | grep provider_name
```

## Performance Considerations

### Execution Order
- Actions execute sequentially
- Each action waits for the previous to complete
- Consider parallel execution for independent operations

### Data Volume
- Large data sets can impact performance
- Use filtering and pagination when possible
- Consider batch processing for multiple items

### Error Handling
- Actions can fail independently
- Implement proper error handling
- Use conditional logic for fallback scenarios

## Next Steps
- [Data Mapping and References](./data-mapping.md)
- [Block Structure and Attributes](./block-structure.md)
- [Formulas](./formulas.md)
