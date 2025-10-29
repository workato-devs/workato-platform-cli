# DataTableRelation


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**table_id** | **str** |  | 
**field_id** | **str** |  | 

## Example

```python
from workato_platform_cli.client.workato_api.models.data_table_relation import DataTableRelation

# TODO update the JSON string below
json = "{}"
# create an instance of DataTableRelation from a JSON string
data_table_relation_instance = DataTableRelation.from_json(json)
# print the JSON string representation of the object
print(DataTableRelation.to_json())

# convert the object into a dict
data_table_relation_dict = data_table_relation_instance.to_dict()
# create an instance of DataTableRelation from a dict
data_table_relation_from_dict = DataTableRelation.from_dict(data_table_relation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


