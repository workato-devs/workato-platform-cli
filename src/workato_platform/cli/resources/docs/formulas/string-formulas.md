---
title: String formulas
date: 2017-03-30 05:00:00 Z
page_nav_depth: 3
---

# String formulas
In Ruby, strings refer to sequences of text and characters. Workato supports a variety of string formulas.

Formulas in Workato are allowlisted Ruby methods. Syntax and functionality for these formulas are generally unchanged. Most formulas return an error and stop the job if the formula operates on nulls (expressed as `nil` in Ruby), except for `present?`, `presence`, and `blank?`.

You can refer to the Ruby documentation on [strings](https://ruby-doc.org/core-2.3.3/String.html) for more information. However, only allowlisted Ruby methods are supported. To request the addition of new formulas to the allowlist, [submit a support ticket](https://support.workato.com/en/support/tickets/new).

The following examples show methods that can be used to manipulate a string in Workato.

---

## Conditionals

This section will cover formulas which allow you to apply conditions (if-else) to your strings. Find out more about how to use conditionals [here](/formulas/conditions.md).

---

### `blank?`

This formula checks the input string and returns true if it is an empty string or if it is null.

#### Syntax

<kbd>Input</kbd>.blank?

- <kbd>Input</kbd> - An input datapill. It can be a string, number, date, or datetime datatype.

#### Sample usage

| Formula                       | Result  |
| ----------------------------- | ------- |
| <kbd>"Any Value"</kbd>.blank? | false   |
| <kbd>123</kbd>.blank?         | false   |
| <kbd>0</kbd>.blank?           | false   |
| <kbd>""</kbd>.blank?          | true    |

#### How it works

If the input is null or an empty string, the formula will return true. For any other data, it returns false.

#### See also

- [presence](/formulas/string-formulas.md#presence): Returns the data if it exists, returns nil if it does not.
- [present?](/formulas/string-formulas.md#present): Returns true if there is a valid input.

---

### `is_not_true?`

Evaluates a boolean value and returns true if the evaluated value is not true.

#### Syntax

<kbd>Input</kbd>.is_not_true?

- <kbd>Input</kbd> - An input boolean, an integer (`1` or `0`), or an accepted string value.

#### Sample usage

| Formula                           | Result |
| --------------------------------- | ------ |
| <kbd>true</kbd>.is_not_true?      | false  |
| <kbd>false</kbd>.is_not_true?     | true   |
| <kbd>0</kbd>.is_not_true?         | true   |
| <kbd>nil</kbd>.is_not_true?       | true   |

#### How it works

Takes in an input and evaluates if it is true or false.

::: tip String values
`"true"`, `"t"`, `"yes"`,`"y"`, and `"1"` are evaluated as a boolean **true**.

`"false"`, `"f"`, `"no"`,`"n"`, and `"0"` are evaluated as a boolean **false**.

However, an empty string (`""`) is not evaluated as a boolean. This formula will display an error if used on a string datatype.
:::

#### See also

- [is_true](/formulas/string-formulas.md#is-true): Evaluates a boolean value and returns true if the evaluated value is true.

---

### `is_true?`

Evaluates a boolean value and returns true if the evaluated value is true.

#### Syntax

<kbd>Input</kbd>.is_true?

- <kbd>Input</kbd> - An input boolean, an integer (`1` or `0`), or an accepted string value.

#### Sample usage

| Formula                       | Result |
| ----------------------------- | ------ |
| <kbd>true</kbd>.is_true?      | true   |
| <kbd>false</kbd>.is_true?     | false  |
| <kbd>0</kbd>.is_true?         | false  |
| <kbd>nil</kbd>.is_true?       | false  |

#### How it works

Takes in an input and evaluates if it is true or false.

::: tip String values
`"true"`, `"t"`, `"yes"`,`"y"`, and `"1"` are evaluated as a boolean **true**.

`"false"`, `"f"`, `"no"`,`"n"`, and `"0"` are evaluated as a boolean **false**.

However, an empty string (`""`) is not evaluated as a boolean. This formula will display an error if used on a string datatype.
:::

#### See also

- [is_not_true](/formulas/string-formulas.md#is-not-true): Evaluates a boolean value and returns true if the evaluated value is not true.

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

- [presence](/formulas/string-formulas.md#presence): Returns the data if it exists, returns nil if it does not.
- [blank?](/formulas/string-formulas.md#blank): Returns nil if the data does not exist or if the string consist of only white spaces.

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

- [blank?](/formulas/string-formulas.md#blank): Returns nil if the data does not exist or if the string consist of only white spaces.
- [present?](/formulas/string-formulas.md#present): Returns true if there is a valid input.

---

### `include?`

Checks if the string contains a specific substring. Returns true if it does.

#### Syntax

<kbd>Input</kbd>.include?(<span style="color:#FF0000">substring</span>)

- <kbd>Input</kbd> - A string input.
- <span style="color:#FF0000">substring</span> - The substring to check for.

#### Sample usage

| Formula                                           | Result |
| ------------------------------------------------- | ------ |
| <kbd>"Partner account"</kbd>.include?("Partner")  | true   |
| <kbd>"Partner account"</kbd>.include?("partner")  | false  |

#### How it works

This formula checks if the string contains a specific substring. The formula returns true if the string includes the substring and false if does not. The substring is case sensitive.

This formula acts in the opposite manner from [exclude?](/formulas/string-formulas.md#exclude). The formula returns true only if the input string contains the stated keyword.

#### See also

- [exclude?](/formulas/string-formulas.md#exclude): Checks if the string contains a specific substring. Returns false if it does.

---

### `exclude?`

Checks if the string contains a specific substring. Returns false if it does.

#### Syntax

<kbd>Input</kbd>.exclude?(<span style="color:#FF0000">substring</span>)

- <kbd>Input</kbd> - A string input.
- <span style="color:#FF0000">substring</span> - The substring to check for.

#### Sample usage

| Formula                                           | Result |
| ------------------------------------------------- | ------ |
| <kbd>"Partner account"</kbd>.exclude?("Partner")  | false  |
| <kbd>"Partner account"</kbd>.exclude?("partner")  | true   |

#### How it works

This formula check is the string contains a specific substring. Returns false if it does, otherwise, returns true. This substring is case sensitive.

This function acts in an opposite manner from [include?](/formulas/string-formulas.md#include). It will return true only if the input string does NOT contain the stated keyword.

#### See also

- [include?](/formulas/string-formulas.md#include): Checks if the string contains a specific substring. Returns true if it does.

---

### `match?`

Checks if the string contains a specific regular expression (regex) pattern. Returns true if it does.

#### Syntax

<kbd>Input</kbd>.match?(<span style="color:#FF0000">pattern</span>)

- <kbd>Input</kbd> - A string input.
- <span style="color:#FF0000">pattern</span> - The regex pattern to check for.

#### Sample usage

| Formula                                           | Result |
| ------------------------------------------------- | ------ |
| <kbd>"Jean Marie"</kbd>.match?(/Marie/)           | true   |
| <kbd>"Jean Marie"</kbd>.match?(/ /)               | true   |
| <kbd>"Partner account"</kbd>.match?(/partner/)    | false  |

#### How it works

This formula checks if the string contains a specific regex pattern. Returns true if it does, otherwise, returns false.

#### See also

- [include?](/formulas/string-formulas.md#include): Checks if the string contains a specific substring. Returns true if it does.
- [exclude?](/formulas/string-formulas.md#exclude): Checks if the string contains a specific substring. Returns false if it does.

---

### `ends_with?`

Checks if the string ends with a specific substring. Returns true if it does.

#### Syntax

<kbd>Input</kbd>.ends_with?(<span style="color:#FF0000">substring</span>)

- <kbd>Input</kbd> - A string input.
- <span style="color:#FF0000">substring</span> - The substring to check for.

#### Sample usage

| Formula                                           | Result |
| ------------------------------------------------- | ------ |
| <kbd>"Jean Marie"</kbd>.ends_with?("rie")         | true   |
| <kbd>"Jean Marie"</kbd>.ends_with?("RIE")         | false  |
| <kbd>"Jean Marie"</kbd>.upcase.ends_with?("RIE")  | true   |

#### How it works

This formula check is the string ends with a specific substring. Returns true if it does, otherwise, returns false.

#### See also

- [include?](/formulas/string-formulas.md#include): Checks if the string contains a specific substring. Returns true if it does.
- [exclude?](/formulas/string-formulas.md#exclude): Checks if the string contains a specific substring. Returns false if it does.
- [match?](/formulas/string-formulas.md#match): Checks if the string contains a specific pattern. Returns true if it does.
- [starts_with?](/formulas/string-formulas.md#starts-with): Checks if the string starts with a specific substring. Returns true if it does.

---

### `starts_with?`

Checks if the string starts with a specific substring. Returns true if it does.

#### Syntax

<kbd>Input</kbd>.starts_with?(<span style="color:#FF0000">substring</span>)

- <kbd>Input</kbd> - A string input.
- <span style="color:#FF0000">substring</span> - The substring to check for.

#### Sample usage

| Formula                                              | Result |
| ---------------------------------------------------- | ------ |
| <kbd>"Jean Marie"</kbd>.starts_with?("Jean")         | true   |
| <kbd>"Jean Marie"</kbd>.starts_with?("JEAN")         | false  |
| <kbd>"Jean Marie"</kbd>.upcase.starts_with?("JEAN")  | true   |

#### How it works

This formula check is the string starts with a specific substring. Returns true if it does, otherwise, returns false.

#### See also

- [include?](/formulas/string-formulas.md#include): Checks if the string contains a specific substring. Returns true if it does.
- [exclude?](/formulas/string-formulas.md#exclude): Checks if the string contains a specific substring. Returns false if it does.
- [match?](/formulas/string-formulas.md#match): Checks if the string contains a specific pattern. Returns true if it does.
- [ends_with?](/formulas/string-formulas.md#ends-with): Checks if the string ends with a specific substring. Returns true if it does.

---

## Text manipulation

This section contains formulas which allow you to manipulate text within strings.

---

### `parameterize`

Replaces special characters in a string with standard characters. Used when app does not accept non-standard characters.

#### Syntax

<kbd>Input</kbd>.parameterize

- <kbd>Input</kbd> - An input string.

#### Sample usage

| Formula                       | Result  |
| ----------------------------- | ------- |
| <kbd>"öüâ"</kbd>.parameterize | "oua"   |

#### How it works

This formula searches for all special characters in the string and replaces them with standard characters.

------

### `lstrip`

This formula removes the white space at the beginning of the input string.

#### Syntax

<kbd>String</kbd>.lstrip

- <kbd>String</kbd> - An input string.

#### Sample usage

| Formula                             | Result      |
| ----------------------------------- | ----------- |
| <kbd>"     Test     "</kbd>.lstrip | "Test     " |

#### How it works

This formula removes white spaces from the beginning of a string. If the string doesn't have any white spaces before, the input string will be returned as is.

::: tip SELECTIVELY REMOVE WHITE SPACES
- To remove white spaces from the end of a string, use [rstrip](/formulas/string-formulas.md#rstrip).
- To remove white spaces from the middle of a string, use [gsub](/formulas/string-formulas.md#gsub).<br>
<kbd>"a b c d e"</kbd>.gsub(" " , "") returns `"abcde"`.
:::

#### See also

- [strip](/formulas/string-formulas.md#strip): Removes the white space at the beginning and the end of the input string.
- [rstrip](/formulas/string-formulas.md#rstrip): Removes the white space at the end of the input string.
- [gsub](/formulas/string-formulas.md#gsub): Replace parts of a text string. Returns a new string with the replaced characters.

---

### `rstrip`

This formula removes the white space at the end of the input string.

#### Syntax

<kbd>String</kbd>.rstrip

- <kbd>String</kbd> - An input string.

#### Sample usage

| Formula                             | Result      |
| ----------------------------------- | ----------- |
| <kbd>"     Test     "</kbd>.rstrip | "     Test" |

#### How it works

This formula removes white spaces from the end of a string. If the string doesn't have any white spaces at the end, the input string will be returned as is.

::: tip SELECTIVELY REMOVE WHITE SPACES
- To remove only white spaces from the beginning of a string, use [lstrip](/formulas/string-formulas.md#lstrip).
- To remove white spaces from the middle of the string, use [gsub](/formulas/string-formulas.md#gsub).<br>
<kbd>"a b c d e"</kbd>.gsub(" " , "") returns `"abcde"`.
:::

#### See also

- [strip](/formulas/string-formulas.md#rstrip): Removes the white space at the beginning and the end of the input string.
- [lstrip](/formulas/string-formulas.md#lstrip): Removes the white space at the beginning of the input string.
- [gsub](/formulas/string-formulas.md#gsub): Replace parts of a text string. Returns a new string with the replaced characters.

---

### `scrub`

If the string is an invalid byte sequence, the formula replaces the invalid bytes with a replacement character. If the string is not invalid, the formula returns the original string.

#### Syntax

<kbd>String</kbd>.scrub(<span style="color:#FF0000">replacement string</span>)

- <kbd>String</kbd> - An input string.

#### Sample usage

| Formula                                    | Result       |
| ------------------------------------------ | ------------ |
| <kbd>"abc\u3042\x81"</kbd>.scrub("*")      | "abc\u3042*" |

---

### `strip`

This formula removes the white space at the beginning and end of the input string.

#### Syntax

<kbd>String</kbd>.strip

- <kbd>String</kbd> - An input string.

#### Sample usage

| Formula                                                      | Result                                 |
| ------------------------------------------------------------ | -------------------------------------- |
| <kbd>"Welcome to the future of automation!     "</kbd>.strip | "Welcome to the future of automation!" |
| <kbd>"   This is an example   "</kbd>.strip                  | "This is an example"                   |

#### How it works

This formula removes white spaces from both sides of a string. If the string doesn't have any white spaces on either side, the input string will be returned as is.

::: tip SELECTIVELY REMOVE WHITE SPACES
- To remove only white spaces from one side, use [lstrip](/formulas/string-formulas.md#lstrip) or [rstrip](/formulas/string-formulas.md#rstrip).
- To remove white spaces from the middle of the string, use [gsub](/formulas/string-formulas.md#gsub).<br>
<kbd>"a b c d e"</kbd>.gsub(" " , "") returns `"abcde"`.
:::

#### See also

- [lstrip](/formulas/string-formulas.md#lstrip): Removes the white space at the beginning of the input string.
- [rstrip](/formulas/string-formulas.md#rstrip): Removes the white space at the end of the input string.
- [gsub](/formulas/string-formulas.md#gsub): Replace parts of a text string. Returns a new string with the replaced characters.

---

### `strip_tags`

This formula removes HTML tags embedded in a string.

#### Syntax

<kbd>String</kbd>.strip_tags

- <kbd>String</kbd> - An input string.

#### Sample usage

| Formula                                    | Result       |
| ------------------------------------------ | ------------ |
| <kbd>"\<p>Jean Marie\</p>".</kbd>.strip_tags | "Jean Marie" |

#### How it works

This formula checks for HTML tags within the input string. It removes any HTML tags found and returns the string.

#### See also

- [strip](/formulas/string-formulas.md#rstrip): Removes the white space at the beginning and the end of the input string.

---

### `ljust`

Aligns the string to left and pads it with whitespace or the provided character/string until the string is a specified length.

#### Syntax

<kbd>String</kbd>.ljust(<span style="color:#FF0000">length</span>,<span style="color:#FF0000">character</span>)

- <kbd>String</kbd> - An input string.
- <span style="color:#FF0000">length</span> - The length of the output string.
- <span style="color:#FF0000">character</span> - (optional) The character or string used to pad the input string. If unspecified, the default pad character is a blank space.

#### Sample usage

| Formula                           | Result       |
| --------------------------------- | ------------ |
| <kbd>"test"</kbd>.ljust(5)       | "test "      |
| <kbd>"test"</kbd>.ljust(10, "*") | "test******" |
| <kbd>"test"</kbd>.ljust(9, "12345") | "test12345" |

#### See also

- [rjust](/formulas/string-formulas.md#rjust): Aligns the string to right and pads with whitespace or the provided string until string is specified length.

---

### `rjust`

Aligns the string to left and pads it with whitespace or a provided character/string until string is a specified length.

#### Syntax

<kbd>String</kbd>.rjust(<span style="color:#FF0000">length</span>,<span style="color:#FF0000">character</span>)

- <kbd>String</kbd> - An input string.
- <span style="color:#FF0000">length</span> - The length of the output string.
- <span style="color:#FF0000">character</span> - (optional) The character or string padding the input string. If unspecified, the default pad character is a blank space.

#### Sample usage

| Formula                           | Result       |
| --------------------------------- | ------------ |
| <kbd>"test"</kbd>.rjust(5)       | " test"      |
| <kbd>"test"</kbd>.rjust(10, "*") | "******test" |
| <kbd>"test"</kbd>.rjust(9, "12345") | "12345test" |

#### See also

- [ljust](/formulas/string-formulas.md#ljust): Aligns the string to left and pads it with whitespace or the provided string until string is a specified length.

------

### `reverse`

Inverts a string, reordering the characters in reverse order. Case is preserved.

#### Syntax

<kbd>String</kbd>.reverse

- <kbd>String</kbd> - An input string.

#### Sample usage

| Formula                           | Result         |
| --------------------------------- | -------------- |
| <kbd>"Jean Marie"</kbd>.reverse   | "eiraM naeJ"   |
| <kbd>" jean marie "</kbd>.reverse | " eiram naej " |

---

### `gsub`

Replace parts of a text string. Returns a new string with the replaced characters.

#### Syntax

<kbd>String</kbd>.gsub(<span style="color:#FF0000">find</span>,<span style="color:#FF0000">replace</span>)

- <kbd>String</kbd> - An input string. You can use a datapill or a static string value.
- <span style="color:#FF0000">find</span> - The string or regular expression (regex) to look for. Use a `/pattern/` syntax for regex.
- <span style="color:#FF0000">replace</span> - The replacement string. You can define the replacement using a string or [hash](/formulas/array-list-formulas.md#hashes).

#### Sample usage

| Formula                                                             | Result                             |
| ------------------------------------------------------------------- | ---------------------------------- |
| <kbd>"I have a blue house and a blue car"</kbd>.gsub("blue", "red") | "I have a red house and a red car" |
| <kbd>"Jean Marie"</kbd>.gsub("J", "M")                              | "Mean Marie"                       |
| <kbd>"Jean Marie"</kbd>.gsub(/[Jr]/, 'M')                           | "Mean MaMie"                       |
| <kbd>"Jean Marie"</kbd>.downcase.gsub("j", "M")                     | "Mean marie"                       |

#### Advanced sample usage

Learn more about advanced usage for the `gsub` method from the [Ruby documentation](https://ruby-doc.org/core-2.7.2/String.html#method-i-gsub.)

| Formula                                               | Result    |
| ----------------------------------------------------- | --------- |
| <kbd>"Awesome"</kbd>.gsub(/[Ae]/, 'A'=>'E', 'e'=>'a') | "Ewasoma" |
| <kbd>"Anna's Cafe"</kbd>.gsub("'", "\\\\'")           | "Annas Cafes Cafe"<br>This replaces the quotation symbol with text after the breakpoint. |
| <kbd>"Anna's Cafe"</kbd>.gsub("'", {"'"=>"\\\\'"})    | "Anna\\\\'s Cafe"<br>This replace the quotation symbol with a replacement string.|

#### How it works

This formula is similar to find and replace. It takes two input parameters:

- **First input**: The string that you plan to replace. The input is case-sensitive, so make sure to input uppercase or lowercase correctly to find all occurrences that are an exact match.
- **Second input**: The new string that replaces all occurrences of the first input.

#### See also

- [sub](/formulas/string-formulas.md#sub): Replaces the first occurrence of a search term.

---

### `sub`

Replaces the first occurrence of the first input value, with the second input value, within the string. This formula is case-sensitive - make sure to type in uppercase or lowercase before comparison if you are concerned about case sensitivity.

#### Syntax

<kbd>String</kbd>.sub(<span style="color:#FF0000">find</span>,<span style="color:#FF0000">replace</span>)

- <kbd>String</kbd> - An input string. You can use a datapill or a static string value.
- <span style="color:#FF0000">find</span> - The string or regular expression (regex) to look for. Use a `/pattern/` syntax for regex.
- <span style="color:#FF0000">replace</span> - The replacement string. You can define the replacement using a string or [hash](/formulas/array-list-formulas.md#hashes).

#### Sample usage
| Formula                                      | Result       |
| -------------------------------------------- | ------------ |
| <kbd>"Mean Marie"</kbd>.sub(/M/, "J")        | "Jean Marie" |
| <kbd>"Hello"</kbd>.sub(/[aeiou]/, "*")       | "H*llo"      |

---

### `length`

Returns the number of characters within an input string, including whitespaces.

#### Syntax

<kbd>String</kbd>.length

- <kbd>String</kbd> - An input string.

#### Sample usage

| Formula                          | Result |
| -------------------------------- | ------ |
| <kbd>"Jean Marie"</kbd>.length   | 10     |
| <kbd>" jean marie "</kbd>.length | 12     |

---

### `slice`

Returns a partial segment of a string.

#### Syntax

<kbd>String</kbd>.slice(<span style="color:#FF0000">start</span>,<span style="color:#FF0000">end</span>)

- <kbd>String</kbd> - An input string.
- <span style="color:#FF0000">start</span> - The index of the string to start returning a partial segment at. Strings are zero-indexed.
- <span style="color:#FF0000">end</span> - (optional) The number of characters to return. If unspecified, the formula will return only one character.

#### Sample usage

| Formula                             | Result  |
| ----------------------------------- | ------- |
| <kbd>"Jean Marie"</kbd>.slice(0,3)  | "Jea"   |
| <kbd>"Jean Marie"</kbd>.slice(5)    | "M"     |
| <kbd>"Jean Marie"</kbd>.slice(3,3)  | "n M"   |
| <kbd>"Jean Marie"</kbd>.slice(-5,5) | "Marie" |

#### How it works

The formula returns a partial segment of a string. It takes in two parameters - the first parameter is the index that decides which part of the string to start returning from. The first letter of a string corresponds to an index of 0. Negative numbers start from the last character, so an index of -1 is the last character in the string. The second parameter decides how many characters to return. If you only pass in the first parameter, one character is returned.

---

### `scan`

Scan the string for the regex pattern to retrieve and returns an array.

#### Syntax

<kbd>String</kbd>.scan(<span style="color:#FF0000">pattern</span>)

- <kbd>String</kbd> - An input string.
- <span style="color:#FF0000">regex pattern</span> - The regex pattern to search for.

#### Sample usage

| Formula                                             | Result             |
| --------------------------------------------------- | ------------------ |
| <kbd>"Thu, 01/23/2014"</kbd>.scan(/\d+/)            | ["01","23","2014"] |
| <kbd>"Thu, 01/23/2014"</kbd>.scan(/\d+/).join("-")  | "01-23-2014"       |

---

### `encode`

Returns the string encoded.

#### Syntax

<kbd>String</kbd>.encode(<span style="color:#FF0000">encoding</span>)

- <kbd>String</kbd> - An input string.
- <span style="color:#FF0000">encoding</span> - Name of the encoding (for example, Windows-1252). Learn more about ruby encodings [here](https://en.wikibooks.org/wiki/Ruby_Programming/Encoding).

#### Sample usage

| Formula                   | Result  |
| ------------------------- | ------- |
| `"Jean Marie"`.encode("Windows-1252") | "Jean Marie"   |
| `"Olé!"`.encode("UTF-8") | `"Olé!"`   |
| `"Olé"`.encode("ASCII") | "Error calculating input: U+00E9 from UTF-8 to US-ASCII"  |


---

### `transliterate`

Replaces non-ASCII characters with an ASCII approximation. If no approximation exists, it uses a replacement character which defaults to '?'.

#### Syntax

<kbd>String</kbd>.transliterate

- <kbd>String</kbd> - An input string.

#### Sample usage

| Formula                   | Result  |
| ------------------------- | ------- |
| <kbd>"Chloé"</kbd>.transliterate     | "Chloe"   |

- [parameterize](/formulas/string-formulas.md#parameterize): Replaces special characters in a string.

---

## Text case manipulation

This section covers formulas which allow you to change the case of certain parts of a word.

------

### `capitalize`

Converts the input string into sentence case, where the first character of the string is capitalized and all other characters are lowercase.

#### Syntax

<kbd>String</kbd>.capitalize

- <kbd>String</kbd> - An input string.

#### Sample usage

| Formula                                | Result                    |
| -------------------------------------- | ------------------------- |
| <kbd>"ticket opened. Gold SLA"</kbd>.capitalize | "Ticket opened. gold sla" |
| <kbd>"jean MARIE"</kbd>.capitalize              | "Jean marie"              |

------

### `titleize`

Converts the input string into title case, where the first character of each word is capitalized and all other characters are lowercase.

#### Syntax

<kbd>String</kbd>.titleize

- <kbd>String</kbd> - An input string.

#### Sample usage

| Formula                              | Result                    |
| ------------------------------------ | ------------------------- |
| <kbd>"ticket opened. Gold SLA"</kbd>.titleize | "Ticket Opened. Gold Sla" |
| <kbd>"jean MARIE"</kbd>.titleize              | "Jean Marie"              |

---

### `upcase`

Convert text to uppercase.

#### Syntax

<kbd>String</kbd>.upcase

- <kbd>String</kbd> - An input string.

#### Sample usage

| Formula                                        | Result                       |
| ---------------------------------------------- | ---------------------------- |
| <kbd>"Automation at its FINEST!"</kbd>.upcase | "AUTOMATION AT ITS FINEST!" |
| <kbd>"Convert to UPCASE"</kbd>.upcase          | "CONVERT TO UPCASE"          |

#### How it works

This formula searches for any lowercase character and replace it with the uppercase characters.

::: tip USE UPCASE TO IMPROVE STRING SEARCHES
Search formulas like ([gsub](/formulas/string-formulas.md#gsub) or [sub](/formulas/string-formulas.md#sub)) use case sensitive characters. Use the `upcase` formula to ensure that all characters are in the same case before searching.
:::

#### See also

- [downcase](/formulas/string-formulas.md#downcase): Convert text to lowercase.
- [capitalize](/formulas/string-formulas.md#capitalize): Convert text to sentence case.
- [titleize](/formulas/string-formulas.md#titleize): Convert text to title case.

---

### `downcase`

Convert text to lowercase.
::: details Video tutorial: Downcase formula use case
<Video src="https://www.youtube.com/embed/HXBe9PVwH0M"/>
:::

#### Syntax

<kbd>String</kbd>.downcase

- <kbd>String</kbd> - An input string.

#### Sample usage

| Formula                                          | Result                      |
| ------------------------------------------------ | --------------------------- |
| <kbd>"Automation at its FINEST!"</kbd>.downcase | "automation at its finest!" |
| <kbd>"Convert to DOWNCASE"</kbd>.downcase        | "convert to downcase"       |

#### How it works

This formula searches for any uppercase character and replace it with the lowercase characters.

::: tip USE DOWNCASE TO IMPROVE STRING SEARCHES
Search formulas like ([gsub](/formulas/string-formulas.md#gsub) or [sub](/formulas/string-formulas.md#sub)) use case sensitive characters. Use the `downcase` formula to ensure that all characters are in the same case before searching.
:::

#### See also

- [upcase](/formulas/string-formulas.md#upcase): Convert text to uppercase.
- [capitalize](/formulas/string-formulas.md#capitalize): Convert text to sentencecase.
- [titleize](/formulas/string-formulas.md#titleize): Convert text to titlecase.

---

### `quote`

Quotes a string, escaping any ' (single quote) characters

#### Syntax

<kbd>String</kbd>.quote

- <kbd>String</kbd> - An input string.

#### Sample usage

| Formula                              | Result                    |
| ------------------------------------ | ------------------------- |
| <kbd>"Paula's Baked Goods"</kbd>.quote        | "Paula\'s Baked Goods"    |

---

## Converting to arrays and back

This section shows how you can manipulate strings into arrays.

---

### `split`

This formula divides a string around a specified character and returns an array of strings.
::: details Watch a step-by-step video tutorial instead
<Video src="https://www.youtube.com/embed/trpODHgNzCY"/>
:::

#### Syntax

<kbd>String</kbd>.split(<span style="color:#FF0000">char</span>)

- <kbd>String</kbd> - An input string value. You can use a datapill or a static value.
- <span style="color:#FF0000">char</span> - (optional) The character to split the text at. This is case sensitive. If no character is defined, then by default, strings are split by white spaces.

#### Sample usage

| Formula                               | Result                  |
| ------------------------------------- | ----------------------- |
| <kbd>"Ms-Jean-Marie"</kbd>.split("-") | ["Ms", "Jean", "Marie"] |
| <kbd>"Ms Jean Marie"</kbd>.split      | ["Ms", "Jean", "Marie"] |
| <kbd>"Split string"</kbd>.split()     | ["Split", "string"]     |
| <kbd>"Split string"</kbd>.split("t")  | ["Split", " s", "ring"]  |
| <kbd>"01/23/2014"</kbd>.split("/")    | ["01", "23", "2014"]    |
| <kbd>"01/23/2014"</kbd>.split("/").join("-") | "01-23-2014"     |

#### How it works

This formula looks for the specified character in the input string. Every time it is found, the input will be split into a new string.

::: tip Split characters
You can use a string of characters together as the split argument (for example, `"and"`).

<kbd>"You and Me"</kbd>.split(`"and"`) returns `["You","Me"]`.
:::

#### See also

- [strip](/formulas/string-formulas.md#strip): Removes white space around the input string.
- [slice](/formulas/string-formulas.md#slice): Returns a partial segment of a string.
- [match](/formulas/string-formulas.md#match): Checks the input string for a particular pattern.
- [join](/formulas/array-list-formulas.md#join): Combines list items into a string.

---

### `bytes`

Returns an array of bytes for a given string.

#### Syntax

<kbd>String</kbd>.bytes

- <kbd>String</kbd> - An input string.

#### Sample usage

| Formula                    | Result            |
| -------------------------- | ----------------- |
| <kbd>"Hello"</kbd>.bytes   | ["72", "101", "108", "108", "111"] |

---

### `bytesize`

Returns the length of a given string in bytes.

#### Syntax

<kbd>Input</kbd>.bytesize

- <kbd>Input</kbd> - Any input string.

#### Sample usage

| Formula                                  | Result               |
| ---------------------------------------- | -------------------- |
| <kbd>"Hello"</kbd>.bytesize              | 5           |

---

### `byteslice`

Returns a substring of specified bytes instead of length. In some cases, non ASCII characters such as Japanese or Chinese may use multiple bytes.

#### Syntax

<kbd>Input</kbd>.byteslice(0,4)

- <kbd>Input</kbd> - Any input string.

#### Sample usage

| Formula                                  | Result               |
| ---------------------------------------- | -------------------- |
| <kbd>"hello"</kbd>.byteslice(1)           | e                    |
| <kbd>"hello"</kbd>.byteslice(-1)          | o                    |
| <kbd>"hello"</kbd>.byteslice(1,2)         | el                   |
| <kbd>"abc漢字"</kbd>.byteslice(0,4)        | abc漢                |

---

## Conversion of other data types to strings {: #conversions :}

---

### `to_s`

Converts non-string data types such as numbers or dates to a string (text) datatype.

::: details Video tutorial: to_s formula use case
<Video src="https://www.youtube.com/embed/nOkGS8fYv5g"/>
:::

#### Syntax

<kbd>Input</kbd>.to_s

- <kbd>Input</kbd> - Any input data. You can use number, array, object, or datetime datatypes.

#### Sample usage

| Formula                                                    | Result                             |
| ---------------------------------------------------------- | ---------------------------------- |
| <kbd>-45.67</kbd>.to_s                                     | "-45.67"                           |
| <kbd>"123"</kbd>.to_s                                      | "123"                              |
| <kbd>[1, 2, 3]</kbd>.to_s                                  | "[1, 2, 3]"                        |
| <kbd>{key: "Workato"}</kbd>.to_s                           | "{:key=>"Workato"}"                |
| <kbd>"2020-06-05T17:13:27.000000-07:00"</kbd>.to_s         | "2020-06-05T17:13:27.000000-07:00" |
| <kbd>"2020-06-05T17:13:27.000000-07:00"</kbd>.to_s(:short) | "05 Jun 17:13"                     |
| <kbd>"2020-06-05T17:13:27.000000-07:00"</kbd>.to_s(:long)  | "June 05, 2020 17:13"              |

#### How it works

This formula returns a string representation of the input data.

::: tip OUTPUT IS A STRING DATATYPE
A string representation of a list cannot be used in a [**repeat step**](/recipes/steps.md#repeat-step).
:::

#### See also

- [to_f](/formulas/string-formulas.md#to-f): Converts data to a float (number) datatype.
- [to_i](/formulas/string-formulas.md#to-i): Converts data to an integer (whole number) datatype.

---

### `ordinalize`

Turns a number into an ordinal string used to denote the position in an ordered sequence, such as 1st, 2nd, 3rd, 4th.

#### Syntax

<kbd>Input</kbd>.ordinalize

- <kbd>Input</kbd> - Any input number.

#### Sample usage

| Formula                    | Result               |
| -------------------------- | -------------------- |
| <kbd>1</kbd>.ordinalize    | "1st"                |
| <kbd>2</kbd>.ordinalize    | "2nd"                |
| <kbd>3</kbd>.ordinalize    | "3rd"                |
| <kbd>1003</kbd>.ordinalize | "1003rd"             |
| <kbd>-3</kbd>.ordinalize   | "-3rd"               |

---

## Conversion of strings to other data types

---

### `to_f`

Converts data to a float (number) datatype.

#### Syntax

<kbd>Input</kbd>.to_f

- <kbd>Input</kbd> - Numerical input data. You can use a string datatype or a integer datatype.

#### Sample usage

| Formula                   | Result |
| ------------------------- | ------ |
| <kbd>45</kbd>.to_f        | 45.0   |
| <kbd>-45</kbd>.to_f       | -45.0  |
| <kbd>"45.67"</kbd>.to_f   | 45.67  |
| <kbd>"Workato"</kbd>.to_f | 0      |

#### How it works

This formula checks if the input contains any numbers. If no numbers are found, it returns 0. If the number does not have a decimal point, `.0` is added to the number.

#### See also

- [to_i](/formulas/string-formulas.md#to-i): Convert data to an integer (whole number) datatype.

---

### `to_i`

Converts data to an integer (whole number) datatype.

#### Syntax

<kbd>Input</kbd>.to_i

- <kbd>Input</kbd> - Numerical input data. You can use a string datatype or a float datatype.

#### Sample usage

| Formula                   | Result |
| ------------------------- | ------ |
| <kbd>45.43</kbd>.to_i     | 45     |
| <kbd>-45.43</kbd>.to_i    | -45    |
| <kbd>"123"</kbd>.to_i     | 123    |
| <kbd>"Workato"</kbd>.to_i | 0      |

#### How it works

This formula checks if the input contains any numbers. If no numbers are found, it returns 0. If the number has a decimal point, everything after the decimal is omitted.

::: tip CHECK FOR INTEGERS
You can use this formula to check if a string contains an integer. If the input does not contain any numbers, the formula returns `0`.
:::

#### See also

- [to_f](/formulas/string-formulas.md#to-f): Converts data to a float (number) datatype.

---

### `to_country_alpha2`

Convert an alpha-3 country code or country name to an alpha-2 country code (first 2 initials).

#### Syntax

<kbd>Input</kbd>.to_country_alpha2

- <kbd>Input</kbd> - Any input string.

#### Sample usage

| Formula                            | Result |
| ---------------------------------- | ------ |
| <kbd>"GBR"</kbd>.to_country_alpha2            | "GB"     |
| <kbd>"United Kingdom"</kbd>.to_country_alpha2 | "GB"     |

---

### `to_country_alpha3`

Convert alpha-2 country code or country name to an alpha-3 country code (first 3 initials).

#### Syntax

<kbd>Input</kbd>.to_country_alpha3

- <kbd>Input</kbd> - Any input string.

#### Sample usage

| Formula                            | Result |
| ---------------------------------- | ------ |
| <kbd>"GB"</kbd>.to_country_alpha3            | "GBR"     |
| <kbd>"United Kingdom"</kbd>.to_country_alpha3 | "GBR"     |

---

### to_country_name

Convert alpha-2, alpha-3 country code, or country name to ISO3166 country name.

#### Syntax

<kbd>Input</kbd>.to_country_name

- <kbd>Input</kbd> - Any input string.

#### Sample usage

| Formula               | Result         |
| --------------------- | -------------- |
| <kbd>"GBR"</kbd>.to_country_name | "United Kingdom" |
| <kbd>"GB"</kbd>.to_country_name  | "United Kingdom" |

---

### `to_currency`

Formats integers or numbers to a currency-style, adding a default currency symbol at the start of the string.

#### Syntax

<kbd>Input</kbd>.to_currency

- <kbd>Input</kbd> - Any input string.

#### Sample usage

| Formula                         | Description                      | Result    |
| ------------------------------- | -------------------------------- | --------- |
| <kbd>"345.60"</kbd>.to_currency | Adds default currency symbol "$" | "$345.60" |

#### Advanced sample usage

Learn more about advanced use of the to_currency formula. A comma-separated combination of these may be used to achieve the desired currency format. For example:

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
| <kbd>"12345.678"</kbd>.to_currency(delimiter: ".") | Specify the **thousands separator** as ",", "." or " ". Defaults to ",".| "$12.345.68"|

---

### `to_currency_code`

Convert alpha-2, alpha-3 country code, or country name to ISO4217 currency code

#### Syntax

<kbd>Input</kbd>.to_currency_code

- <kbd>Input</kbd> - Any input string.

#### Sample usage

| Formula                | Result |
| ---------------------- | ------ |
| <kbd>"GBR"</kbd>.to_currency_code | "GBP"    |
| <kbd>"US"</kbd>.to_currency_code  | "USD"    |

---

### `to_currency_name`

Convert alpha-3 currency code or alpha-2/3 country code or country name to ISO4217 currency name.

#### Syntax

<kbd>Input</kbd>.to_currency_name

- <kbd>Input</kbd> - Any input string.

#### Sample usage

| Formula                | Result  |
| ---------------------- | ------- |
| <kbd>"GBR"</kbd>.to_currency_code | "Pound"   |
| <kbd>"USD"</kbd>.to_currency_code | "Dollars" |

---

### `to_currency_symbol`

Convert alpha-3 currency code or alpha-2/3 country code or country name to ISO4217 currency symbol.

#### Syntax

<kbd>Input</kbd>.to_currency_symbol

- <kbd>Input</kbd> - Any input string.

#### Sample usage

| Formula                | Result |
| ---------------------- | ------ |
| <kbd>"GBR"</kbd>.to_currency_symbol | "£"      |
| <kbd>"USD"</kbd>.to_currency_symbol | "$"      |

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

---

### `to_state_code`

Convert state name to code.

#### Syntax

<kbd>Input</kbd>.to_state_code

- <kbd>Input</kbd> - Any input string.

#### Sample usage

| Formula                                  | Result               |
| ---------------------------------------- | -------------------- |
| <kbd>"California"</kbd>.to_state_code    | CA                   |

---

### `to_state_name`

Convert state code to name.

#### Syntax

<kbd>Input</kbd>.to_state_name

- <kbd>Input</kbd> - Any input string.

#### Sample usage

| Formula                                  | Result               |
| ---------------------------------------- | -------------------- |
| <kbd>"CA"</kbd>.to_state_name            | CALIFORNIA           |

---
