# Formulas

## Overview
Workato supports powerful formula capabilities that allow you to transform, manipulate, and process data within your recipes. Formulas use Ruby syntax and are executed in formula mode using the `=_dp('...')` syntax.

## Formula Fundamentals

### Formula Mode Syntax
Formulas in Workato use a special syntax that starts with `=` (equals sign):

```json
"field_name": "=_dp('data.provider.as.field').method()"
```

### Key Components
- **`=`**: Indicates formula mode (not text input mode)
- **`_dp('...')`**: Data pill reference within the formula
- **`.method()`**: Ruby method calls on the data pill value
- **Operators**: Standard Ruby operators like `+`, `-`, `*`, `/`, `==`, `&&`, `||`

### Formula vs. Text Input Mode
```json
// Formula Mode - for data processing
"id": "=_dp('data.source_block.field').split(':').first"

// Text Input Mode - for simple concatenation
"name": "#{_dp('data.source_block.field')} - additional text"
```

## Formula Categories

### 1. [String Formulas](./formulas/string-formulas.md)
String manipulation, text processing, and validation operations.

**Common Use Cases**:
- Text transformation (uppercase, lowercase, trim)
- String parsing and extraction
- Text validation and checking
- String concatenation and formatting

**Examples**:
```json
"clean_name": "=_dp('data.source_block.name').strip.upcase"
"file_extension": "=_dp('data.source_block.file_name').split('.').last"
"status": "=_dp('data.source_block.value').present?"
```

### 2. [Number Formulas](./formulas/number-formulas.md)
Mathematical operations, calculations, and numeric processing.

**Common Use Cases**:
- Basic arithmetic operations
- Rounding and precision control
- Percentage calculations
- Statistical operations

**Examples**:
```json
"total": "=_dp('data.source_block.quantity') * _dp('data.source_block.price')"
"percentage": "=_dp('data.source_block.value') / _dp('data.source_block.total') * 100"
"rounded": "=_dp('data.source_block.decimal').round(2)"
```

### 3. [Date Formulas](./formulas/date-formulas.md)
Date and time operations, formatting, and calculations.

**Common Use Cases**:
- Date parsing and formatting
- Date arithmetic (add/subtract days, months, years)
- Date comparison and validation
- Time zone conversions

**Examples**:
```json
"next_week": "=_dp('data.source_block.date') + 7.days"
"formatted_date": "=_dp('data.source_block.date').strftime('%Y-%m-%d')"
"is_future": "=_dp('data.source_block.date') > Date.today"
```

### 4. [Array/List Formulas](./formulas/array-list-formulas.md)
Array operations, list processing, and hash manipulation.

**Common Use Cases**:
- Array element access and manipulation
- List filtering and mapping
- Hash key-value operations
- Array aggregation and transformation

**Examples**:
```json
"first_item": "=_dp('data.source_block.items').first"
"item_count": "=_dp('data.source_block.items').length"
"filtered_items": "=_dp('data.source_block.items').select { |item| item['status'] == 'active' }"
```

### 5. [Conditional Formulas](./formulas/conditions.md)
If-else logic, boolean operations, and conditional processing.

**Common Use Cases**:
- Conditional value assignment
- Boolean logic and evaluation
- Complex conditional statements
- Default value handling

**Examples**:
```json
"status": "=_dp('data.source_block.value') > 100 ? 'High' : 'Low'"
"message": "=_dp('data.source_block.success') ? 'Success' : 'Failed'"
"category": "=_dp('data.source_block.type') == 'file' ? 'Document' : 'Other'"
```

### 6. [Other Formulas](./formulas/other-formulas.md)
Additional utility functions and operations.

**Common Use Cases**:
- Type checking and conversion
- Null handling and validation
- Specialized operations
- Utility functions

## Formula Best Practices

### 1. Choose the Right Mode
```json
// ✅ Use Formula Mode for data processing
"clean_id": "=_dp('data.source_block.id').split(':').first"

// ✅ Use Text Input Mode for display strings
"message": "Processing: #{_dp('data.source_block.file_name')}"
```

### 2. Keep Formulas Readable
```json
// ✅ Good - clear and readable
"file_extension": "=_dp('data.source_block.file_name').split('.').last"

// ❌ Bad - overly complex
"result": "=_dp('data.source_block.field').split(':').filter { |x| x.length > 0 }.map { |x| x.strip }.join('|')"
```

### 3. Handle Edge Cases
```json
// ✅ Good - handles null values
"name": "=_dp('data.source_block.name').presence || 'Unknown'"

// ❌ Bad - may fail on null
"name": "=_dp('data.source_block.name').upcase"
```

### 4. Test Incrementally
- Start with simple formulas
- Test each operation step by step
- Use the recipe validation tools
- Check for null/empty value handling

## Common Formula Patterns

### 1. Data Transformation
```json
"transformed_field": "=_dp('data.source_block.original_field').method1.method2"
```

### 2. Conditional Assignment
```json
"result": "=_dp('data.source_block.condition') ? _dp('data.source_block.true_value') : _dp('data.source_block.false_value')"
```

### 3. Array Processing
```json
"processed_items": "=_dp('data.source_block.items').select { |item| item['active'] }.map { |item| item['name'] }"
```

### 4. String Manipulation
```json
"clean_text": "=_dp('data.source_block.text').strip.downcase.gsub(/[^a-z0-9]/, '')"
```

## Formula Validation

### CLI Validation
```bash
# Validate recipe with formulas
workato recipes validate --file recipe.json

# Check for formula syntax errors
workato recipes validate --file recipe.json --verbose
```

### Common Formula Errors
1. **Missing equals sign**: Formula must start with `=`
2. **Invalid method calls**: Only allowlisted Ruby methods are supported
3. **Null handling**: Most formulas fail on null values
4. **Syntax errors**: Invalid Ruby syntax in formulas

## Getting Help

### Documentation
- Each formula category has detailed documentation with examples
- Refer to specific formula guides for detailed syntax and usage
- Check the official Workato formula documentation for updates

### Support
- Use `workato recipes validate` to check for errors
- Test formulas incrementally to isolate issues
- Submit support tickets for formula requests not in the allowlist

## Next Steps
- [Naming Conventions](./naming-conventions.md) - Project and asset naming standards
- [String Formulas](./formulas/string-formulas.md) - Text manipulation and processing
- [Number Formulas](./formulas/number-formulas.md) - Mathematical operations
- [Date Formulas](./formulas/date-formulas.md) - Date and time operations
- [Array/List Formulas](./formulas/array-list-formulas.md) - Array and hash operations
- [Conditional Formulas](./formulas/conditions.md) - Logic and conditions
- [Other Formulas](./formulas/other-formulas.md) - Additional utilities
