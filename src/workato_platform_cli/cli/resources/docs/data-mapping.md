# Data Mapping and References

## Overview
Data mapping is the core mechanism that enables data to flow between blocks in a Workato recipe. Understanding how to reference and map data is essential for building functional recipes.

## Data Pill Fundamentals

### Data Pill Syntax
Workato supports two main syntaxes for referencing data from previous blocks:

#### 1. Simple Data Path Syntax (Recommended)
```json
"#{_dp('data.{provider}.{as}.{data_path}')}"
```

#### 2. Complex JSON Path Syntax (Advanced)
```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"{provider}\",\"line\":\"{as}\",\"path\":[\"field1\",\"field2\"]}')}"
```

### Components Breakdown

#### Simple Syntax
- **`#{_dp('...')}`**: Data pill wrapper function
- **`data`**: Fixed prefix indicating data reference
- **`{provider}`**: Provider name of the source block
- **`{as}`**: The "as" value from the source block
- **`{data_path}`**: Path to specific data field using dot notation

#### Complex JSON Syntax
- **`pill_type`**: Usually "output" for data references
- **`provider`**: Provider name of the source block
- **`line`**: The "as" value from the source block
- **`path`**: Array of path elements to the target field
- **`path_element_type`**: Special values like "current_item" for array operations

### Example Data Pills

#### Simple Syntax Example
```json
"#{_dp('data.google_drive.9672c97b.file.name')}"
```

**Breakdown**:
- `google_drive`: Provider name
- `9672c97b`: The "as" value from the source block
- `file.name`: Path to the "name" field within the "file" object

#### Complex JSON Syntax Example
```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"b2dacec4\",\"path\":[\"result\",\"files\",{\"path_element_type\":\"current_item\"},\"id\"]}')}"
```

**Breakdown**:
- `pill_type`: "output" (data reference)
- `provider`: "workato_recipe_function"
- `line`: "b2dacec4" (the "as" value)
- `path`: ["result", "files", {"path_element_type": "current_item"}, "id"]

### When to Use Each Syntax

#### Use Simple Syntax When:
- Referencing simple fields (strings, numbers, booleans)
- Accessing nested object properties
- Referencing specific array elements by index
- Building straightforward data mappings

#### Use Complex JSON Syntax When:
- Working with array transformations using `current_item`
- Need precise control over path elements
- Building complex array-to-array mappings
- Working with recipe functions that require specific path structures

## Data Flow Between Blocks

### Execution Order and Data Availability
1. **Block 0 (Trigger)**: Provides initial data
2. **Block 1**: Can reference data from Block 0
3. **Block 2**: Can reference data from Block 0 and Block 1
4. **Block N**: Can reference data from all previous blocks

### Data Reference Timeline
```
Block 0 (Trigger) → Block 1 → Block 2 → Block 3
     ↓                ↓         ↓         ↓
   Data A          Data B     Data C     Data D
     ↓                ↓         ↓         ↓
   Available      Available  Available  Available
   to: 1,2,3     to: 2,3    to: 3      to: none
```

## Data Pill Reference Patterns

### 1. Direct Field References
Reference a simple field from a previous block:

```json
"#{_dp('data.workato_recipe_function.6b031f18.parameters.issue_key')}"
```

**Source Block**:
```json
{
  "provider": "workato_recipe_function",
  "as": "6b031f18",
  "extended_output_schema": [
    {
      "name": "parameters",
      "properties": [
        {
          "name": "issue_key",
          "type": "string"
        }
      ]
    }
  ]
}
```

## Input Modes and Data Pill Usage

Workato supports two distinct input modes that affect how data pills are used:

### 1. Text Input Mode (Direct Data Pills)
Data pills are embedded directly in text strings using the `#{_dp('...')}` syntax:

```json
"name": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"b2dacec4\",\"path\":[\"result\",\"files\",{\"path_element_type\":\"current_item\"},\"name\"]}')} - raw text - #{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"b2dacec4\",\"path\":[\"result\",\"files\",{\"path_element_type\":\"current_item\"},\"id\"]}')}"
```

