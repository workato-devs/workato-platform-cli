# Triggers

## Overview
Triggers are the starting point of every Workato recipe. They define what event initiates the recipe execution and provide the initial data that flows through subsequent actions.

## Trigger Fundamentals

### Key Characteristics
- **Always Block 0**: Triggers must be the root block (number 0)
- **Keyword**: Must use `"keyword": "trigger"`
- **Execution**: Fires automatically based on configured conditions
- **Data Source**: Provides initial data for the recipe

### Trigger Structure
```json
{
  "number": 0,
  "provider": "connector_name",
  "name": "trigger_name",
  "as": "unique_identifier",
  "keyword": "trigger",
  "input": { /* trigger configuration */ },
  "extended_output_schema": [ /* output data structure */ ]
}
```

## Trigger Types by Provider

### 1. Platform Connector Triggers

#### Webhook Triggers
**Provider**: `workato_api_platform`
**Name**: `receive_request`
**Purpose**: Receive HTTP requests from external systems

```json
{
  "number": 0,
  "provider": "workato_api_platform",
  "name": "receive_request",
  "as": "6c30db8b",
  "keyword": "trigger",
  "input": {
    "request": {
      "content_type": "json"
    },
    "response": {
      "content_type": "json",
      "responses": [
        {
          "http_status_code": "200"
        }
      ]
    }
  },
  "extended_output_schema": [
    {
      "label": "Context",
      "name": "context",
      "type": "object",
      "properties": [
        {
          "name": "calling_ip",
          "type": "string",
          "label": "Calling IP address"
        }
      ]
    }
  ]
}
```

#### Scheduled Triggers
**Provider**: `clock`
**Name**: `scheduled_event`
**Purpose**: Execute recipes on a schedule

```json
{
  "number": 0,
  "provider": "clock",
  "name": "scheduled_event",
  "as": "scheduled_trigger",
  "keyword": "trigger",
  "input": {
    "schedule": "0 9 * * 1-5"  // Cron expression: weekdays at 9 AM
  }
}
```

#### File Triggers
**Provider**: `google_drive`
**Name**: `new_file`
**Purpose**: Trigger when new files are added

```json
{
  "number": 0,
  "provider": "google_drive",
  "name": "new_file",
  "as": "file_trigger",
  "keyword": "trigger",
  "input": {
    "folder": "folder_id_here"
  }
}
```

#### Database Triggers
**Provider**: `mysql` (or other database connectors)
**Name**: `new_record`
**Purpose**: Trigger when new records are added

```json
{
  "number": 0,
  "provider": "mysql",
  "name": "new_record",
  "as": "db_trigger",
  "keyword": "trigger",
  "input": {
    "table": "users"
  }
}
```

### 2. Recipe Function Triggers

**Provider**: `workato_recipe_function`
**Name**: `execute`
**Purpose**: Make recipes callable as functions

```json
{
  "number": 0,
  "provider": "workato_recipe_function",
  "name": "execute",
  "as": "6b031f18",
  "keyword": "trigger",
  "input": {
    "parameters_schema_json": "[{\"name\":\"issue_key\",\"type\":\"string\",\"optional\":false,\"control_type\":\"text\",\"label\":\"Issue key\"}]",
    "result_schema_json": "[{\"name\":\"link\",\"type\":\"string\",\"optional\":false,\"control_type\":\"text\",\"label\":\"Link\"}]"
  },
  "extended_output_schema": [
    {
      "label": "Parameters",
      "name": "parameters",
      "type": "object",
      "properties": [
        {
          "name": "issue_key",
          "type": "string",
          "control_type": "text",
          "label": "Issue key",
          "optional": false
        }
      ]
    }
  ]
}
```

**Critical Requirements**:
- `extended_output_schema` must be the loaded JSON version of `parameters_schema_json`
- `result_schema_json` defines what the function returns
- This enables the recipe to be called by other recipes

### 3. Custom Connector Triggers

**Provider**: Custom connector name
**Name**: Varies by connector
**Purpose**: Trigger based on custom connector events

```json
{
  "number": 0,
  "provider": "custom_connector_name",
  "name": "trigger_name_from_connector",
  "as": "custom_trigger",
  "keyword": "trigger",
  "input": {
    "parameter1": "value1"
  }
}
```

**Finding Available Triggers**:
```bash
workato connectors code --id {connector_id}
```

## Trigger Configuration Patterns

### Webhook Configuration
```json
"input": {
  "request": {
    "content_type": "json",
    "headers": ["authorization", "content-type"]
  },
  "response": {
    "content_type": "json",
    "responses": [
      {
        "http_status_code": "200",
        "body": "Success response"
      },
      {
        "http_status_code": "400",
        "body": "Error response"
      }
    ]
  }
}
```

### Schedule Configuration
```json
"input": {
  "schedule": "0 9 * * 1-5",  // Cron format
  "timezone": "America/New_York"
}
```

### Filter Configuration
```json
"input": {
  "folder": "folder_id",
  "file_types": ["pdf", "doc", "docx"],
  "include_subfolders": true
}
```

## Trigger Output Data

### Data Structure
Triggers output data that subsequent actions can reference:

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
Actions reference trigger data using:
```json
"#{_dp('data.{provider}.{as}.{data_path}')}"
```

**Example**:
```json
"#{_dp('data.google_drive.file_trigger.file.name')}"
```

## Common Trigger Scenarios

### 1. API Endpoint Recipe
```json
{
  "number": 0,
  "provider": "workato_api_platform",
  "name": "receive_request",
  "as": "api_trigger",
  "keyword": "trigger",
  "input": {
    "request": {
      "content_type": "json"
    },
    "response": {
      "content_type": "json",
      "responses": [
        {
          "http_status_code": "200"
        }
      ]
    }
  }
}
```

### 2. Scheduled Recipe
```json
{
  "number": 0,
  "provider": "clock",
  "name": "scheduled_event",
  "as": "schedule_trigger",
  "keyword": "trigger",
  "input": {
    "schedule": "0 8 * * 1-5"
  }
}
```

### 3. File Monitoring Recipe
```json
{
  "number": 0,
  "provider": "google_drive",
  "name": "new_file",
  "as": "file_trigger",
  "keyword": "trigger",
  "input": {
    "folder": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
  }
}
```

## Trigger Validation

### Required Fields
- `number`: Must be 0
- `keyword`: Must be "trigger"
- `provider`: Must be valid connector
- `name`: Must be valid trigger for the provider
- `as`: Must be unique identifier
- `input`: Must contain required configuration

### Common Validation Errors
1. **Wrong block number**: Trigger must be block 0
2. **Invalid provider**: Provider doesn't exist or isn't available
3. **Invalid trigger name**: Name not supported by the provider
4. **Missing configuration**: Required input parameters missing
5. **Schema mismatch**: Extended output schema doesn't match actual output

### CLI Validation
```bash
# Validate trigger configuration
workato recipes validate --file recipe.json

# Check specific trigger requirements
workato connectors list --platform | grep provider_name
```

## Next Steps
- [Action Types and Requirements](./actions.md)
- [Data Mapping and References](./data-mapping.md)
- [Block Structure and Attributes](./block-structure.md)
