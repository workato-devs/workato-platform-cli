# DataTableCreateResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**DataTable**](DataTable.md) |  | 

## Example

```python
from workato_platform_cli.client.workato_api.models.data_table_create_response import DataTableCreateResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DataTableCreateResponse from a JSON string
data_table_create_response_instance = DataTableCreateResponse.from_json(json)
# print the JSON string representation of the object
print(DataTableCreateResponse.to_json())

# convert the object into a dict
data_table_create_response_dict = data_table_create_response_instance.to_dict()
# create an instance of DataTableCreateResponse from a dict
data_table_create_response_from_dict = DataTableCreateResponse.from_dict(data_table_create_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