**Characteristics**:
- Uses `#{_dp('...')}` syntax
- Data pills can be mixed with literal text
- Multiple data pills can be concatenated in a single string
- No formula processing - data pills are treated as text substitutions

### 2. Formula Mode (Data Pills in Formulas)
Data pills are used within formulas using the `=_dp('...')` syntax:

```json
"id": "=_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"b2dacec4\",\"path\":[\"result\",\"files\",{\"path_element_type\":\"current_item\"},\"id\"]}').split(\":\").first"
```

**Characteristics**:
- Uses `=_dp('...')` syntax (note the `=` prefix)
- Data pills can be processed with string methods and functions
- Supports complex operations like `.split()`, `.first`, `.last`, etc.
- Formula processing enables data transformation and manipulation

### 3. Mixed Mode Examples
Here are real examples from the recipe showing both modes:

```json
"files": {
  "____source": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"b2dacec4\",\"path\":[\"result\",\"files\"]}')}",

  // Formula mode - data processing
  "id": "=_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"b2dacec4\",\"path\":[\"result\",\"files\",{\"path_element_type\":\"current_item\"},\"id\"]}').split(\":\").first",

  // Text input mode - direct concatenation
  "name": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"b2dacec4\",\"path\":[\"result\",\"files\",{\"path_element_type\":\"current_item\"},\"name\"]}')} - raw text - #{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"b2dacec4\",\"path\":[\"result\",\"files\",{\"path_element_type\":\"current_item\"},\"id\"]}')}",

  // Formula mode with text and data pill
  "type": "=\"text in a formula with a data pill: #{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"b2dacec4\",\"path\":[\"result\",\"files\",{\"path_element_type\":\"current_item\"},\"type\"]}')}\"",

  // Text input mode - simple data pill
  "content": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"b2dacec4\",\"path\":[\"result\",\"files\",{\"path_element_type\":\"current_item\"},\"content\"]}')}"
}
```

### 4. When to Use Each Mode

#### Use Text Input Mode When:
- You need to concatenate data pills with literal text
- Simple data substitution is required
- No data processing or transformation is needed
- Building display strings or messages

#### Use Formula Mode When:
- You need to process or transform the data
- String operations like split, substring, or replace are required
- Mathematical operations are needed
- Complex data manipulation is required

### 5. Common Formula Operations

For comprehensive formula documentation, refer to the official Workato formula guides:

- **[String Formulas](../formulas/string-formulas.md)** - String manipulation, text processing, and validation
- **[Number Formulas](../formulas/number-formulas.md)** - Mathematical operations, calculations, and numeric processing
- **[Date Formulas](../formulas/date-formulas.md)** - Date/time operations, formatting, and calculations
- **[Array/List Formulas](../formulas/array-list-formulas.md)** - Array operations, list processing, and hash manipulation
- **[Conditional Formulas](../formulas/conditions.md)** - If-else logic, boolean operations, and conditional processing
- **[Other Formulas](../formulas/other-formulas.md)** - Additional utility functions and operations

**Key Formula Syntax**:
```json
// Formula mode uses =_dp('...') syntax
"id": "=_dp('data.source_block.field').split(':').first"
"name": "=_dp('data.source_block.field').upcase"
"count": "=_dp('data.source_block.items').length"
```

### 2. Nested Object References
Reference fields within nested objects:

```json
"#{_dp('data.jira.748bbf54.attachments.0.self')}"
```

**Source Block Output**:
```json
{
  "attachments": [
    {
      "self": "https://example.com/attachment/123",
      "thumbnail": "https://example.com/thumb/123"
    }
  ]
}
```

### 3. Array Element References
Reference specific elements in arrays:

```json
"#{_dp('data.google_drive.search_files.files.0.id')}"
"#{_dp('data.google_drive.search_files.files.1.name')}"
```

**Array Structure**:
```json
{
  "files": [
    {"id": "file1", "name": "Document1.pdf"},
    {"id": "file2", "name": "Document2.pdf"}
  ]
}
```

### 4. Complex Array Mapping with Current Item Pattern
For complex array operations, Workato uses a special `current_item` pattern that allows mapping array elements to new structures:

