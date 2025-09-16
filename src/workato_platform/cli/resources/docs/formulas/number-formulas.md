---
title: Number formulas
date: 2017-03-30 05:00:00 Z
page_nav_depth: 3
---

# Number formulas
In Ruby, Fixnum refers to integers, such as 9, 10, and 11, while Float refers to decimals, such as 1.75 and 2.5. Workato supports a variety of Fixnum and Float formulas.

Formulas in Workato are allowlisted Ruby methods. Syntax and functionality for these formulas are generally unchanged. Most formulas return an error and stop the job if the formula operates on nulls (expressed as `nil` in Ruby), except for `present?`, `presence`, and `blank?`.

You can refer to the Ruby documentation for [Fixnum (integers)](http://ruby-doc.org/core-2.3.3/Fixnum.html) and [Float (decimals)](http://ruby-doc.org/core-2.3.3/Float.html) for more information. However, only allowlisted Ruby methods are supported. To request the addition of new formulas to the allowlist, [submit a support ticket](https://support.workato.com/en/support/tickets/new).

## Arithmetic operations
In the cases of arithmetic operations, whether the values are of integer types or decimal (float) types are important. Formulas will always stick to the types given as input, and the returned result will be of the most precise type.

For example:
- If integer values are provided, an integer value will be returned.
- If float values are provided, a float value will be returned.
- If both float and integer values are provided, a float value will be returned, as that is more precise.

### The add (+) operator

This operator allows the addition of operands on either side. This section talks about number arithmetic. Date arithmetic is possible as well and can be found [here](/formulas/date-formulas.md#date-arithmetic).

#### Sample usage
| Formula    | Result | Type   |
| ----------- | ------ | ------ |
| 4 + 7     | 11     | Fixnum |
| 4.0 + 7   | 11.0   | Float  |
| 4.0 + 7.0 | 11.0   | Float  |

---

### The subtract (-) operator

This operator subtracts the right hand operand from the left hand operand. This section talks about number arithmetic. Date arithmetic is possible as well and can be found [here](/formulas/date-formulas.md#date-arithmetic).

#### Sample usage
| Formula    | Result | Type   |
| ----------- | ------ | ------ |
| 4 - 7     | -3     | Fixnum |
| 4.0 - 7   | -3.0   | Float  |
| 4.0 - 7.0 | -3.0   | Float  |

---

### The multiply (\*) operator
This operator multiplies the operands on either side.

#### Sample usage
| Formula    | Result | Type   |
| ----------- | ------ | ------ |
| 4 * 7     | 28     | Fixnum |
| 4.0 * 7   | 28.0   | Float  |
| 4.0 * 7.0 | 28.0   | Float  |

---

### The divide (/) operator

Divides left hand operand by right hand operand.

#### Sample usage
| Formula    | Result      | Type   |
| ----------- | ----------- | ------ |
| 4 / 7     | 0           | Fixnum |
| 4.0 / 7   | 0.571428... | Float  |
| 7 / 4     | 1           | Fixnum |
| 7 / 4.0   | 1.75        | Float  |
| 7.0 / 4   | 1.75        | Float  |
| 7.0 / 4.0 | 1.75        | Float  |

---

### The exponential (\*\*) operator

Left hand operand to the power of the right hand operand.

#### Sample usage
| Formula     | Result      | Type     |
| ------------ | ----------- | ---------|
| 5**3       | 125         | Fixnum   |
| 4**1.5     | 8.0         | Float    |
| 4.0**2     | 16.0        | Float    |
| 3**-1      | "1/3"       | Rational |
| 8**(3**-1) | 2.0         | Float    |
| 7**-1.6    | 0.044447... | Float    |

---

### The modulo (%) operator

Divides left hand operand by right hand operand and returns the remainder.

#### Sample usage
| Formula    | Result | Type   |
| ----------- | ------ | ------ |
| 4 % 7     | 4      | Fixnum |
| 4.0 % 7   | 4.0    | Float  |
| 4 % 7.0   | 4.0    | Float  |
| 7 % 4     | 3      | Fixnum |
| 7.0 % 4.0 | 3.0    | Float  |

---

## Other number formulas

### `abs`

Returns the absolute (positive) value of a number.

#### Syntax

<kbd>number</kbd>.abs

- <kbd>number</kbd> - An input integer or float.

#### Sample usage

| Formula               | Result |
| --------------------- | ------ |
| <kbd>45</kbd>.abs     | 45     |
| <kbd>-45</kbd>.abs    | 45     |
| <kbd>45.67</kbd>.abs  | 45.67  |
| <kbd>-45.67</kbd>.abs | 45.67  |

---

### `round`

Rounds off a numerical value. This formula returns a value with a specified number of decimal places.

#### Syntax

<kbd>number</kbd>.round(<span style="color:#FF0000">offset</span>)

- <kbd>number</kbd> - An input integer or float.
- <span style="color:#FF0000">offset</span> - (optional) The number of decimal places to return, you can provide negative values. If not specified, this formula will return the number with no decimal places.

#### Sample usage

| Formula                       | Result  |
| ----------------------------- | ------- |
| <kbd>1234.567</kbd>.round     | 1235    |
| <kbd>1234.567</kbd>.round(2)  | 1234.57 |
| <kbd>1234.567</kbd>.round(-2) | 1230    |

---

## Conditionals

### `blank?`

This formula checks the input and returns `true` if:

- Input is a non-value number, sometimes referred to as NaN (not a number). This is an undefined value or value that cannot be represented. For example, the result of division by zero, or a missing value.
- Input is null.

#### Syntax

<kbd>Input</kbd>.blank?

- <kbd>Input</kbd> - An input datapill. It can be a string, number, date, or datetime datatype.

#### Sample usage

| Formula                       | Result  |
| ----------------------------- | ------- |
| <kbd>123</kbd>.blank?         | false   |
| <kbd>0</kbd>.blank?           | false   |
| <kbd>nil</kbd>.blank?         | true    |
| <kbd>""</kbd>.blank?          | true    |

#### How it works

If the input is null or an empty string, the formula will return true. For any other data, it returns false.

#### See also

- [presence](/formulas/number-formulas.md#presence): Returns the data if it exists, returns nil if it does not.
- [present?](/formulas/number-formulas.md#present): Returns true if there is a valid input.

---

### `even?`

Checks the integer input and returns true if it is an even number.

#### Syntax

<kbd>integer</kbd>.even?

- <kbd>integer</kbd> - An input integer.

#### Sample usage

| Formula               | Result |
| --------------------- | ------ |
| <kbd>123</kbd>.even?  | false  |
| <kbd>1234</kbd>.even? | true   |

#### See also

- [odd?](/formulas/number-formulas.md#odd): Checks the integer input and returns true if it is an odd number.

---

### `odd?`

Checks the integer input and returns true if it is an odd number.

#### Syntax

<kbd>integer</kbd>.odd?

- <kbd>integer</kbd> - An input integer.

#### Sample usage

| Formula              | Result |
| -------------------- | ------ |
| <kbd>123</kbd>.odd?  | true   |
| <kbd>1234</kbd>.odd? | false  |

#### See also

- [even?](/formulas/number-formulas.md#even): Checks the integer input and returns true if it is an even number.

---

### `present?`

This formula will check the input and if there is a value present, it will return true. If the input is nil, boolean false, an empty string, or an empty list, the formula will return false.

#### Syntax

<kbd>Input</kbd>.present?

- <kbd>Input</kbd> - An input datapill. It can be a string, number, date, or list datatype.

#### Sample usage

| Formula                                                | Result  |
| ------------------------------------------------------ | ------- |
| <kbd>"Any Value"</kbd>.present?                        | true    |
| <kbd>123</kbd>.present?                                | true    |
| <kbd>0</kbd>.present?                                  | true    |
| <kbd>"2017-04-02T12:30:00.000000-07:00"</kbd>.present? | true    |
| <kbd>nil</kbd>.present?                                | false   |
| <kbd>""</kbd>.present?                                 | false   |
| <kbd>[]</kbd>.present?                                 | false   |

#### How it works

If the input is null, an empty string or an empty list, the formula will return false. For any other data, it returns true.

::: tip Evaluating a list with nil values
- Only an empty list will return false.

<kbd>[]</kbd>.present? returns false.

- A list with nil and empty string will return true.

<kbd>[nil,""]</kbd>.present? returns true.
:::

#### See also

- [presence](/formulas/number-formulas.md#presence): Returns the data if it exists, returns nil if it does not.
- [blank?](/formulas/number-formulas.md#blank): Returns nil if the data does not exist or if the string consist of only white spaces.

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

- [blank?](/formulas/number-formulas.md#blank): Returns nil if the data does not exist or if the string consist of only white spaces.
- [present?](/formulas/number-formulas.md#present): Returns true if there is a valid input.

---

## Conversions

### `ceil`

Rounds the input number to the next greater integer or float. You can specify the precision of the decimal digits.

#### Syntax

<kbd>number</kbd>.ceil(<span style="color:#FF0000">precision</span>)

- <kbd>number</kbd> - An input integer or float.
- <span style="color:#FF0000">precision</span> - (optional) The number of decimal places to return, you can provide negative values. If not specified, this formula will return the number with no decimal places.

#### Sample usage

| Formula                      | Result  |
| ---------------------------- | ------- |
| <kbd>1234.567</kbd>.ceil     | 1235    |
| <kbd>-1234.567</kbd>.ceil    | -1234   |
| <kbd>1234.567</kbd>.ceil(2)  | 1234.57 |
| <kbd>1234.567</kbd>.ceil(-2) | 1300    |

---

### `floor`

Rounds the input number to the next smaller integer or float. You can specify the precision of the decimal digits.

#### Syntax

<kbd>number</kbd>.floor(<span style="color:#FF0000">precision</span>)

- <kbd>number</kbd> - An input integer or float.
- <span style="color:#FF0000">precision</span> - (optional) The number of decimal places to return, you can provide negative values. If not specified, this formula will return the number with no decimal places.

#### Sample usage

| Formula                       | Result  |
| ----------------------------- | ------- |
| <kbd>1234.567</kbd>.floor     | 1234    |
| <kbd>-1234.567</kbd>.floor    | -1235   |
| <kbd>1234.567</kbd>.floor(2)  | 1234.56 |
| <kbd>1234.567</kbd>.floor(-2) | 1200    |

---

### `to_f`

Converts data to a float (number) datatype.

#### Syntax

<kbd>Input</kbd>.to_f

- <kbd>Input</kbd> - An number input data. You can use a string datatype or a integer datatype.

#### Sample usage

| Formula                   | Result |
| ------------------------- | ------ |
| <kbd>45</kbd>.to_f        | 45.0   |
| <kbd>-45</kbd>.to_f       | -45.0  |
| <kbd>"45.67"</kbd>.to_f   | 45.67  |
| <kbd>"Workato"</kbd>.to_f | 0      |

#### How it works

This formula checks whether the input contains any numbers, if no numbers are found, it returns 0. If the number does not have a decimal point, `.0` will be added the number.

#### See also

- [to_i](/formulas/number-formulas.md#to-i): Convert data to an integer (whole number) datatype.

---

### `to_i`

Converts data to an integer (whole number) datatype.

#### Syntax

<kbd>Input</kbd>.to_i

- <kbd>Input</kbd> - An number input data. You can use a string datatype or a float datatype.

#### Sample usage

| Formula                   | Result |
| ------------------------- | ------ |
| <kbd>45.43</kbd>.to_i     | 45     |
| <kbd>-45.43</kbd>.to_i    | -45    |
| <kbd>"123"</kbd>.to_i     | 123    |
| <kbd>"Workato"</kbd>.to_i | 0      |

#### How it works

This formula checks whether the input contains any numbers, if no numbers are found, it returns 0. If the number has a decimal point, everything after the decimal will be omitted.

::: tip Check for integers
You can use this formula to check if a string contains an integer. If the input does not contain any numbers, the formula will return `0`.
:::

#### See also

- [to_f](/formulas/number-formulas.md#to-f): Converts data to a float (number) datatype.

---

### `to_s`

Converts data to a string (text) datatype.

#### Syntax

<kbd>Input</kbd>.to_s

- <kbd>Input</kbd> - Any input data. You can use number, array, object, or datetime datatypes.

#### Sample usage

| Formula                                                    | Result                             |
| ---------------------------------------------------------- | ---------------------------------- |
| <kbd>-45.67</kbd>.to_s                                     | "-45.67"                           |
| <kbd>"123"</kbd>.to_s                                      | "123"                              |
| <kbd>[1,2,3]</kbd>.to_s                                    | "[1,2,3]"                          |
| <kbd>{key: "Workato"}</kbd>.to_s                           | "{:key=>"Workato"}""               |
| <kbd>"2020-06-05T17:13:27.000000-07:00"</kbd>.to_s         | "2020-06-05T17:13:27.000000-07:00" |
| <kbd>"2020-06-05T17:13:27.000000-07:00"</kbd>.to_s(:short) | "05 Jun 17:13"                     |
| <kbd>"2020-06-05T17:13:27.000000-07:00"</kbd>.to_s(:long)  | "June 05, 2020 17:13"              |

#### How it works

This formula returns a string representation of the input data.

::: tip Quicktip: Output is a string datatype.
A string representation of a list cannot be used in a [**repeat step**](/recipes/steps.md#repeat-step).
:::

#### See also

- [to_f](/formulas/number-formulas.md#to-f): Converts data to a float (number) datatype.
- [to_i](/formulas/number-formulas.md#to-i): Converts data to an integer (whole number) datatype.

---

### `to_currency`

Formats integers/numbers to a currency-style.

#### Syntax

<kbd>Input</kbd>.to_currency

- <kbd>Input</kbd> - Any input string.

#### Sample usage

| Formula                         | Description                      | Result    |
| ------------------------------- | -------------------------------- | --------- |
| <kbd>"345.60"</kbd>.to_currency | Adds default currency symbol "$" | "$345.60" |

#### Advanced sample usage

Learn more about advance usage for the to_currency formula. A comma-separated combination of these may be used to achieve the desired currency format. For example:

```ruby
"12345.678".to_currency(delimiter: ".", format: "%n %u", precision: 2, separator: ",", unit: "€")
```

| Formula           |  Description  |  Result  |
| ------------------| ------------- | -------- |
| <kbd>"345.60"</kbd>.to_currency(unit: "€") | Changes the default currency unit | "€345.60" |
| <kbd>"345.60"</kbd>.to_currency(format: "%n %u") | Changes the position of the number relative to the unit (where the number is represented by `%n` and the currency unit is represented by `%u`). Accepts 0 or 1 spaces in between. Defaults to `"%u%n"`. | "345.60 $" |
| <kbd>"-345.60"</kbd>.to_currency(negative_format: "(%u%n)") | Specifies the format when the number is negative (where the number is represented by `%n` and the currency unit is represented by `%u`). | "($345.60)" |
| <kbd>"345.678"</kbd>.to_currency               | Precision defaults to 2 decimal places | "$345.68"  |
| <kbd>"345.678"</kbd>.to_currency(precision: 3) | Change the precision by specifying the number of decimal places | "$345.678" |
| <kbd>"345.678"</kbd>.to_currency(separator: ",") | Specify the **decimal separator** as ".", "," or " ". Defaults to ".". |  "$345,68" |
| <kbd>"12345.678"</kbd>.to_currency(delimiter: ".") | Specify the **thousands separator** as ",", "." or " ". Defaults to ",".| ""$12.345.68"|

---

### `to_phone`

Converts string or number to a formatted phone number (user-defined).

#### Syntax

<kbd>Input</kbd>.to_phone

- <kbd>Input</kbd> - Any input string or number.

#### Sample usage

| Formula                                  | Result               |
| ---------------------------------------- | -------------------- |
| <kbd>"5551234"</kbd>.to_phone                     | 555-1234             |
| <kbd>1235551234</kbd>.to_phone                    | 123-555-1234         |
| <kbd>1235551234</kbd>.to_phone(area_code: true)   | (123) 555-1234       |
| <kbd>1235551234</kbd>.to_phone(delimiter: " ")    | 123 555 1234         |
| <kbd>1235551234</kbd>.to_phone(area_code: true, extension: 555) | (123) 555-1234 x 555 |
| <kbd>1235551234</kbd>.to_phone(country_code: 1)   | +1-123-555-1234      |
| <kbd>"123a456</kbd>".to_phone                     | 123a456              |
