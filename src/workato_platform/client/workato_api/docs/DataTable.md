# DataTable


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**name** | **str** |  | 
**var_schema** | [**List[DataTableColumn]**](DataTableColumn.md) |  | 
**folder_id** | **int** |  | 
**created_at** | **datetime** |  | 
**updated_at** | **datetime** |  | 

## Example

```python
from workato_platform.client.workato_api.models.data_table import DataTable

# TODO update the JSON string below
json = "{}"
# create an instance of DataTable from a JSON string
data_table_instance = DataTable.from_json(json)
# print the JSON string representation of the object
print(DataTable.to_json())

# convert the object into a dict
data_table_dict = data_table_instance.to_dict()
# create an instance of DataTable from a dict
data_table_from_dict = DataTable.from_dict(data_table_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