```json
"files": {
  "____source": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"b2dacec4\",\"path\":[\"result\",\"files\"]}')}",
  "id": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"b2dacec4\",\"path\":[\"result\",\"files\",{\"path_element_type\":\"current_item\"},\"id\"]}')}",
  "name": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"b2dacec4\",\"path\":[\"result\",\"files\",{\"path_element_type\":\"current_item\"},\"name\"]}')}",
  "type": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"b2dacec4\",\"path\":[\"result\",\"files\",{\"path_element_type\":\"current_item\"},\"type\"]}')}"
}
```

**Key Components**:
- **`____source`**: References the entire array from the source block
- **`current_item`**: Special path element that maps each array item individually
- **Field mapping**: Each field maps to the corresponding property of the current array item

**Source Block Structure** (Block b2dacec4):
```json
{
  "provider": "workato_recipe_function",
  "name": "call_recipe",
  "as": "b2dacec4",
  "extended_output_schema": [
    {
      "name": "result",
      "properties": [
        {
          "name": "files",
          "type": "array",
          "of": "object",
          "properties": [
            {"name": "id", "type": "string"},
            {"name": "name", "type": "string"},
            {"name": "type", "type": "string"}
          ]
        }
      ]
    }
  ]
}
```

**Result**: This creates a new array where each item has the mapped structure, transforming the source data format.

### Real-World Example: File Processing Pipeline

**Source Block** (Block 4 - Call Recipe):
```json
{
  "provider": "workato_recipe_function",
  "name": "call_recipe",
  "as": "b2dacec4",
  "keyword": "action",
  "input": {
    "flow_id": {
      "zip_name": "Functions/search_google_drive_user_scoped.recipe.json",
      "name": "Search Google Drive (User Scoped)",
      "folder": "Functions"
    },
    "parameters": {
      "query": "#{_dp('data.workato_api_platform.93424d18.request.query')}"
    }
  }
}
```

**Target Block** (Block 5 - Return Response):
```json
{
  "provider": "workato_api_platform",
  "name": "return_response",
  "as": "b621c65f",
  "keyword": "action",
  "input": {
    "http_status_code": "200",
    "response": {
      "message": "success. Make sure you search Jira tickets next.",
      "files": {
        "____source": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"b2dacec4\",\"path\":[\"result\",\"files\"]}')}",
        "id": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"b2dacec4\",\"path\":[\"result\",\"files\",{\"path_element_type\":\"current_item\"},\"id\"]}')}",
        "name": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"b2dacec4\",\"path\":[\"result\",\"files\",{\"path_element_type\":\"current_item\"},\"name\"]}')}",
        "type": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"b2dacec4\",\"path\":[\"result\",\"files\",{\"path_element_type\":\"current_item\"},\"type\"]}')}",
        "content": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"b2dacec4\",\"path\":[\"result\",\"files\",{\"path_element_type\":\"current_item\"},\"content\"]}')}",
        "thumbnail_link": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"b2dacec4\",\"path\":[\"result\",\"files\",{\"path_element_type\":\"current_item\"},\"thumbnail_link\"]}')}",
        "web_link": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"b2dacec4\",\"path\":[\"result\",\"files\",{\"path_element_type\":\"current_item\"},\"webview_link\"]}')}"
      }
    }
  }
}
```

**What Happens**:
1. Block 4 calls another recipe and returns an array of files
2. Block 5 maps each file in the array to a new structure
3. The `____source` field preserves the array structure
4. Each field maps to the corresponding property of each array item
5. The result is a transformed array with the new structure

### 4. Conditional References
Reference data conditionally:

```json
"#{_dp('data.mysql.insert_record.success') == true ? 'Success' : 'Failed'}"
```

## Common Data Mapping Scenarios

### 1. Recipe Function Parameter Mapping
**Trigger Block** (Block 0):
```json
{
  "provider": "workato_recipe_function",
  "name": "execute",
  "as": "6b031f18",
  "keyword": "trigger",
  "input": {
    "parameters_schema_json": "[{\"name\":\"issue_key\",\"type\":\"string\"}]"
  },
  "extended_output_schema": [
    {
      "name": "parameters",
      "properties": [
        {
          "name": "issue_key",
          "type": "string"
        }
      ]
    }
  ]
}
```

