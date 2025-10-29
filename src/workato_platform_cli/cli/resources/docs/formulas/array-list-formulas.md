---
title: List and Hash Formulas
date: 2022-01-03 05:00:00 Z
page_nav_depth: 3
---

# List and Hash formulas

In addition to the basic data types (for example, string and integer), you may encounter more complex data structures that contain information about multiple items or multiple pieces of information about a single item.

You may encounter these data structures:

- [Lists](#lists-arrays) (also known as arrays)
- [Hashes](#hashes)
- [List of hashes](#lists-of-hashes)

Formulas in Workato are added to allowlists for Ruby methods. Only allowlisted Ruby methods are supported. To request the addition of new formulas to the allowlist, [submit a support ticket](https://support.workato.com/en/support/tickets/new).

---

## Lists (arrays)

Arrays are ordered, integer-indexed collections of any object. List indexing starts at 0. Lists and arrays refer to the same data structure.

In the example below, a list of integers is expressed as:

```ruby
number_list = [100, 101, 102, 103, 104]
```

As lists are ordered, we can use the following formula to get the values. Workato only supports retrieving up to the fifth item using this syntax.

| Formula            | Result |
| ------------------ | ------ |
| number_list.first  | 100    |
| number_list.second | 101    |
| number_list.third  | 102    |
| number_list.fourth | 103    |
| number_list.fifth  | 104    |
| number_list.last   | 104    |

We can also use indexes to get corresponding values. Remember, indexes start at 0:

| Formula        | Result |
| -------------- | ------ |
| number_list[0] | 100    |
| number_list[1] | 101    |
| number_list[2] | 102    |
| number_list[3] | 103    |

Lists in Ruby supports negative indexes.

| Formula         | Result |
| --------------- | ------ |
| number_list[-1] | 104    |
| number_list[-2] | 103    |
| number_list[-3] | 102    |
| number_list[-4] | 101    |

Lists also support ranges as indexes. This returns another list, instead of returning only a value.

| Formula             | Result               |
| ------------------- | -------------------- |
| number_list[0..2]   | [100, 101, 102]      |
| number_list[-3..-1] | [102, 103, 104]      |
| number_list[0..-2]  | [100, 101, 102, 103] |

---

## Hashes

A hash is a dictionary-like collection of unique keys and their values. They are similar to Lists, but where a List uses integers as its index, a Hash allows you to use any object type. Hashes enumerate their values in the order that the corresponding keys were inserted.

Let's take the example of a hash with 2 values, with `'Acme widgets'` and `10` as the values of item_name and item_quantity respectively.

```ruby
line_item = { 'item_name' => 'Acme widgets', 'item_qty' => 10 }
```

| Formula                | Result         |
| ---------------------- | -------------- |
| line_item["item_name"] | "Acme widgets" |
| line_item["item_qty"]  | 10             |

---

## Lists of hashes

Here is an example of an invoice which has multiple line items. It is represented as a list of hashes.

```ruby
line_items = [
  { 'item_no': 1, 'item_name' => 'Acme widgets', 'item_qty' => 10 },
  { 'item_no': 2, 'item_name' => 'RR bearings',  'item_qty' => 99 },
  { 'item_no': 3, 'item_name' => 'Coyote tyres', 'item_qty' => 7 }
]
```

---

### Example list of hashes

The following is an example of a list of hashes called **Contacts**.

This is the Contacts list in a table form:

| name | email        | state | company | company_rev |
| ---- | ------------ | ----- | ------- | ----------- |
| Joe  | joe@abc.om   | CA    | ABC     | 1000        |
| Jill | jill@nbc.com | MA    | NBC     | 1000        |
| Joan | joan@nbc.com | MA    | NBC     | 10000       |
| Jack | jack@hbo.com | CA    | HBO     | 30000       |

This is the Contacts list in a list of hashes form.

```ruby
[
  {
    'name' => 'Joe',
    'email' => 'joe@abc.com',
    'state' => 'CA',
    'company' => 'ABC',
    'company_rev' => 1000,
    'description' => { 'summary' => 'First time buyer', 'estimated_value' => 300 }
  },
  {
    'name' => 'Jill',
    'email' => 'jill@nbc.com',
    'state' => 'MA',
    'company' => 'NBC',
    'company_rev' => 1000,
    'description' => { 'summary' => 'Referral', 'estimated_value' => 500 }
  },
  {
    'name' => 'Joan',
    'email' => 'joan@nbc.com',
    'state' => 'MA',
    'company' => 'NBC',
    'company_rev' => 10000,
    'description' => { 'summary' => 'Recurring customer', 'estimated_value' => 900 }
  },
  {
    'name' => 'Jack',
    'email' => 'jack@hbo.com',
    'state' => 'CA',
    'company' => 'HBO',
    'company_rev' => 30000,
    'description' => { 'summary' => 'Recurring customer', 'estimated_value' => 1000 }
  }
]
```
---

## List formulas

---

### `first`

This formula returns the first item in a list.

It can also be used to return the first _n_ items in a list. In this case, the output will be formatted as a list.

#### Syntax

<kbd>List</kbd>.first(<span style="color:#FF0000">number</span>)

- <kbd>List</kbd> - An input list.
- <span style="color:#FF0000">number</span> - (optional) The number of items to retrieve from the list. If not specified, the formula will return only _one_ item.

#### Sample usage

| Formula                                                 | Result        |
| ------------------------------------------------------- | ------------- |
| <kbd>["One","Two","Three","Four","Five"]</kbd>.first()  | "One"         |
| <kbd>["One","Two","Three","Four","Five"]</kbd>.first(2) | ["One","Two"] |
| <kbd>[1,2,3,4,5]</kbd>.first()                          | 1             |
| <kbd>[1,2,3,4,5]</kbd>.first(3)                         | [1,2,3]       |

#### How it works

This formula returns the first _n_ items from a list. If _n_ is greater than one, the output is formatted as a list.

::: tip Output datatype
If you are returning a single item (i.e. no arguments provided). The output will be formatted according to the item's datatype.

If you are returning more than _one_ item. The output will be formatted as a list datatype.
:::

#### See also

- [last](/formulas/array-list-formulas.md#last): Returns the last _n_ items in a list.
- [where](/formulas/array-list-formulas.md#where): Returns a subset of list items that meet a certain condition.

---

### `last`

This formula returns the last item in a list.

It can also be used to return the last _n_ items in a list. In this case, the output will be formatted as a list.

#### Syntax

<kbd>List</kbd>.last(<span style="color:#FF0000">number</span>)

- <kbd>List</kbd> - An input list.
- <span style="color:#FF0000">number</span> - (optional) The number of items to retrieve from the list. If not specified, the formula will return only _one_ item.

#### Sample usage

| Formula                                                 | Result          |
| ------------------------------------------------------- | --------------- |
| <kbd> ["One","Two","Three","Four","Five"]</kbd>.last()  | "Five"          |
| <kbd> ["One","Two","Three","Four","Five"]</kbd>.last(2) | ["Four","Five"] |
| <kbd>[1,2,3,4,5]</kbd>.last()                           | 5               |
| <kbd>[1,2,3,4,5]</kbd>.last(3)                          | [3,4,5]         |

#### How it works

This formula returns the last _n_ items from a list. If _n_ is greater than one, the output is formatted as a list.

::: tip Output datatype
If you are returning a single item (i.e. no arguments provided). The output will be formatted according to the item's datatype.

If you are returning more than _one_ item. The output will be formatted as a list datatype.
:::

#### See also

- [first](/formulas/array-list-formulas.md#first): Returns the first _n_ items in a list.
- [where](/formulas/array-list-formulas.md#where): Returns a subset of list items that meet a certain condition.

---

### `index`

Returns the index of the first item matching the given value. Returns `nil` if no matching items are found.

#### Syntax

<kbd>Input</kbd>.index(<span style="color:#FF0000">value</span>)

- <kbd>Input</kbd> - An input list.
- <span style="color:#FF0000">value</span> - The value to search for in the list.

#### Sample usage

| Formula               | Result |
| --------------------- | ------ |
| [4, 5, 6, 7].index(6) | 2      |
| [4, 5, 6, 7].index(8) | nil    |

---

### `count`

Returns the number of items in a list.

#### Syntax

`List`.count

- `List` - An input of list datatype.

#### Sample usage

| Formula | Result |
| ------- | ------ |
| `["Hello", "World", "Cat", "Dog"]`.count | 4 |
| `["Hello", "World", ["Sub-array", "Here"]]`.count | 3 |
| `["Hello", "World", nil, ["Sub-array", "Here"]]`.count | 4 |

---

### `where`

Retrieves only the rows (hashes) which satisfy the specified WHERE condition. This formula accepts a single argument in the form of a hash with one or more key-value pairs.

The default operand for the condition is **equal to** (`==`). This formula also supports the following operands. Operands should be added to the end of key separated by a space.

| Name                  | Notation | Example                                  |
| --------------------- | -------- | ---------------------------------------- |
| Equal to (default)    | ==       | leads.where('state': 'CA')               |
| More than             | >        | leads.where('company_revenue >': 10000)  |
| More than or equal to | >=       | leads.where('company_revenue >=': 10000) |
| Less than             | <        | leads.where('company_revenue <': 10000)  |
| Less than or equal to | <=       | leads.where('company_revenue <=': 10000) |
| Not equal to          | !=       | leads.where('state !=': 'CA')            |

::: tip Use datapills as the conditional argument
Instead of using a static value (for example, `'CA'`), you can use a datapill as the conditional argument. The value of the datapill will be processed at run-time.

`contacts.where(state: ` <kbd>datapill</kbd> `)`
:::

#### Sample usage

::: details Example of a single where condition
`contacts.where('state': 'CA')` returns the following rows:

| name | email        | state | company | company_rev |
| ---- | ------------ | ----- | ------- | ----------- |
| Joe  | joe@abc.om   | CA    | ABC     | 1000        |
| Jack | jack@hbo.com | CA    | HBO     | 30000       |

These rows will be expressed as a list of hashes:

```ruby
[
  {
    'name' => 'Joe',
    'email' => 'joe@abc.com',
    'state' => 'CA',
    'company' => 'ABC',
    'company_rev' => 1000
  },
  {
    'name' => 'Jack',
    'email' => 'jack@hbo.com',
    'state' => 'CA',
    'company' => 'HBO',
    'company_rev' => 30000
  }
]
```

:::

::: details Example of compound where formula
A compound WHERE formula will retrieve only the rows that matches all the conditions.

`contacts.where('state': 'CA', 'company_revenue >=': 10000)`

Returns the following rows:

| name | email        | state | company | company_rev |
| ---- | ------------ | ----- | ------- | ----------- |
| Jack | jack@hbo.com | CA    | HBO     | 30000       |

These rows will be expressed as a list of hashes:

```ruby
[
  {
    'name' => 'Jack',
    'email' => 'jack@hbo.com',
    'state' => 'CA',
    'company' => 'HBO',
    'company_rev' => 30000
  }
]
```

---

::: danger Warning - MULTIPLE CONDITIONS IN A SINGLE KEY

Only the last condition is considered when you apply multiple conditions to the same key in a compound WHERE formula. This overrides previous conditions, and can lead to unexpected outcomes.

The following example shows that applying multiple conditions for `state`, returns only rows that contain the second `MA` key:


`contacts.where('state': 'CA', 'state': 'MA')`

returns only rows with states that are `MA`:

| name | email        | state | company | company_rev |
| ---- | ------------ | ----- | ------- | ----------- |
| Jill | jill@nbc.com | MA    | NBC     | 1000       |
| Joan | joan@nbc.com | MA    | NBC     | 10000       |

These rows will be returned as a list of hashes.

```ruby
[
  {
    'name' => 'Jill',
    'email' => 'jill@nbc.com',
    'state' => 'MA',
    'company' => 'NBC',
    'company_rev' => 1000
  },
  {
    'name' => 'Joan',
    'email' => 'joan@nbc.com',
    'state' => 'MA',
    'company' => 'NBC',
    'company_rev' => 10000
  }
]
```
:::

::: details Example of multiple matches
You can filter out records based on a particular field against more than 1 value. This is done by passing an array value in the WHERE condition.

`contacts.where('company': ['ABC','HBO'])`

This WHERE condition will return rows where the company is either **ABC** or **HBO**:

| name | email        | state | company | company_rev |
| ---- | ------------ | ----- | ------- | ----------- |
| Joe  | joe@abc.om   | CA    | ABC     | 1000        |
| Jack | jack@hbo.com | CA    | HBO     | 30000       |

These rows will be returned as a list of hashes.

```ruby
[
  {
    'name' => 'Joe',
    'email' => 'joe@abc.com',
    'state' => 'CA',
    'company' => 'ABC',
    'company_rev' => 1000
  },
  {
    'name' => 'Jack',
    'email' => 'jack@hbo.com',
    'state' => 'CA',
    'company' => 'HBO',
    'company_rev' => 30000
  }
]
```

:::

::: details Example where condition with pattern matching
You can also filter out records using regex. This is done by passing a regex instead of a string.

`contacts.where('name': /^Jo/)`

This WHERE condition will return rows where the name starts with **Jo**:

| name | email        | state | company | company_rev |
| ---- | ------------ | ----- | ------- | ----------- |
| Joe  | joe@abc.om   | CA    | ABC     | 1000        |
| Joan | joan@nbc.com | MA    | NBC     | 10000       |

These rows will be expressed as a list of hashes:

```ruby
[
  {
    'name' => 'Joe',
    'email' => 'joe@abc.com',
    'state' => 'CA',
    'company' => 'ABC',
    'company_rev' => 1000
  },
  {
    'name' => 'Joan',
    'email' => 'joan@nbc.com',
    'state' => 'MA',
    'company' => 'NBC',
    'company_rev' => 10000
  }
]
```

:::

::: details Example where condition with pattern matching (using datapills)
You may use data pills within a regex pattern to dynamically change the string that you are matching. However, using variables in a regex pattern requires escaping within the regex expression.

For example: `contacts.where(state: /#{` <kbd>datapill</kbd> `}/)`

The image below shows the method used to obtain all the 'Emails' in lookup table where the value in the 'State' column contains the string in the datapill from Salesforce, `State | Step 2`.

![Datapill in regex expression](~@img/formula-docs/regex-datapill.png)
_Using datapills in regex expressions_

**Note:** All regex metacharacters will need to be escaped if they should not be interpreted as metacharacters.
:::

::: details Example of chaining where conditions
If a series of WHERE conditions are chained, the formula evaluates each where condition in series.

`contacts.where('state': 'CA').where('company_revenue >=': 10000)` returns the following rows, which is the same as the compound where formula:

| name | email        | state | company | company_rev |
| ---- | ------------ | ----- | ------- | ----------- |
| Jack | jack@hbo.com | CA    | HBO     | 30000       |

In this case, however, the chaining will result in an intermediary array:

`contacts.where('state': 'CA')` first returns:

| name | email        | state | company | company_rev |
| ---- | ------------ | ----- | ------- | ----------- |
| Joe  | joe@abc.om   | CA    | ABC     | 1000        |
| Jack | jack@hbo.com | CA    | HBO     | 30000       |

And `.where('company_revenue >=': 10000)` filters this intermediary array further to return only:

| name | email        | state | company | company_rev |
| ---- | ------------ | ----- | ------- | ----------- |
| Jack | jack@hbo.com | CA    | HBO     | 30000       |

Results will be expressed as a list of hashes:

```ruby
[
  {
    'name' => 'Jack',
    'email' => 'jack@hbo.com',
    'state' => 'CA',
    'company' => 'HBO',
    'company_rev' => '30000'
  }
]
```
:::

::: details Example of chaining not operator
You can use the WHERE formula to find the difference between two arrays by chaining a not operator. This is useful if you have two lists, an original list and an updated list, and plan to compare the two to ensure the updated list contains all values from the original list.

For example: `contacts.where.not("id":updated_contacts.pluck('id'))` identifies any values that are present in the original list (`contacts`) and missing from the updated list (`updated_contacts`).
:::

---

### `except`

Returns a hash that includes everything except given keys.

```ruby
hash = { a: true, b: false, c: nil }
hash.except(:c)     # => { a: true, b: false }
hash.except(:a, :b) # => { c: nil }
hash                # => { a: true, b: false, c: nil }
```

---

### `pluck`

Retrieves only the columns which have been specified.

#### Sample usage

::: details Example of a single column output
`contacts.pluck("email")` returns

| email        |
| ------------ |
| joe@abc.com  |
| jill@nbc.com |
| joan@nbc.com |
| jack@hbo.com |

If a single column, results will be returned as an array:

```ruby
["joe@abc.com", "jill@nbc.com", "joan@nbc.com", "jack@hbo.com"]
```

:::

::: details Example of a multiple column dataset
`contacts.where("state ==": "CA").pluck("email", "company")` returns

| email        | company |
| ------------ | ------- |
| joe@abc.com  | ABC     |
| jill@nbc.com | NBC     |
| joan@nbc.com | NBC     |
| jack@hbo.com | HBO     |

Results are returned as a list of a list:

```ruby
[["joe@abc.com", "ABC"], ["jill@nbc.com", "NBC"], ["joan@nbc.com", "NBC"], ["jack@hbo.com", "HBO"]]
```

:::

::: details Example of retrieving nested fields
This method can be used to extract nested fields. Use the `[<1st-level field>,<2nd-level field>...]` format to define which fields to retrieve.

`contacts.pluck("email", ["description", "summary"])` returns

| email        | summary            |
| ------------ | ------------------ |
| joe@abc.com  | First time buyer   |
| jill@nbc.com | Referral           |
| joan@nbc.com | Recurring customer |
| jack@hbo.com | Recurring customer |

Results are returned as a list of lists:

```ruby
[
  ["joe@abc.com", "First time buyer"],
  ["jill@nbc.com", "Referral"],
  ["joan@nbc.com", "Recurring customer"],
  ["jack@hbo.com", "Recurring customer"]
]
```

:::

---

### `format_map`

Create an array of strings by formatting each row of given array of hashes. Allows you to add static text to the created strings as well. Fields to be represented in the format %{**\<field_name>**}.

#### Sample usage

`contacts.format_map('Name: %{name}, Email: %{email}, Company: %{company}') ` returns

```ruby
[
  'Name: Joe, Email: joe@abc.com, Company: ABC' ,
  'Name: Jill, Email: jill@nbc.com, Company: NBC' ,
  'Name: Joan, Email: joan@nbc.com, Company: NBC' ,
  'Name: Jack, Email: jack@hbo.com, Company: HBO' ,
]
```

The preceding example will give you a list of strings, one string for each row of the list **"contacts"**, using data from 3 of the fields: name, email, and company, as stated.

---

### `join`

Combines all items in a list into a text string. A separator is placed between each item.

#### Syntax

<kbd>List</kbd>.join(<span style="color:#FF0000">separator</span>)

- <kbd>List</kbd> - An input of list datatype.
- <span style="color:#FF0000">separator</span> - The character to add between items when they are joined. If no separator is specified, the list items will be joined together.

#### Sample usage

| Formula                                      | Result          |
| -------------------------------------------- | --------------- |
| <kbd>["Ms", "Jean", "Marie"]</kbd>.join("-") | "Ms-Jean-Marie" |
| <kbd>[1,2,3]</kbd>.join("--")                | "1--2--3"       |
| <kbd>["ab", "cd", "ef"]</kbd>.join           | "abcdef"        |

#### How it works

The list items are combined into a single text string. The separator characters is added between each item.

::: tip Separator character
You can use a string of characters together as the separator argument (for example, `", "`).

<kbd>["Open","Pending","Closed"]</kbd>.join(", ") returns `"Open, Pending, Closed"`.
:::

#### See also

- [split](/formulas/string-formulas.md#split): Divides a string around a specified character and returns an array of strings.

---

### `smart_join`

Joins list elements into a string. Removes empty and nil values and trims any white space before joining.

#### Syntax

<kbd>List</kbd>.smart_join(<span style="color:#FF0000">separator</span>)

- <kbd>List</kbd> - An input of list datatype.
- <span style="color:#FF0000">separator</span> - The character to add between items when they are joined. If no separator is specified, a blank space will be used as the joining character.

#### Sample usage

| Formula                                                                               | Result                                         |
| ------------------------------------------------------------------------------------- | ---------------------------------------------- |
| <kbd>[nil, "", "Hello", " ", "World"]</kbd>.smart_join(" ")                           | "Hello World"                                  |
| <kbd>["111 Vinewood Drive", "", "San Francisco", "CA", "95050"]</kbd>.smart_join(",") | "111 Vinewood Drive, San Francisco, CA, 95050" |

---

### `concat`

Concatenates 2 lists into a single list. Nested lists will NOT be flattened.

#### Syntax

<kbd>List</kbd>.concat(<span style="color:#FF0000">list_to_be_joined</span>)

- <kbd>List</kbd> - An input of list datatype.
- <span style="color:#FF0000">list_to_be_joined</span> - The other list to be concatenated with the original list input.

#### Sample usage

| Formula                                                                                           | Result                                                                        |
| ------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| <kbd>["Hello", "World"]</kbd>.concat(<kbd>["Workato", "Rocks"]</kbd>)                             | <kbd>["Hello", "World", "Workato", "Rocks"]</kbd>                             |
| <kbd>["Hello", "World", ["Sub-array", "Here"]]</kbd>.concat(<kbd>["Workato", "Rocks"]</kbd>)      | <kbd>["Hello", "World", ["Sub-array", "Here"], "Workato", "Rocks"]</kbd>      |
| <kbd>["Hello", "World", nil, ["Sub-array", "Here"]]</kbd>.concat(<kbd>["Workato", "Rocks"]</kbd>) | <kbd>["Hello", "World", nil, ["Sub-array", "Here"], "Workato", "Rocks"]</kbd> |

---

### `reverse`

Reverses the order of a list.

#### Syntax

<kbd>List</kbd>.reverse

- <kbd>List</kbd> - An input of list datatype.

#### Sample usage

| Formula                                            | Result                          |
| -------------------------------------------------- | ------------------------------- |
| <kbd>["Joe", "Jill", "Joan", "Jack"]</kbd>.reverse | ["Jack", "Joan", "Jill", "Joe"] |
| <kbd>[100, 101, 102, 103]</kbd>.reverse            | [103, 102, 101, 100]            |

---

### `sum`

For integers and decimals, the numbers will be added together and the total sum obtained. For strings, the strings will be concatenated together to form a longer string.

#### Syntax

<kbd>List</kbd>.sum

- <kbd>List</kbd> - An input of list datatype.

#### Sample usage

| Formula                       | Result   |
| ----------------------------- | -------- |
| <kbd>[1, 2, 3]</kbd>.sum      | 6        |
| <kbd>[1.5, 2.5, 3]</kbd>.sum  | 7.0      |
| <kbd>["abc", "xyz"]</kbd>.sum | "abcxyz" |

---

### `uniq`

Returns a list containing unique items.

#### Syntax

<kbd>List</kbd>.uniq

- <kbd>List</kbd> - An input of list datatype.

#### Sample usage

| Formula                                                | Result                 |
| ------------------------------------------------------ | ---------------------- |
| <kbd>["joe", "jack", "jill", "joe", "jack"]</kbd>.uniq | ["joe","jack", "jill"] |
| <kbd>[1, 2, 3, 1, 1, 3]</kbd>.uniq                     | [1, 2, 3]              |
| <kbd>[1.0, 1.5, 1.0]</kbd>.uniq                        | [1.0, 1.5]             |

---

### `flatten`

Flattens a multi-dimensional array (i.e. array of arrays) to a single dimension array.

#### Syntax

<kbd>List</kbd>.flatten

- <kbd>List</kbd> - An input of list datatype.

#### Sample usage

| Formula                                        | Result                |
| ---------------------------------------------- | --------------------- |
| <kbd>[[1, 2, 3], [4, 5, 6]]</kbd>.flatten      | [1, 2, 3, 4, 5, 6]    |
| <kbd>[[1, [2, 3], 3], [4, 5, 6]]</kbd>.flatten | [1, 2, 3, 3, 4, 5, 6] |
| <kbd>[[1, [2, 3], 9], [9, 8, 7]]</kbd>.flatten | [1, 2, 3, 9, 9, 8, 7] |

---

### `length`

Returns the number of elements in self. Returns 0 if the list is empty.

#### Syntax

<kbd>List</kbd>.length

- <kbd>List</kbd> - An input of list datatype.

#### Sample usage

| Formula                               | Result |
| ------------------------------------- | ------ |
| <kbd>[ 1, 2, 3, 4, 5 ]</kbd>.length   | 5      |
| <kbd>[{..}, {..}, {..}]</kbd>.length  | 3      |
| <kbd>[" ", nil, "", nil]</kbd>.length | 4      |
| <kbd>[]</kbd>.length                  | 0      |

---

### `max`

Returns largest value in an array. When comparing numbers, the largest number is returned. When comparing strings, the string with the largest ASCII value is returned.

#### Syntax

<kbd>List</kbd>.max

- <kbd>List</kbd> - An input of list datatype.

#### Sample usage

| Formula                               | Result |
| ------------------------------------- | ------ |
| <kbd>[-5, 0, 1, 2, 3, 4, 5]</kbd>.max | 5      |
| <kbd>[-1.5, 1.5, 2, 3, 3.5]</kbd>.max | 3.5    |
| <kbd>["cat", "dog", "rat"]</kbd>.max  | "rat"  |

---

### `min`

Returns smallest value in an array. When comparing numbers, the smallest number is returned. When comparing strings, the string with the smallest ASCII value is returned.

#### Syntax

<kbd>List</kbd>.min

- <kbd>List</kbd> - An input of list datatype.

#### Sample usage

| Formula                               | Result |
| ------------------------------------- | ------ |
| <kbd>[-5, 0, 1, 2, 3, 4, 5]</kbd>.min | -5     |
| <kbd>[-1.5, 1.5, 2, 3, 3.5]</kbd>.min | -1.5   |
| <kbd>["cat", "dog", "rat"]</kbd>.min  | "cat"  |

---

### `compact`

Removes nil values from array and hash.

#### Sample usage

| Formula                                         | Result             |
| ----------------------------------------------- | ------------------ |
| <kbd>["foo", nil, "bar"]</kbd>.compact          | ["foo", "bar"]     |
| <kbd>{ foo: 1, bar: nil, baz: 2 }</kbd>.compact | { foo: 1, baz: 2 } |

---

## Conditionals

---

### `blank?`

This formula checks the input string and returns true if it is an empty string or if it is null.

#### Syntax

<kbd>Input</kbd>.blank?

- <kbd>Input</kbd> - An input datapill. It can be a string, number, date, or datetime datatype.

#### Sample usage

| Formula                       | Result |
| ----------------------------- | ------ |
| <kbd>"Any Value"</kbd>.blank? | false  |
| <kbd>123</kbd>.blank?         | false  |
| <kbd>0</kbd>.blank?           | false  |
| <kbd>""</kbd>.blank?          | true   |

#### How it works

If the input is null or an empty string, the formula will return true. For any other data, it returns false.

#### See also

- [presence](/formulas/string-formulas.md#presence): Returns the data if it exists, returns nil if it does not.
- [present?](/formulas/string-formulas.md#present): Returns true if there is a valid input.

---

### `include?`

Checks if the string contains a specific substring, or if a list contains an element. Returns true if it does.

#### Syntax

<kbd>Input</kbd>.include?(<span style="color:#FF0000">substring</span>)

- <kbd>Input</kbd> - A string or list input.
- <span style="color:#FF0000">substring_or_element</span> - The substring or element to check for.

#### Sample usage

| Formula                                                                                        | Result |
| ---------------------------------------------------------------------------------------------- | ------ |
| <kbd>"Partner account"</kbd>.include?("Partner")                                               | true   |
| <kbd>"Partner account"</kbd>.include?("partner")                                               | false  |
| <kbd>["Hello", "World", ["Sub-array","Here"]"]</kbd>.include?("Hello")                         | true   |
| <kbd>["Hello", "World", ["Sub-array","Here"]"]</kbd>.include?(<kbd>["Sub-array","Here"]</kbd>) | true   |

#### How it works

This formula check is the string contains a specific substring, or if a list contains a specific element. Returns true if it does, otherwise, returns false. The substring comparison is case sensitive, and the element comparison is exact match.

This function acts in an opposite manner from [exclude?](#exclude). The latter will return true only if the input string/list does NOT contain the stated keyword/element.

#### See also

- [exclude?](#exclude): Checks if the string contains a specific substring, or if a list contains an element. Returns false if it does.

---

### `exclude?`

Checks if the string contains a specific substring, or if a list contains an element. Returns false if it does.

#### Syntax

<kbd>Input</kbd>.exclude?(<span style="color:#FF0000">substring</span>)

- <kbd>Input</kbd> - A string or list input.
- <span style="color:#FF0000">substring_or_element</span> - The substring or element to check for.

#### Sample usage

| Formula                                                                                        | Result |
| ---------------------------------------------------------------------------------------------- | ------ |
| <kbd>"Partner account"</kbd>.exclude?("Partner")                                               | false  |
| <kbd>"Partner account"</kbd>.exclude?("partner")                                               | true   |
| <kbd>["Hello", "World", ["Sub-array","Here"]"]</kbd>.include?("Hello")                         | false  |
| <kbd>["Hello", "World", ["Sub-array","Here"]"]</kbd>.include?(<kbd>["Sub-array","Here"]</kbd>) | false  |

#### How it works

This formula check is the string contains a specific substring, or if a list contains a specific element. Returns false if it does, otherwise, returns true. The substring comparison is case sensitive, and the element comparison is exact match.

This function acts in an opposite manner from [include?](#include). The latter will return true only if the input string/list contains the stated keyword/element.

#### See also

- [include?](#include): Checks if the string contains a specific substring, or if a list contains an element. Returns true if it does.

---

### `present?`

This formula will check the input and if there is a value present, it will return true. If the input is nil, boolean false, an empty string, or an empty list, the formula will return false.

#### Syntax

<kbd>Input</kbd>.present?

- <kbd>Input</kbd> - An input datapill. It can be a string, number, date, or list datatype.

#### Sample usage

| Formula                                                | Result |
| ------------------------------------------------------ | ------ |
| <kbd>"Any Value"</kbd>.present?                        | true   |
| <kbd>123</kbd>.present?                                | true   |
| <kbd>0</kbd>.present?                                  | true   |
| <kbd>"2017-04-02T12:30:00.000000-07:00"</kbd>.present? | true   |
| <kbd>nil</kbd>.present?                                | false  |
| <kbd>""</kbd>.present?                                 | false  |
| <kbd>[]</kbd>.present?                                 | false  |

#### How it works

If the input is null, an empty string or an empty list, the formula will return false. For any other data, it returns true.

::: tip Evaluating a list with nil values

- Only an empty list will return false.

<kbd>[]</kbd>.present? returns false.

- A list with nil and empty string will return true.

<kbd>[nil,""]</kbd>.present? returns true.
:::

#### See also

- [presence](/formulas/array-list-formulas.md#presence): Returns the data if it exists, returns nil if it does not.
- [blank?](/formulas/array-list-formulas.md#blank): Returns nil if the data does not exist or if the string consist of only white spaces.

---

### `presence`

Returns the data if it exists, returns nil if it does not.

#### Syntax

<kbd>Input</kbd>.presence

- <kbd>Input</kbd> - An input datapill. It can be a string, number, date, or datetime datatype.

#### Sample usage

| Formula                         | Result      |
| ------------------------------- | ----------- |
| <kbd>nil</kbd>.presence         | nil         |
| <kbd>""</kbd>.presence          | nil         |
| <kbd>"Any Value"</kbd>.presence | "Any Value" |
| <kbd>45.0</kbd>.presence        | 45.0        |
| <kbd>0</kbd>.presence           | 0           |

#### How it works

If the input is null or an empty string, the formula will return nil. For any other data, it returns the original input data.

#### See also

- [blank?](/formulas/array-list-formulas.md#blank): Returns nil if the data does not exist or if the string consist of only white spaces.
- [present?](/formulas/array-list-formulas.md#present): Returns true if there is a valid input.

---

## Conversion

---

The following formulas allows you to convert data from arrays to other data types

---

### `to_csv`

Generates CSV line from an array. This handles escaping. Nil values and empty strings will also be expressed within the csv line.

#### Syntax

<kbd>Input</kbd>.to_csv

- <kbd>Input</kbd> - An input of list datatype.

#### Sample usage

| Formula                                                            | Result                            |
| ------------------------------------------------------------------ | --------------------------------- |
| <kbd>["John Smith", "No-Email", " ", nil, "555-1212"]</kbd>.to_csv | "John Smith,No-Email, ,,555-1212" |
| <kbd>["John Smith", "No-Email", " ", nil, 1212]</kbd>.to_csv       | "John Smith,No-Email, ,,1212"     |

---

### `to_json`

Converts hash or array to JSON string.

#### Syntax

<kbd>Input</kbd>.to_json

- <kbd>Input</kbd> - An input datapill. It can be a list or hash datatype.

#### Sample usage

| Formula                                                | Result                       |
| ------------------------------------------------------ | ---------------------------- |
| <kbd>{"pet" => "cat", "color" => "gray"}</kbd>.to_json | {"pet":"cat","color":"gray"} |
| <kbd>["1","2","3"]</kbd>.to_json                       | ["1", "2", "3"]              |

---

### `to_xml`

Converts hash or array into XML string.

#### Syntax

<kbd>Input</kbd>.to_xml

- <kbd>Input</kbd> - An input datapill. It can be a list or hash datatype.

#### Sample usage

| Formula                                              | Result                                             |
| ---------------------------------------------------- | -------------------------------------------------- |
| <kbd>{"name" => "Ken"}</kbd>.to_xml(root: "user")    | \<user>\<name>Ken\</name>\</user>                  |
| <kbd>[{"name" => "Ken"}]</kbd>.to_xml(root: "users") | \<users>\<user>\<name>Ken\</name>\</user>\</users> |

---

### `from_xml`

Converts XML string to hash.

#### Syntax

<kbd>Input</kbd>.from_xml

- <kbd>Input</kbd> - Input XML data.

#### Sample usage

::: details Converting XML string to hash

This XML string:

`<?xml version=\"1.0\" encoding=\"UTF-8\" ?> <hash><foo type="integer">123</foo></hash>`

represents the following XML data.

```xml
<?xml version=\"1.0\" encoding=\"UTF-8\" ?>

<hash>
  <foo type="integer">123</foo>
</hash>

```

<kbd>XML string</kbd>.from_xml will return the following hash.

```ruby
{ "hash":
  [ "foo":
    [
      { "@type": "integer",
        "content!": "1"
      }
    ]
  ]
}
```

:::

---

### `encode_www_form`

Join hash into url-encoded string of parameters.

#### Syntax

<kbd>Input</kbd>.encode_www_form

- <kbd>Input</kbd> - An input of hash datatype.

#### Sample usage

| Formula                                                         | Result                |
| --------------------------------------------------------------- | --------------------- |
| <kbd>{"apple" => "red green", "2" => "3"}</kbd>.encode_www_form | "apple=red+green&2=3" |

---

### `to_param`

Returns a string representation for use as a URL query string.

#### Syntax

<kbd>Input</kbd>.to_param

- <kbd>Input</kbd> - An input of hash datatype.

#### Sample usage

| Formula                                       | Result             |
| --------------------------------------------- | ------------------ |
| <kbd>{name: 'Jake', age: '22'}</kbd>.to_param | "name=Jake&age=22" |

---

### `keys`

Returns an array of keys from the input hash.

#### Syntax

<kbd>Input</kbd>.keys

- <kbd>Input</kbd> - An input of hash datatype.

#### Sample usage

| Formula                                           | Result          |
| ------------------------------------------------- | --------------- |
| <kbd>{"name" => 'Jake', "age" => '22'}</kbd>.keys | ["name", "age"] |

---

### `values`

Returns an array of values from the input hash.

#### Syntax

<kbd>Input</kbd>.values

- <kbd>Input</kbd> - An input of hash datatype.

#### Sample usage

| Formula                                           | Result          |
| ------------------------------------------------- | --------------- |
| <kbd>{"name" => 'Jake', "age" => '22'}</kbd>.values | ["Jake", "22"] |

---


## List operands

### Difference (`-`)

Returns the difference between two arrays, meaning a new array that is a copy of the first array without any of the items also present in the second array.

#### Syntax

`list` - `updated_list`

- `-` the difference/subtract operand
- `list` - the original list
- `updated_list` - an updated list


#### Sample usage

Let's say you have two arrays, `contacts` and `updated_contacts`:

`contacts = ["Ariel", "Max", "Kai", "Noam", "Tal"]`

`updated_contacts = ["Ariel", "Max", "Kai", "Lee", "Quinn"]`


|Formula| Result |
|-------|--------|
| `contacts - updated_contacts` | ["Noam", "Tal"] |
| `updated_contacts - contacts` | ["Lee", "Quinn"] |


#### How it works

This operand creates an array that is the difference between the two arrays. The first example, `contacts - updated_contacts`, returns an array of items present in `contacts` but not present in `updated_contacts`. It's important to note that this does not simply remove duplicate items; if we reverse the order of operations, we obtain different results. For example, when we find the difference between `updated_contacts` and `contacts`, the new array contains items that are present in `updated_contacts`, and not present in `contacts`.

#### See also

- [where](/formulas/array-list-formulas.md#where): Returns a subset of list items that meet a certain condition. Reference the example on chaining not operands to use `where` to compare two lists.

---

### Union (`&`)

While Workato does not support the union (`&`) operand to manipulate arrays directly, you can achieve a similar result by combining the [concat](#concat) and [uniq](#uniq) formulas.

#### Syntax

`list.concat(updated_list).uniq`

- `list` - a list
- `concat` - concatenates two lists into a single list
- `updated_list` - an updated list
- `uniq` - returns a list containing unique values

#### Sample usage

| Formula | Result |
|---------|--------|
| `contacts.concat(updated_contacts).uniq` | ["Ariel", "Kai", "Lee", "Max", "Noam", "Quinn", "Tal"]

#### How it works

`concat` concatenates two lists into a single list, and `uniq` returns a list containing unique items. You can combine two lists and remove any duplicate items that may appear by combining the two formulas.
