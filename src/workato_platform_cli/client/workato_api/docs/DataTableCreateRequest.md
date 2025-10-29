# DataTableCreateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name of the data table to create | 
**folder_id** | **int** | ID of the folder where to create the data table | 
**var_schema** | [**List[DataTableColumnRequest]**](DataTableColumnRequest.md) | Array of column definitions | 

## Example

```python
from workato_platform_cli.client.workato_api.models.data_table_create_request import DataTableCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of DataTableCreateRequest from a JSON string
data_table_create_request_instance = DataTableCreateRequest.from_json(json)
# print the JSON string representation of the object
print(DataTableCreateRequest.to_json())

# convert the object into a dict
data_table_create_request_dict = data_table_create_request_instance.to_dict()
# create an instance of DataTableCreateRequest from a dict
data_table_create_request_from_dict = DataTableCreateRequest.from_dict(data_table_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