**Action Block** (Block 1):
```json
{
  "provider": "jira",
  "name": "upload_attachment",
  "as": "62c5b5f6",
  "keyword": "action",
  "input": {
    "id": "#{_dp('data.workato_recipe_function.6b031f18.parameters.issue_key')}"
  }
}
```

### 2. File Processing Pipeline
**Block 1** (Download File):
```json
{
  "provider": "google_drive",
  "name": "download_file_contents",
  "as": "9672c97b",
  "keyword": "action"
}
```

**Block 2** (Process File):
```json
{
  "provider": "utility",
  "name": "transform",
  "as": "transform_data",
  "keyword": "action",
  "input": {
    "data": "#{_dp('data.google_drive.9672c97b.content')}",
    "file_name": "#{_dp('data.google_drive.9672c97b.name')}"
  }
}
```

**Block 3** (Save Results):
```json
{
  "provider": "mysql",
  "name": "insert_record",
  "as": "save_data",
  "keyword": "action",
  "input": {
    "table": "processed_files",
    "data": {
      "file_name": "#{_dp('data.google_drive.9672c97b.name')}",
      "processed_content": "#{_dp('data.utility.transform_data.result')}",
      "file_size": "#{_dp('data.google_drive.9672c97b.size')}"
    }
  }
}
```

### 3. API Response Chain
**Block 1** (HTTP Request):
```json
{
  "provider": "rest",
  "name": "get",
  "as": "fetch_data",
  "keyword": "action",
  "input": {
    "url": "https://api.example.com/data"
  }
}
```

**Block 2** (Process Response):
```json
{
  "provider": "utility",
  "name": "filter",
  "as": "filter_data",
  "keyword": "action",
  "input": {
    "data": "#{_dp('data.rest.fetch_data.body')}",
    "condition": "#{_dp('data.rest.fetch_data.status')} == 200"
  }
}
```

**Block 3** (Return Response):
```json
{
  "provider": "workato_api_platform",
  "name": "return_response",
  "as": "return_result",
  "keyword": "action",
  "input": {
    "http_status_code": "200",
    "body": {
      "filtered_data": "#{_dp('data.utility.filter_data.result')}",
      "original_status": "#{_dp('data.rest.fetch_data.status')}"
    }
  }
}
```

## Data Type Handling

### String Data
```json
"#{_dp('data.source_block.field_name')}"
```

### Numeric Data
```json
"#{_dp('data.source_block.count') + 1}"
"#{_dp('data.source_block.price') * 1.1}"
```

### Boolean Data
```json
"#{_dp('data.source_block.success') == true}"
"#{_dp('data.source_block.enabled') != false}"
```

### Array Data
```json
"#{_dp('data.source_block.items')}"
"#{_dp('data.source_block.files.0.name')}"
```

### Object Data
```json
"#{_dp('data.source_block.user.name')}"
"#{_dp('data.source_block.response.data.id')}"
```

## Array Data Mapping Patterns

### 1. Simple Array References
Reference entire arrays or specific elements:

```json
// Reference entire array
"files": "#{_dp('data.google_drive.search_files.files')}"

// Reference specific array element
"first_file": "#{_dp('data.google_drive.search_files.files.0')}"

// Reference specific field of array element
"first_file_name": "#{_dp('data.google_drive.search_files.files.0.name')}"
```

### 2. Array Transformation with Current Item Pattern
Transform array data using the `current_item` pattern:

```json
"transformed_files": {
  "____source": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"b2dacec4\",\"path\":[\"result\",\"files\"]}')}",
  "id": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"b2dacec4\",\"path\":[\"result\",\"files\",{\"path_element_type\":\"current_item\"},\"id\"]}')}",
  "name": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"b2dacec4\",\"path\":[\"result\",\"files\",{\"path_element_type\":\"current_item\"},\"name\"]}')}",
  "type": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"b2dacec4\",\"path\":[\"result\",\"files\",{\"path_element_type\":\"current_item\"},\"type\"]}')}"
}
```

