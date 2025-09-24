# DataTableColumn


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**name** | **str** |  | 
**optional** | **bool** |  | 
**field_id** | **str** |  | 
**hint** | **str** |  | 
**default_value** | **object** | Default value matching the column type | 
**metadata** | **Dict[str, object]** |  | 
**multivalue** | **bool** |  | 
**relation** | [**DataTableRelation**](DataTableRelation.md) |  | 

## Example

```python
from workato_platform.client.workato_api.models.data_table_column import DataTableColumn

# TODO update the JSON string below
json = "{}"
# create an instance of DataTableColumn from a JSON string
data_table_column_instance = DataTableColumn.from_json(json)
# print the JSON string representation of the object
print(DataTableColumn.to_json())

# convert the object into a dict
data_table_column_dict = data_table_column_instance.to_dict()
# create an instance of DataTableColumn from a dict
data_table_column_from_dict = DataTableColumn.from_dict(data_table_column_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


