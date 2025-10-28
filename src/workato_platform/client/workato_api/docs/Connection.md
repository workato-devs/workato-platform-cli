# Connection


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**application** | **str** |  | 
**name** | **str** |  | 
**description** | **str** |  | 
**authorized_at** | **datetime** |  | 
**authorization_status** | **str** |  | 
**authorization_error** | **str** |  | 
**created_at** | **datetime** |  | 
**updated_at** | **datetime** |  | 
**external_id** | **str** |  | 
**folder_id** | **int** |  | 
**connection_lost_at** | **datetime** |  | 
**connection_lost_reason** | **str** |  | 
**parent_id** | **int** |  | 
**provider** | **str** |  | [optional] 
**tags** | **List[str]** |  | 

## Example

```python
from workato_platform.client.workato_api.models.connection import Connection

# TODO update the JSON string below
json = "{}"
# create an instance of Connection from a JSON string
connection_instance = Connection.from_json(json)
# print the JSON string representation of the object
print(Connection.to_json())

# convert the object into a dict
connection_dict = connection_instance.to_dict()
# create an instance of Connection from a dict
connection_from_dict = Connection.from_dict(connection_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