**What This Does**:
- Takes an array of files from the source block
- Maps each file to a new structure with selected fields
- Preserves the array structure while transforming individual items

### 3. Array Filtering and Mapping
Filter arrays based on conditions:

```json
"filtered_files": "#{_dp('data.google_drive.search_files.files').filter(file => file.type == 'pdf')}"
```

**Note**: Array filtering syntax may vary by provider and context.

### 4. Array Aggregation
Combine array data into single values:

```json
"total_files": "#{_dp('data.google_drive.search_files.files').length}"
"file_names": "#{_dp('data.google_drive.search_files.files').map(file => file.name).join(', ')}"
```

### 5. Nested Array Handling
Handle arrays within arrays:

```json
// Source structure: { "folders": [{ "files": [{ "name": "doc.pdf" }] }] }
"file_names": "#{_dp('data.google_drive.folders.0.files.0.name')}"

// Using current_item for nested arrays
"all_files": {
  "____source": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"google_drive\",\"line\":\"folder_block\",\"path\":[\"folders\"]}')}",
  "folder_name": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"google_drive\",\"line\":\"folder_block\",\"path\":[\"folders\",{\"path_element_type\":\"current_item\"},\"name\"]}')}",
  "files": {
    "____source": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"google_drive\",\"line\":\"folder_block\",\"path\":[\"folders\",{\"path_element_type\":\"current_item\"},\"files\"]}')}",
    "file_name": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"google_drive\",\"line\":\"folder_block\",\"path\":[\"folders\",{\"path_element_type\":\"current_item\"},\"files\",{\"path_element_type\":\"current_item\"},\"name\"]}')}"
  }
}
```

## Advanced Data Mapping

### 1. Multiple Source References
Reference data from multiple previous blocks:

```json
"input": {
  "issue_key": "#{_dp('data.workato_recipe_function.6b031f18.parameters.issue_key')}",
  "file_content": "#{_dp('data.google_drive.9672c97b.content')}",
  "file_name": "#{_dp('data.google_drive.9672c97b.name')}",
  "user_id": "#{_dp('data.mysql.get_user.id')}"
}
```

### 2. Conditional Data Mapping
Use conditional logic for data mapping:

```json
"input": {
  "status": "#{_dp('data.mysql.check_status.success') == true ? 'active' : 'inactive'}",
  "message": "#{_dp('data.mysql.check_status.success') == true ? 'Success' : 'Failed: ' + _dp('data.mysql.check_status.error')}"
}
```

### 3. Data Transformation in Mapping
Transform data during mapping:

```json
"input": {
  "file_name_upper": "#{_dp('data.google_drive.9672c97b.name').toUpperCase()}",
  "file_size_mb": "#{_dp('data.google_drive.9672c97b.size') / 1024 / 1024}"
}
```

## Data Validation and Error Handling

### Common Data Reference Errors

#### 1. Invalid Provider Name
```json
// ❌ Wrong provider name
"#{_dp('data.google_drive_wrong.9672c97b.file.name')}"
```

#### 2. Invalid "as" Value
```json
// ❌ Wrong "as" value
"#{_dp('data.google_drive.wrong_as_value.file.name')}"
```

#### 3. Invalid Data Path
```json
// ❌ Field doesn't exist in source
"#{_dp('data.google_drive.9672c97b.nonexistent_field')}"
```

#### 4. Array Index Out of Bounds
```json
// ❌ Array index doesn't exist
"#{_dp('data.google_drive.9672c97b.files.999.name')}"
```

### Data Reference Validation
```bash
# Validate recipe data references
workato recipes validate --file recipe.json

# Check for data reference errors
workato recipes validate --file recipe.json --verbose
```

## Best Practices

### 1. Use Descriptive "as" Values
```json
// ✅ Good - descriptive and clear
"as": "download_file_action"

// ❌ Bad - unclear and hard to reference
"as": "abc123"
```

