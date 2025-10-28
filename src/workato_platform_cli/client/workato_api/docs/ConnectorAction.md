# ConnectorAction


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**title** | **str** |  | 
**deprecated** | **bool** |  | 
**bulk** | **bool** |  | 
**batch** | **bool** |  | 

## Example

```python
from workato_platform.client.workato_api.models.connector_action import ConnectorAction

# TODO update the JSON string below
json = "{}"
# create an instance of ConnectorAction from a JSON string
connector_action_instance = ConnectorAction.from_json(json)
# print the JSON string representation of the object
print(ConnectorAction.to_json())

# convert the object into a dict
connector_action_dict = connector_action_instance.to_dict()
# create an instance of ConnectorAction from a dict
connector_action_from_dict = ConnectorAction.from_dict(connector_action_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


