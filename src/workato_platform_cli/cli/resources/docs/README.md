# Workato Recipe Documentation

## Overview

This documentation is designed specifically for **AI agents** to understand how to build Workato recipes. It provides a comprehensive, structured approach to recipe development with clear examples and validation rules.

## Documentation Structure

### Core Concepts (Start Here)

1. **[Recipe Fundamentals](./recipe-fundamentals.md)** - Foundation concepts, structure, and workflow
2. **[Block Structure and Attributes](./block-structure.md)** - Block anatomy, schemas, and validation
3. **[Triggers](./triggers.md)** - Trigger types, requirements, and examples
4. **[Actions](./actions.md)** - Action types, requirements, and patterns
5. **[Data Mapping](./data-mapping.md)** - Data pill references and cross-block data flow
6. **[Formulas](./formulas.md)** - Formula syntax, categories, and best practices
7. **[Naming Conventions](./naming-conventions.md)** - Project and asset naming standards

### Formula Reference

Detailed formula documentation in the `formulas/` subdirectory:
- [String Formulas](./formulas/string-formulas.md) - Text manipulation and processing
- [Number Formulas](./formulas/number-formulas.md) - Mathematical operations
- [Date Formulas](./formulas/date-formulas.md) - Date and time operations
- [Array/List Formulas](./formulas/array-list-formulas.md) - Array and hash operations
- [Conditional Formulas](./formulas/conditions.md) - Logic and conditions
- [Other Formulas](./formulas/other-formulas.md) - Additional utilities

## AI Agent Recipe Building Flow

### 1. Start with Recipe Fundamentals
- Understand recipe structure and JSON format
- Learn about providers and connectors
- Understand data flow between blocks

### 2. Learn Block Structure
- Master block anatomy and attributes
- Understand extended schemas (input/output)
- Learn validation rules and requirements

### 3. Configure Triggers
- Choose appropriate trigger type
- Configure trigger parameters
- Define output data structure

### 4. Add Actions
- Select appropriate actions for your workflow
- Configure action parameters
- Reference data from previous blocks

### 5. Map Data Between Blocks
- Use data pills to reference previous block data
- Choose between text input mode and formula mode
- Handle arrays and complex data structures

### 6. Apply Formulas When Needed
- Use formulas for data transformation
- Apply string, number, date, and array operations
- Handle conditional logic

### 7. Follow Naming Conventions
- Use consistent naming patterns
- Apply project and asset codes
- Maintain clear documentation

## Key Concepts for AI Agents

### Recipe Structure
```json
{
  "name": "Recipe Name",
  "version": 3,
  "code": {
    "number": 0,
    "provider": "connector_name",
    "name": "trigger_name",
    "as": "unique_identifier",
    "keyword": "trigger",
    "block": [ /* child actions */ ]
  },
  "config": [ /* connections */ ]
}
```

### Block Requirements
- **Block 0**: Must be a trigger
- **Blocks 1+**: Must be actions
- **Sequential numbering**: 0, 1, 2, 3...
- **Unique identifiers**: Each block needs unique "as" value

### Data Flow
1. **Trigger fires** and provides initial data
2. **Actions execute sequentially** (1, 2, 3...)
3. **Data flows** from one block to the next
4. **Each block** can reference data from all previous blocks

### Data Pills
- **Simple syntax**: `#{_dp('data.provider.as.field')}`
- **Complex syntax**: `#{_dp('{"pill_type":"output",...}')}`
- **Formula mode**: `=_dp('data.provider.as.field').method()`

## Validation and Testing

### CLI Commands
```bash
# Validate recipe structure
workato recipes validate --file recipe.json

# Check for specific errors
workato recipes validate --file recipe.json --verbose

# List available connectors
workato connectors list --platform
```

### Common Validation Issues
1. **Missing required fields** in blocks
2. **Invalid provider names** or connector references
3. **Missing connection configurations**
4. **Invalid data pill references**
5. **Schema mismatches** between blocks

## Best Practices

### 1. Start Simple
- Begin with basic trigger → action → action flow
- Add complexity incrementally
- Test each block before adding the next

### 2. Use Descriptive Names
- Clear "as" values: `download_file_action`, `save_to_database`
- Consistent naming patterns across blocks
- Meaningful comments for complex logic

### 3. Validate Early and Often
- Validate after each block addition
- Check data pill references
- Verify schema compatibility

### 4. Handle Errors Gracefully
- Use conditional logic for fallback scenarios
- Implement proper error handling
- Test edge cases and failure modes

## Getting Help

### Documentation Commands
```bash
# List all available topics
workato guide topics

# Get specific topic content
workato guide content <topic-name>

# Search across all documentation
workato guide search <query>

# Show topic structure
workato guide structure <topic-name>
```

### Example Usage
```bash
# Learn about triggers
workato guide content triggers

# Search for data mapping examples
workato guide search "current_item"

# Understand block structure
workato guide content block-structure
```

## Next Steps

This documentation provides everything an AI agent needs to build functional Workato recipes. Start with the core concepts and work through each section systematically. Use the search functionality to find specific information, and validate your recipes frequently to catch issues early.

For advanced topics and specific use cases, refer to the individual formula guides and explore the examples provided in each section.
