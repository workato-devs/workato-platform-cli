# DataTableColumnRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** | The data type of the column | 
**name** | **str** | The name of the column | 
**optional** | **bool** | Whether the column is optional | 
**field_id** | **str** | Unique UUID of the column | [optional] 
**hint** | **str** | Tooltip hint for users | [optional] 
**default_value** | **object** | Default value matching the column type | [optional] 
**metadata** | **Dict[str, object]** | Additional metadata | [optional] 
**multivalue** | **bool** | Whether the column accepts multi-value input | [optional] 
**relation** | [**DataTableRelation**](DataTableRelation.md) |  | [optional] 

## Example

```python
from workato_platform.client.workato_api.models.data_table_column_request import DataTableColumnRequest

# TODO update the JSON string below
json = "{}"
# create an instance of DataTableColumnRequest from a JSON string
data_table_column_request_instance = DataTableColumnRequest.from_json(json)
# print the JSON string representation of the object
print(DataTableColumnRequest.to_json())

# convert the object into a dict
data_table_column_request_dict = data_table_column_request_instance.to_dict()
# create an instance of DataTableColumnRequest from a dict
data_table_column_request_from_dict = DataTableColumnRequest.from_dict(data_table_column_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


