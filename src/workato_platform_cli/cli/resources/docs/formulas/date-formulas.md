---
title: Date formulas
date: 2017-03-30 05:00:00 Z
---

# Date formulas

::: details Video guide: Learn how to transform dates with formula mode
<Video src="https://www.youtube.com/embed/Saq5ybJauVM"/>
:::

Workato supports a variety of date and datetime formulas.

Formulas in Workato are allowlisted Ruby methods. Syntax and functionality for these formulas are generally unchanged. Most formulas return an error and stop the job if the formula operates on nulls (expressed as `nil` in Ruby), except for `present?`, `presence`, and `blank?`.

You can refer to the Ruby documentation on [time](http://ruby-doc.org/core-2.3.3/Time.html) for more information. However, only allowlisted Ruby methods are supported. To request the addition of new formulas to the allowlist, [submit a support ticket](https://support.workato.com/en/support/tickets/new).

## Date arithmetic

Use the following keywords to perform arithmetic with date and datetime data:

- `seconds`
- `minutes`
- `days`
- `months`
- `years`

When combined with a formula, you can perform addition and subtraction.

### Sample usage

| Date Arithmetic                            | Output       |
| ------------------------------------------ | ------------ |
| <kbd>"2020-01-01"</kbd>.to_date + 2.days   | "2020-01-03" |
| <kbd>"2020-01-01"</kbd>.to_date - 2.days   | "2019-12-30" |
| <kbd>"2020-01-01"</kbd>.to_date + 2.months | "2020-03-01" |
| <kbd>"2020-01-01"</kbd>.to_date - 2.months | "2019-11-01" |
| <kbd>"2020-01-01"</kbd>.to_date + 2.years  | "2022-01-01" |
| <kbd>"2020-01-01"</kbd>.to_date - 2.years  | "2018-01-01" |

---

## `now`

Returns the time and date at runtime in US Pacific Time Zone (PST).

### Sample usage

| Formula       | Result                             |
| ------------- | ---------------------------------- |
| now           | "2022-02-01T07:00:00.000000-08:00" |
| now + 8.hours | "2022-02-01T15:00:00.000000-08:00" |
| now + 2.days  | "2022-02-03T07:00:00.000000-08:00" |

### How it works

The formula calculates the timestamp when the job is processed. Each step using this formula returns the timestamp at which the step runs.

::: tip Output datapill
If you only want the date without the time, try using the <u>[today](/formulas/date-formulas.md#today)</u> formula instead.
:::

### See also

- [today](/formulas/date-formulas.md#today): Returns the date at runtime.
- [in_time_zone](/formulas/date-formulas.md#in-time-zone): Converts a time value to a different time zone.

---

## `today`

Returns the date at runtime in US Pacific Time Zone.

### Sample usage

| Formula        | Result                      			|
| --------------- | ----------------------------------- |
| today           | "2022-02-01" 						|
| today + 8.hours | "2022-02-01T15:00:00.000000-08:00" 	|
| today + 2.days  | "2022-02-03"                		|

### How it works

The formula calculates the timestamp when the job is processed. Each step using this formula returns the date at which the step runs.

::: tip Output datapill
If you want the date and time, try using the <u>[now](/formulas/date-formulas.md#now)</u> formula instead.
:::

### See also

- [now](/formulas/date-formulas.md#now): Returns the time and date at runtime.
- [in_time_zone](/formulas/date-formulas.md#in-time-zone): Converts a time value to a different time zone.

---

## `from_now`

Returns a future timestamp by a specified time duration. The timestamp is calculated at runtime.

### Syntax

<kbd>Unit</kbd>.from_now

- <kbd>Unit</kbd> - A time value to offset.

### Sample usage

| Formula       				 | Result                    		   |
| ------------------------------ | ----------------------------------- |
| <kbd>30.seconds</kbd>.from_now | "2022-02-01T07:00:30.000000-08:00"  |
| <kbd>2.months</kbd>.from_now   | "2022-04-01T07:00:00.000000-08:00"  |
| <kbd>3.days</kbd>.from_now     | "2022-02-04T07:00:00.000000-08:00"  |

### How it works

The formula calculates the current timestamp and offsets by a specified time duration. This timestamp is calculated when the job is processed. Each step using this formula returns a timestamp.

::: tip UNITS
You can use any of the following units: `seconds`, `minutes`, `hours`, `days`, `months`, or `years`.
:::

### See also

- [ago](/formulas/date-formulas.md#ago): Returns an earlier timestamp by a specified time duration.
- [now](/formulas/date-formulas.md#now): Returns the time and date at runtime.
- [today](/formulas/date-formulas.md#today): Returns the date at runtime.

---

## `ago`

Returns an earlier timestamp by a specified time duration. The timestamp is calculated at runtime.

### Syntax

<kbd>Unit</kbd>.ago

- <kbd>Unit</kbd> - A time value to offset.

### Sample usage

| Formula        | Result                      |
| --------------- | --------------------------- |
| <kbd>2.months</kbd>.ago   | "2020-10-04 14:45:29 -0700"  |
| <kbd>3.days</kbd>.ago     | "2020-12-01 14:45:29 -0700"  |
| <kbd>30.seconds</kbd>.ago | "2020-12-04 14:15:29 -0700"  |

### How it works

The formula calculates the current timestamp and offsets by a specified time duration. This timestamp is calculated when the job is processed. Each step using this formula returns a timestamp for each step that runs.

::: tip Units
You can use any of the following units: `seconds`, `minutes`, `hours`, `days`, `months`, or `years`.
:::

### See also

- [from_now](/formulas/date-formulas.md#from-now): Returns a future timestamp by a specified time duration.
- [now](/formulas/date-formulas.md#now): Returns the time and date at runtime.
- [today](/formulas/date-formulas.md#today): Returns the date at runtime.

---

## `wday`

Returns day of the week. Sunday returns 0, Monday returns 1.

### Syntax

<kbd>Date</kbd>.wday

- <kbd>Date</kbd> - A date or datetime datatype.

### Sample usage

| Example                                                  | Result |
| -------------------------------------------------------- | ------ |
| today.wday                                               | 4      |
| <kbd>"01/12/2020"</kbd>.to_date(format:"DD/MM/YYYY").wday | 2      |

### How it works

The formula calculates the current day when the job is processed. The day of the week is converted into an integer output. Sunday = 0, Monday = 1.

::: tip Quicktip: Convert to date datatype
This formula only works with date or datetime datatype. Use [to_date](/formulas/date-formulas.md#to-date) to convert a string into a date datatype.
:::

### See also

- [yday](/formulas/date-formulas.md#yday): Returns the day number of the year.
- [yweek](/formulas/date-formulas.md#yweek): Returns the week number of the year.

---

## `yday`

Returns day number of the year.

### Syntax

<kbd>Date</kbd>.yday

- <kbd>Date</kbd> - A date or datetime datatype.

### Sample usage

| Example                                                   | Result |
| --------------------------------------------------------- | ------ |
| today.yday                                                | 338    |
| <kbd>"2020-01-01"</kbd>.to_date(format:"YYYY-MM-DD").yday | 1      |
| <kbd>"2020-02-01"</kbd>.to_date(format:"YYYY-MM-DD").yday | 32     |

### How it works

The formula calculates the current day when the job is processed. The day of the year is converted to an integer output.

::: tip Quicktip: Convert to date datatype
This formula only works with date or datetime datatype. Use [to_date](/formulas/date-formulas.md#to-date) to convert a string into a date datatype.
:::

### See also

- [wday](/formulas/date-formulas.md#wday): Returns the day number of the week.
- [yweek](/formulas/date-formulas.md#yweek): Returns the week number of the year.

---

## `yweek`

Returns week number of the year.

### Syntax

<kbd>Date</kbd>.yweek

- <kbd>Date</kbd> - A date or datetime datatype.

### Sample usage

| Example                                                    | Result |
| ---------------------------------------------------------- | ------ |
| today.yweek                                                | 49     |
| <kbd>"2020-01-01"</kbd>.to_date(format:"YYYY-MM-DD").yweek | 1      |
| <kbd>"2020-02-01"</kbd>.to_date(format:"YYYY-MM-DD").yweek | 5      |

### How it works

The formula calculates the current day when the job is processed. The week of the year is converted to an integer output.

::: tip Quicktip: Convert to date datatype
This formula only works with date or datetime datatype. Use [to_date](/formulas/date-formulas.md#to-date) to convert a string into a date datatype.
:::

### See also

- [wday](/formulas/date-formulas.md#wday): Returns the day number of the week.
- [yday](/formulas/date-formulas.md#yday): Returns the day number of the year.

---

## `beginning_of_hour`

Returns datetime for top-of-the-hour for a given datetime.

### Syntax

<kbd>Datetime</kbd>.beginning_of_hour

- <kbd>Datetime</kbd> - An input datetime.

### Sample usage

| Formula                                                         | Result                             |
| --------------------------------------------------------------- | ---------------------------------- |
| today.to_time.beginning_of_hour                                 | "2020-12-02T16:00:00.000000-07:00" |
| <kbd>"2020-06-01T01:30:45.000000+00:00"</kbd>.to_time.beginning_of_hour | "2020-06-01T01:00:00.000000+00:00" |
| <kbd>"2020-06-01"</kbd>.to_time.beginning_of_hour               | "2020-06-01T00:00:00.000000+00:00" |

---

## `beginning_of_day`

Returns datetime for midnight on date of a given date/datetime.

### Syntax

<kbd>Date</kbd>.beginning_of_day

- <kbd>Date</kbd> - An input date or datetime.

### Sample usage

| Formula                                                        | Result                             |
| -------------------------------------------------------------- | ---------------------------------- |
| today.beginning_of_day                                         | "2020-12-02T00:00:00.000000-07:00" |
| <kbd>"2020-06-01"</kbd>.to_date.beginning_of_day               | "2020-06-01T00:00:00.000000+00:00" |
| <kbd>"2020-06-01T01:30:45.000000+00:00"</kbd>.beginning_of_day | "2020-06-01T00:00:00.000000+00:00" |

---

## `beginning_of_week`

Returns date for the start of the week (Monday) for a given date/timestamp.

### Syntax

<kbd>Date</kbd>.beginning_of_week

- <kbd>Date</kbd> - An input date or datetime.

### Sample usage

| Formula                                                         | Result                             |
| --------------------------------------------------------------- | ---------------------------------- |
| today.beginning_of_week                                         | "2020-11-30T00:00:00.000000+00:00" |
| <kbd>"2020-06-01"</kbd>.to_date.beginning_of_week               | "2020-06-01T00:00:00.000000+00:00" |
| <kbd>"2020-06-01T01:30:45.000000+00:00"</kbd>.beginning_of_week | "2020-06-01T00:00:00.000000+00:00" |

---

## `beginning_of_month`

Returns first day of the month for a given date/datetime.

### Syntax

<kbd>Date</kbd>.beginning_of_month

- <kbd>Date</kbd> - An input date or datetime.

### Sample usage

| Formula                                                          | Result                             |
| ---------------------------------------------------------------- | ---------------------------------- |
| today.beginning_of_month                                         | "2020-12-01T00:00:00.000000+00:00" |
| <kbd>"2020-06-01"</kbd>.to_date.beginning_of_month               | "2020-06-01T00:00:00.000000+00:00" |
| <kbd>"2020-06-01T01:30:45.000000+00:00"</kbd>.beginning_of_month | "2020-06-01T00:00:00.000000+00:00" |

---

## `beginning_of_year`

Returns first day of the year for a given date/datetime.

### Syntax

<kbd>Date</kbd>.beginning_of_year

- <kbd>Date</kbd> - An input date or datetime.

### Sample usage

| Formula                                                         | Result                             |
| --------------------------------------------------------------- | ---------------------------------- |
| today.beginning_of_year                                         | "2020-01-01T00:00:00.000000+00:00" |
| <kbd>"2020-06-01"</kbd>.to_date.beginning_of_year               | "2020-01-01T00:00:00.000000+00:00" |
| <kbd>"2020-06-01T01:30:45.000000+00:00"</kbd>.beginning_of_year | "2020-01-01T00:00:00.000000+00:00" |

---

## `end_of_month`

Returns last day of the month for a given date/datetime. This formula will return a date or datetime based on the input data.

### Syntax

<kbd>Date</kbd>.end_of_month

- <kbd>Date</kbd> - An input date or datetime.

### Sample usage

| Formula                                                          | Result                             |
| ---------------------------------------------------------------- | ---------------------------------- |
| today.end_of_month                                         | "2020-12-31"                       |
| <kbd>"2020-06-01"</kbd>.to_date.end_of_month               | "2020-06-30"                       |
| <kbd>"2020-06-01T01:30:45.000000+00:00"</kbd>.to_time.end_of_month | "2020-06-30T23:59:59.999999+00:00" |

---

## `strftime`

Returns a datetime input as a user-defined string.

### Syntax

<kbd>Date</kbd>.strftime(<span style="color:#FF0000">format</span>)

- <kbd>Date</kbd> - An input date or datetime.
- <span style="color:#FF0000">format</span> - The format of the user-defined datetime written as a string.

### Sample usage

| Formula                                                                      | Result                      |
| ----------------------------------------------------------------------------- | --------------------------- |
| <kbd>"2020-06-05T17:13:27.000000-07:00"</kbd>.to_date.strftime("%Y/%m/%d")            | "2020/06/05"                |
| <kbd>"2020-06-05T17:13:27.000000-07:00"</kbd>.strftime("%Y-%m-%dT%H:%M:%S%z") | "2020-06-05T17:13:27-0700"  |
| <kbd>"2020-06-05T17:13:27.000000-07:00"</kbd>.strftime("%B %e, %l:%M%p")      | "June 5, 5:13 pm"            |
| <kbd>"2020-06-05T17:13:27.000000-07:00"</kbd>.strftime("%A, %d %B %Y %k:%M")  | "Friday, 05 June 2020 0:00" |

### Parameters

As previously shown, each code (`%B`, `%e`, `%I`, for example) refers to a specific element of `datetime`. You can also add static text and punctuation, such as commas (`,`), slashes (`/`), and colons (`:`). Refer to the following list of frequently used codes:

| Code             | Meaning                                | Example<br>(2020-06-05T17:13:27.000000-07:00) |
| ---------------- | -------------------------------------- | ---------------------------------------- |
| %Y               | Year with century                      | 2020                                     |
| %m               | Month with zero-prefix                 | 06                                       |
| %B               | Full month name                        | June                                     |
| %b               | Abbreviated month name                 | Jun                                      |
| %d               | Day of the month with zero-prefix      | 05                                       |
| %e               | Day of the month without zero-prefix   | 5                                        |
| %H               | Hour of the day (24-hour)              | 17                                       |
| %k               | Hour of day without 0 prefix (24-hour) | 17                                       |
| %I (capital i)   | Hour of the day (12-hour)              | 05                                       |
| %l (lowercase L) | Hour of day without 0 prefix (12-hour) | 5                                        |
| %p               | AM or PM                               | PM                                       |
| %M               | Minute of the hour                     | 13                                       |
| %S               | Second of the minute                   | 27                                       |
| %L               | Millisecond of the second              | 000                                      |
| %z               | Time zone offset from UTC              | -0700                                    |
| %:z              | Time zone formatted offset from UTC    | -07:00                                   |
| %Z               | Time zone abbrev. name                 | UTC                                      |
| %A               | Full day name                          | Friday                                   |

To access the full list, check out the [Ruby documentation](http://ruby-doc.org/core-2.3.3/Time.html#method-i-strftime)

### How it works

Allows the user to define a datetime format. Returns the datetime input in the specified format.

::: tip Input datatype
The input must be a date or datetime datatype. You can use the <u>[to_date](/formulas/date-formulas.md#to-date)</u> formula to convert a string into a date datatype.
:::

### See also

- [to_date](/formulas/date-formulas.md#to-date): Returns a date in date datatype.

---

## `in_time_zone`

Converts a date or datetime to a different time zone using [IANA time zone names](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones). Returns a datetime. If no time zone is specified, the value defaults to Pacific Time (PT).

### Syntax

<kbd>Date</kbd>.in_time_zone(<span style="color:#FF0000">format</span>)

- <kbd>Date</kbd> - An input date or datetime.
- <span style="color:#FF0000">format</span> - The target timezone.

### Sample usage

| Formula                                                    | Result                             |
| ---------------------------------------------------------- | ---------------------------------- |
| today.in_time_zone("America/New_York")                     | "2020-12-01T00:00:00.000000-04:00" |
| today.to_time.in_time_zone("America/New_York")             | "2020-12-01T20:00:00.000000-04:00" |
| <kbd>"2020-06-01"</kbd>.to_time.in_time_zone               | "2020-05-31T17:00:00.000000-07:00" |
| <kbd>"2020-06-01T01:30:45.000000+00:00"</kbd>.in_time_zone | "2020-05-31T18:30:45.000000-07:00" |

---

## `dst?`

Returns true if the input datetime is within Daylight Savings Time.

### Syntax

<kbd>Datetime</kbd>.dst?

- <kbd>Datetime</kbd> - An input date or datetime.

### Sample usage

| Formula                                                       | Result |
| ------------------------------------------------------------- | ------ |
| today.to_time.dst?                                            | false  |
| today.in_time_zone("America/New_York").dst?                   | true   |
| <kbd>"2020-06-01"</kbd>.in_time_zone("America/New_York").dst? | true   |
| <kbd>"2020-09-06T18:30:15.671720-05:00"</kbd>.to_time.dst?    | false  |

### Regions reference

Refer to the following table for the timezone name to use in the formula.

| Region                       | Timezone to use in formula     | UTC zone  | DST offset?        |
|------------------------------|--------------------------------|-----------|--------------------|
| International Date Line West | Pacific/Midway                 | UTC-11    |                    |
| Midway Island                | Pacific/Midway                 | UTC-11    |                    |
| American Samoa               | Pacific/Pago_Pago              | UTC-11    |                    |
| Hawaii                       | Pacific/Honolulu               | UTC-10    |                    |
| Alaska                       | America/Juneau                 | UTC-9     | :white_check_mark: |
| Pacific Time (US & Canada)   | America/Los_Angeles            | UTC-8     | :white_check_mark: |
| Tijuana                      | America/Tijuana                | UTC-8     | :white_check_mark: |
| Mountain Time (US & Canada)  | America/Denver                 | UTC-7     | :white_check_mark: |
| Arizona                      | America/Phoenix                | UTC-7     |                    |
| Chihuahua                    | America/Chihuahua              | UTC-7     | :white_check_mark: |
| Mazatlan                     | America/Mazatlan               | UTC-7     | :white_check_mark: |
| Central Time (US & Canada)   | America/Chicago                | UTC-6     | :white_check_mark: |
| Saskatchewan                 | America/Regina                 | UTC-6     |                    |
| Guadalajara                  | America/Mexico_City            | UTC-6     | :white_check_mark: |
| Mexico City                  | America/Mexico_City            | UTC-6     | :white_check_mark: |
| Monterrey                    | America/Monterrey              | UTC-6     | :white_check_mark: |
| Central America              | America/Guatemala              | UTC-6     |                    |
| Eastern Time (US & Canada)   | America/New_York               | UTC-5     | :white_check_mark: |
| Indiana (East)               | America/Indiana/Indianapolis   | UTC-5     | :white_check_mark: |
| Bogota                       | America/Bogota                 | UTC-5     |                    |
| Lima                         | America/Lima                   | UTC-5     |                    |
| Quito                        | America/Lima                   | UTC-5     |                    |
| Atlantic Time (Canada)       | America/Halifax                | UTC-4     | :white_check_mark: |
| Caracas                      | America/Caracas                | UTC-4     |                    |
| La Paz                       | America/La_Paz                 | UTC-4     |                    |
| Santiago                     | America/Santiago               | UTC-4     | :white_check_mark: |
| Georgetown                   | America/Guyana                 | UTC-4     |                    |
| Newfoundland                 | America/St_Johns               | UTC-3:30  | :white_check_mark: |
| Brasilia                     | America/Sao_Paulo              | UTC-3     |                    |
| Buenos Aires                 | America/Argentina/Buenos_Aires | UTC-3     |                    |
| Montevideo                   | America/Montevideo             | UTC-3     |                    |
| Greenland                    | America/Godthab                | UTC-3     | :white_check_mark: |
| Mid-Atlantic                 | Atlantic/South_Georgia         | UTC-2     |                    |
| Azores                       | Atlantic/Azores                | UTC-1     | :white_check_mark: |
| Cape Verde Is.              | Atlantic/Cape_Verde            | UTC-1     |                    |
| Dublin                       | Europe/Dublin                  | UTC-1     | :white_check_mark: |
| Lisbon                       | Europe/Lisbon                  | UTC+0     | :white_check_mark: |
| Edinburgh                    | Europe/London                  | UTC+0     | :white_check_mark: |
| London                       | Europe/London                  | UTC+0     | :white_check_mark: |
| Monrovia                     | Africa/Monrovia                | UTC+0     |                    |
| UTC                          | Etc/UTC                        | UTC+0     |                    |
| Casablanca                   | Africa/Casablanca              | UTC+1     |                    |
| Belgrade                     | Europe/Belgrade                | UTC+1     | :white_check_mark: |
| Bratislava                   | Europe/Bratislava              | UTC+1     | :white_check_mark: |
| Budapest                     | Europe/Budapest                | UTC+1     | :white_check_mark: |
| Ljubljana                    | Europe/Ljubljana               | UTC+1     | :white_check_mark: |
| Prague                       | Europe/Prague                  | UTC+1     | :white_check_mark: |
| Sarajevo                     | Europe/Sarajevo                | UTC+1     | :white_check_mark: |
| Skopje                       | Europe/Skopje                  | UTC+1     | :white_check_mark: |
| Warsaw                       | Europe/Warsaw                  | UTC+1     | :white_check_mark: |
| Zagreb                       | Europe/Zagreb                  | UTC+1     | :white_check_mark: |
| Brussels                     | Europe/Brussels                | UTC+1     | :white_check_mark: |
| Copenhagen                   | Europe/Copenhagen              | UTC+1     | :white_check_mark: |
| Madrid                       | Europe/Madrid                  | UTC+1     | :white_check_mark: |
| Paris                        | Europe/Paris                   | UTC+1     | :white_check_mark: |
| Amsterdam                    | Europe/Amsterdam               | UTC+1     | :white_check_mark: |
| Berlin                       | Europe/Berlin                  | UTC+1     | :white_check_mark: |
| Bern                         | Europe/Zurich                  | UTC+1     | :white_check_mark: |
| Zurich                       | Europe/Zurich                  | UTC+1     | :white_check_mark: |
| Rome                         | Europe/Rome                    | UTC+1     | :white_check_mark: |
| Stockholm                    | Europe/Stockholm               | UTC+1     | :white_check_mark: |
| Vienna                       | Europe/Vienna                  | UTC+1     | :white_check_mark: |
| West Central Africa          | Africa/Algiers                 | UTC+1     |                    |
| Bucharest                    | Europe/Bucharest               | UTC+2     | :white_check_mark: |
| Cairo                        | Africa/Cairo                   | UTC+2     |                    |
| Helsinki                     | Europe/Helsinki                | UTC+2     | :white_check_mark: |
| Kyiv                         | Europe/Kiev                    | UTC+2     | :white_check_mark: |
| Riga                         | Europe/Riga                    | UTC+2     | :white_check_mark: |
| Sofia                        | Europe/Sofia                   | UTC+2     | :white_check_mark: |
| Tallinn                      | Europe/Tallinn                 | UTC+2     | :white_check_mark: |
| Vilnius                      | Europe/Vilnius                 | UTC+2     | :white_check_mark: |
| Athens                       | Europe/Athens                  | UTC+2     | :white_check_mark: |
| Jerusalem                    | Asia/Jerusalem                 | UTC+2     | :white_check_mark: |
| Harare                       | Africa/Harare                  | UTC+2     |                    |
| Pretoria                     | Africa/Johannesburg            | UTC+2     |                    |
| Kaliningrad                  | Europe/Kaliningrad             | UTC+2     |                    |
| Istanbul                     | Europe/Istanbul                | UTC+3     |                    |
| Minsk                        | Europe/Minsk                   | UTC+3     |                    |
| Moscow                       | Europe/Moscow                  | UTC+3     |                    |
| St. Petersburg               | Europe/Moscow                  | UTC+3     |                    |
| Kuwait                       | Asia/Kuwait                    | UTC+3     |                    |
| Riyadh                       | Asia/Riyadh                    | UTC+3     |                    |
| Nairobi                      | Africa/Nairobi                 | UTC+3     |                    |
| Baghdad                      | Asia/Baghdad                   | UTC+3     |                    |
| Tehran                       | Asia/Tehran                    | UTC+3:30  | :white_check_mark: |
| Volgograd                    | Europe/Volgograd               | UTC+4     |                    |
| Samara                       | Europe/Samara                  | UTC+4     |                    |
| Abu Dhabi                    | Asia/Muscat                    | UTC+4     |                    |
| Muscat                       | Asia/Muscat                    | UTC+4     |                    |
| Baku                         | Asia/Baku                      | UTC+4     |                    |
| Tbilisi                      | Asia/Tbilisi                   | UTC+4     |                    |
| Yerevan                      | Asia/Yerevan                   | UTC+4     |                    |
| Kabul                        | Asia/Kabul                     | UTC+4:30  | :white_check_mark: |
| Ekaterinburg                 | Asia/Yekaterinburg             | UTC+5     |                    |
| Islamabad                    | Asia/Karachi                   | UTC+5     |                    |
| Karachi                      | Asia/Karachi                   | UTC+5     |                    |
| Tashkent                     | Asia/Tashkent                  | UTC+5     |                    |
| Sri Jayawardenepura          | Asia/Colombo                   | UTC+5:30  | :white_check_mark: |
| Chennai                      | Asia/Kolkata                   | UTC+5:30  | :white_check_mark: |
| Kolkata                      | Asia/Kolkata                   | UTC+5:30  | :white_check_mark: |
| Mumbai                       | Asia/Kolkata                   | UTC+5:30  | :white_check_mark: |
| New Delhi                    | Asia/Kolkata                   | UTC+5:30  | :white_check_mark: |
| Kathmandu                    | Asia/Kathmandu                 | UTC+5:45  | :white_check_mark: |
| Astana                       | Asia/Dhaka                     | UTC+6     |                    |
| Dhaka                        | Asia/Dhaka                     | UTC+6     |                    |
| Almaty                       | Asia/Almaty                    | UTC+6     |                    |
| Urumqi                       | Asia/Urumqi                    | UTC+6     |                    |
| Rangoon                      | Asia/Rangoon                   | UTC+6:30  | :white_check_mark: |
| Novosibirsk                  | Asia/Novosibirsk               | UTC+7     |                    |
| Bangkok                      | Asia/Bangkok                   | UTC+7     |                    |
| Hanoi                        | Asia/Bangkok                   | UTC+7     |                    |
| Jakarta                      | Asia/Jakarta                   | UTC+7     |                    |
| Krasnoyarsk                  | Asia/Krasnoyarsk               | UTC+7     |                    |
| Beijing                      | Asia/Shanghai                  | UTC+8     |                    |
| Chongqing                    | Asia/Chongqing                 | UTC+8     |                    |
| Hong Kong                    | Asia/Hong_Kong                 | UTC+8     |                    |
| Kuala Lumpur                 | Asia/Kuala_Lumpur              | UTC+8     |                    |
| Singapore                    | Asia/Singapore                 | UTC+8     |                    |
| Taipei                       | Asia/Taipei                    | UTC+8     |                    |
| Perth                        | Australia/Perth                | UTC+8     |                    |
| Irkutsk                      | Asia/Irkutsk                   | UTC+8     |                    |
| Ulaanbaatar                  | Asia/Ulaanbaatar               | UTC+8     |                    |
| Seoul                        | Asia/Seoul                     | UTC+9     |                    |
| Osaka                        | Asia/Tokyo                     | UTC+9     |                    |
| Sapporo                      | Asia/Tokyo                     | UTC+9     |                    |
| Tokyo                        | Asia/Tokyo                     | UTC+9     |                    |
| Yakutsk                      | Asia/Yakutsk                   | UTC+9     |                    |
| Darwin                       | Australia/Darwin               | UTC+9:30  |                    |
| Adelaide                     | Australia/Adelaide             | UTC+9:30  | :white_check_mark: |
| Canberra                     | Australia/Melbourne            | UTC+10    | :white_check_mark: |
| Melbourne                    | Australia/Melbourne            | UTC+10    | :white_check_mark: |
| Sydney                       | Australia/Sydney               | UTC+10    | :white_check_mark: |
| Brisbane                     | Australia/Brisbane             | UTC+10    |                    |
| Hobart                       | Australia/Hobart               | UTC+10    | :white_check_mark: |
| Vladivostok                  | Asia/Vladivostok               | UTC+10    |                    |
| Guam                         | Pacific/Guam                   | UTC+10    |                    |
| Port Moresby                 | Pacific/Port_Moresby           | UTC+10    |                    |
| Magadan                      | Asia/Magadan                   | UTC+11    |                    |
| Srednekolymsk                | Asia/Srednekolymsk             | UTC+11    |                    |
| Solomon Is.                 | Pacific/Guadalcanal            | UTC+11    |                    |
| New Caledonia                | Pacific/Noumea                 | UTC+11    |                    |
| Fiji                         | Pacific/Fiji                   | UTC+12    | :white_check_mark: |
| Kamchatka                    | Asia/Kamchatka                 | UTC+12    |                    |
| Marshall Is.                | Pacific/Majuro                 | UTC+12    |                    |
| Auckland                     | Pacific/Auckland               | UTC+12    | :white_check_mark: |
| Wellington                   | Pacific/Auckland               | UTC+12    | :white_check_mark: |
| Nuku'alofa                   | Pacific/Tongatapu              | UTC+13    |                    |
| Tokelau Is.                 | Pacific/Fakaofo                | UTC+13    |                    |
| Samoa                        | Pacific/Apia                   | UTC+13    |                    |
| Chatham Is.                 | Pacific/Chatham                | UTC+13:45 | :white_check_mark: |

---

## `to_date`

This formula converts input data into a date and returns the date formatted as `YYYY-MM-DD`.


### Syntax

<kbd>String</kbd>.to_date(format: <span style="color:#FF0000">format</span>)

- <kbd>String</kbd> - A string input that describes a date or datetime.
- <span style="color:#FF0000">format</span> - (optional) The format of the input date string. If not specified, Workato parses the input string automatically.

::: warning FORMAT PARAMETER DOESN'T AFFECT OUTPUT FORMAT
The `format` parameter defines only the input format. It does not affect the output format, which is always returned as `YYYY-MM-DD`.
:::

### Sample usage

| Formula                                                        | Result       |
| -------------------------------------------------------------- | ------------ |
| <kbd>"23-01-2020 10:30 pm"</kbd>.to_date(format: "DD-MM-YYYY") | "2020-01-23" |
| <kbd>"01-23-2020 10:30 pm"</kbd>.to_date(format: "MM-DD-YYYY") | "2020-01-23" |
| <kbd>"2020/01/23"</kbd>.to_date(format: "YYYY/MM/DD")          | "2020-01-23" |
| <kbd>"06/27/25"</kbd>.to_date(format: "%m/%d/%y")              | "2025-06-27" |

### How it works

Converts the input data into a date datatype.

::: tip INPUT DATA BEST PRACTICE
We recommend that you specify the input data format. If you don't specify the input data format, Workato parses the input string automatically.

The input string must resemble a date for this formula to work.
:::

### See also

- [strftime](/formulas/date-formulas.md#strftime): Returns datetime is a custom format.
- [to_time](/formulas/date-formulas.md#to-time): Converts a string to an ISO timestamp.

---

## `to_time`

Converts a string to an ISO timestamp. The response will use the UTC timezone (+00:00).

### Syntax

<kbd>String</kbd>.to_time(format: <span style="color:#FF0000">format</span>)

- <kbd>String</kbd> - An input string that describes a date or datetime.
- <span style="color:#FF0000">format</span> - (optional) The format of the user-defined datetime written as a string.

### Sample usage

| Formula                                               | Result        |
| ----------------------------------------------------- | ------------- |
| <kbd>"2020-04-02T12:30:30.462659-07:00"</kbd>.to_time(format: "%Y-%m-%dT%H:%M:%S") | "2020-04-02T19:30:30.000+00:00"  |
| <kbd>"2020-04-02"</kbd>.to_time                                                    | "2020-04-02T00:00:00.000+00:00"  |

### How it works

Converts the input string into a datetime datatype. The output datetime will be converted to the UTC timezone (+00:00).

::: tip Autofill time
If the input data does not include the time, the output will default to `00:00:00.000000 +00:00`.
:::

### See also

- [strftime](/formulas/date-formulas.md#strftime): Returns datetime is a custom format.
- [to_date](/formulas/date-formulas.md#to-date): This formula converts the date-like input into a date. Returns the date formatted as YYYY-MM-DD.

### Parameters

As previously shown, each code (`%B`, `%e`, `%I`, for example) refers to a specific element of `datetime`. You can also add static text and punctuation, such as commas (`,`), slashes (`/`), and colons (`:`). Refer to the following list of frequently used codes:

| Code             | Meaning                                | Example<br>(2020-06-05T17:13:27.000000-07:00) |
| ---------------- | -------------------------------------- | ---------------------------------------- |
| %Y               | Year with century                      | 2020                                     |
| %m               | Month with zero-prefix                 | 06                                       |
| %B               | Full month name                        | June                                     |
| %b               | Abbreviated month name                 | Jun                                      |
| %d               | Day of the month with zero-prefix      | 05                                       |
| %e               | Day of the month without zero-prefix   | 5                                        |
| %H               | Hour of the day (24-hour)              | 17                                       |
| %k               | Hour of day without 0 prefix (24-hour) | 17                                       |
| %I (capital i)   | Hour of the day (12-hour)              | 05                                       |
| %l (lowercase L) | Hour of day without 0 prefix (12-hour) | 5                                        |
| %p               | AM or PM                               | PM                                       |
| %M               | Minute of the hour                     | 13                                       |
| %S               | Second of the minute                   | 27                                       |
| %L               | Millisecond of the second              | 000                                      |
| %z               | Time zone offset from UTC              | -0700                                    |
| %:z              | Time zone formatted offset from UTC    | -07:00                                   |
| %Z               | Time zone abbrev. name                 | UTC                                      |
| %A               | Full day name                          | Friday                                   |

To access the full list, check out the [Ruby documentation](http://ruby-doc.org/core-2.3.3/Time.html#method-i-strftime)

---

## `to_i`

Convert datetime into epoch time. Returns an epoch time in UTC (+00:00).

### Syntax

<kbd>Datetime</kbd>.to_i

- <kbd>Datetime</kbd> - An input datetime.

### Sample usage

| Formula                                           | Result     |
| ------------------------------------------------- | ---------- |
| today.to_time.to_i 								| 1645660800 |
| now.to_i                     						| 1645714000 |

### How it works

Converts the input datetime into an integer, it will return epoch time in seconds, not milliseconds. The output datetime will be converted to the UTC timezone (+00:00).

::: tip Converting between Epoch time to datetime

Convert time formats easily with Workato formulas.

#### How to convert human readable time to epoch time

Use `to_i` to convert a datetime datapill to epoch time (in UTC). Learn more about [how it works](/formulas/date-formulas.md#to-i).

#### How to convert epoch time to human-readable time

Use the following formula to convert an epoch time to human-readable datetime.

Note that the output will be in UTC timezone (+00:00).

`"1970-01-01".to_time + `<kbd>Epoch time</kbd>`.seconds`

If you plan to convert epoch time to a specific timezone, you must specify it with [in_time_zone](/formulas/date-formulas.md#in-time-zone).

`"1970-01-01".to_time.in_time_zone("US/Pacific") + `<kbd>Epoch time</kbd>`.seconds`
:::

::: danger Wrong datatype: undefined method `to_i`
Epoch time requires a datetime datapill. If you are using a date datapill, it will cause an error.

Use [to_time](/formulas/date-formulas.md#to-time) to convert a date into a datetime before converting to epoch time.
:::

### See also

- [to_time](/formulas/date-formulas.md#to-time): Converts a string to an ISO timestamp.
- [to_date](/formulas/date-formulas.md#to-date): This formula converts the date-like input into a date. Returns the date formatted as YYYY-MM-DD.
- [in_time_zone](/formulas/date-formulas.md#in-time-zone): Converts a time value to a different time zone.
