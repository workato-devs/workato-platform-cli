---
title: Formula mode - Add conditions to formulas
date: 2021-06-28 00:00:00 Z
---

# Add conditions to formulas
It is also important to create recipes that are resilient against unexpected scenarios. For example, your trigger data might contain missing values or contain a data of another datatype.

You can use conditional logic to prepare your recipes for these situations.

## Conditionals
You can conditionally execute formulas using Ruby's ternary syntax (popular shortcut for if-else statements). Ternary syntax are of the form:

```
condition ? expression1 : expression2
```

### Behavior
#### `condition`
A boolean expression that evaluates to `true` or `false`.

#### `expression1`
Returns this expression if `condition` is `true`.

#### `expression2`
Returns this expression if `condition` is `false`.

## Example: Using first name or full name
In the following example, we conditionally pass in either the <kbd>Full name</kbd> or <kbd>First name</kbd> into the <kbd>Message</kbd> input field.

![Ternary syntax](~@img/formula-docs/ternary-formula.png)
*Checks if <kbd>Full name</kbd> is present. Outputs <kbd>Full name</kbd> if present, or <kbd>First name</kbd> if not present.*

Here is a detailed explanation of what the ternary formula does:

1. <code><kbd>Full name</kbd>.present?</code> will check if the <kbd>Full name</kbd> pill has a value . If it has a value, it evaluates to `true`. If it has no value, it evaluates to `false`.
2. The second `?` in the formula separates the condition to evaluate from the expressions to return. Note, the first `?` is part of the [`.present?` formula](/formulas/string-formulas.md#present) whilst the second `?` is separated with a space character and is part of the ternary syntax.
3. If there is a value in the <kbd>Full name</kbd> pill when the job is ran, the value for <kbd>Full name</kbd> will mapped to the **Message** input.
4. If there is no value in the <kbd>Full name</kbd> pill when the job is ran, the value for <kbd>First name</kbd> will be mapped to the **Message** input. Of course, if there's also no value in this <kbd>First name</kbd> pill, the job will fail at this step if **Message** is a required input field.

For more information on Ruby's ternary syntax, check out this [article](http://www.w3resource.com/ruby/ruby-ternary-operator.php).

## Example: Skip field if empty
When updating records, you want to preserve existing data while changing only the updated fields. In this situation, can you use the `skip` formula to instruct the Workato action to leave this field untouched.

This example attempts use an updated Salesforce record to update a lead in Marketo. It checks if the Salesforce <kbd>Company</kbd> is present. If yes, it will output the Salesforce <kbd>Company</kbd> into Marketo. Otherwise, the Marketo record is left untouched.

![Skip syntax](~@img/formula-docs/skip-formula.png)
*Checks if <kbd>Company</kbd> is present. Outputs <kbd>Company</kbd> if present, otherwise, leaves this field untouched*

::: tip How to avoid passing any values
The [skip formula](/formulas/other-formulas.md#skip) will avoid passing any data to the input field.
:::

## Safe navigation operator

Checks if the input is not `nil` or undefined. If true, it performs a specified operation on the input data. Otherwise, it returns a `nil` value.

### Syntax

<kbd>Input</kbd>&.<span style="color:#FF0000">operation</span>

- <kbd>Input</kbd> - An input datapill. It can be any datatype.
- <span style="color:#FF0000">operation</span> - If the input is not `nil`, this formula is applied to the input data. This formula must be compatible with the input datatype.

### How it works

The safe navigation operator (`&.`) checks if the input data is not `nil` or undefined. If the input data exists, it performs the operation specified by the <span style="color:#FF0000">operation</span> argument. Otherwise, it returns `nil`. This operator enables you to write simpler expressions to handle `nil` values.

#### Example: Converting dates safely

You can use the safe navigation operator when you're working with a datapill that might contain `nil` values.

For example, applying the `to_date` formula directly to the <Datapill step="1">Created Date</Datapill> datapill would cause a `NoMethodError` if the datapill value is `nil`. The safe navigation operator enables you to handle these cases without complex ternary expressions.

```ruby
# Instead of: created_date.present? ? created_date.to_date(format:"MM/DD/YYYY") : nil
created_date&.to_date(format:"MM/DD/YYYY")
```

![Using safe navigation operator](~@img/formula-docs/safe-navigation-after.png)
_Using the safe navigation operator_

### Example: Safe hash retrieval

You can also use the safe navigation operator when you have a nested hash structure, such as a customer record with optional address information.

**With safe navigation**:

```ruby
# This returns nil instead of an error if any key is missing
customer["address"]&.[]("billing")&.[]("zip_code")
```

**Without safe navigation**:

```ruby
# This could fail if "address" or "billing" doesn't exist
customer["address"]["billing"]["zip_code"]
```

The safe navigation operator prevents errors by returning `nil` if any key is missing. This approach allows you to retrieve nested hash values without worrying about `NoMethodError` exceptions.