### 2. Choose the Right Input Mode
```json
// ✅ Text Input Mode - for simple concatenation
"display_name": "#{_dp('data.source_block.first_name')} #{_dp('data.source_block.last_name')}"

// ✅ Formula Mode - for data processing
"clean_id": "=_dp('data.source_block.id').split(':').first"

// ❌ Mixed Mode - can be confusing
"mixed": "=_dp('data.source_block.field') + ' - ' + _dp('data.source_block.other')"
```

### 3. Formula Mode Best Practices
```json
// ✅ Good - clear and readable
"id": "=_dp('data.source_block.complex_id').split(':').first"

// ✅ Good - with descriptive variable names
"file_extension": "=_dp('data.source_block.file_name').split('.').last"

// ❌ Bad - overly complex inline operations
"result": "=_dp('data.source_block.field').split(':').filter(item => item.length > 0).map(item => item.trim()).join('|')"
```

### 4. Text Input Mode Best Practices
```json
// ✅ Good - clear concatenation
"full_path": "#{_dp('data.source_block.base_url')}/#{_dp('data.source_block.endpoint')}"

// ✅ Good - readable with spacing
"message": "Processing file: #{_dp('data.source_block.file_name')} (Size: #{_dp('data.source_block.file_size')} bytes)"

// ❌ Bad - hard to read without spacing
"message": "#{_dp('data.source_block.status')}#{_dp('data.source_block.code')}#{_dp('data.source_block.message')}"
```

### 2. Consistent Naming Conventions
```json
// ✅ Good - consistent pattern
"as": "jira_upload_attachment"
"as": "google_drive_download_file"
"as": "mysql_insert_record"

// ❌ Bad - inconsistent patterns
"as": "jira_upload"
"as": "download_file"
"as": "mysql_insert"
```

### 3. Document Data Dependencies
```json
"comment": "Downloads file content for processing in next block",
"input": {
  "file_id": "#{_dp('data.workato_recipe_function.6b031f18.parameters.file_id')}"
}
```

### 4. Validate Data References Early
Test data references as you build the recipe:
```bash
# Validate after each block addition
workato recipes validate --file recipe.json
```

## Troubleshooting Data Mapping

### Debug Data References
1. **Check provider names** - Ensure they match exactly
2. **Verify "as" values** - Must match source block exactly
3. **Validate data paths** - Use extended output schemas as reference
4. **Test incrementally** - Add blocks one at a time and validate

### Common Issues and Solutions

#### Issue: "Data reference not found"
**Solution**: Check the exact provider name and "as" value from the source block

#### Issue: "Field not available in schema"
**Solution**: Verify the field exists in the source block's `extended_output_schema`

#### Issue: "Array index out of bounds"
**Solution**: Ensure the array index exists or use conditional logic

#### Issue: "Type mismatch"
**Solution**: Check data types match between source and target fields

#### Issue: "Array mapping not working with current_item"
**Solution**:
- Ensure the source block has `extended_output_schema` with array definition
- Verify the `____source` field references the correct array path
- Check that all field mappings use the same `current_item` pattern

#### Issue: "Complex JSON syntax errors"
**Solution**:
- Escape quotes properly: `\"` instead of `"`
- Ensure the JSON path array is valid
- Verify `path_element_type` values are correct
- Use the simple syntax when possible for easier debugging

#### Issue: "Formula mode not working"
**Solution**:
- Ensure the formula starts with `=` (equals sign)
- Check that the data pill syntax is correct within the formula
- Verify the formula syntax is valid (proper method calls, operators)
- Test with simple formulas first before adding complexity

#### Issue: "Text concatenation not working as expected"
**Solution**:
- Use `#{_dp('...')}` syntax for text input mode
- Ensure proper spacing between data pills and literal text
- Check that all data pill references are valid
- Avoid mixing formula syntax (`=_dp`) in text input mode

#### Issue: "Mixed input modes causing errors"
**Solution**:
- Choose one input mode per field when possible
- Use formula mode for data processing, text mode for display
- Keep complex operations in formula mode
- Test each input mode separately before combining

## Next Steps
- [Formulas](./formulas.md) - Formula syntax, categories, and best practices
- [Naming Conventions](./naming-conventions.md) - Project and asset naming standards
- [Block Structure and Attributes](./block-structure.md)
