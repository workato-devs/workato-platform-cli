# ConnectorVersion


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**version** | **int** |  | 
**version_note** | **str** |  | 
**created_at** | **datetime** |  | 
**released_at** | **datetime** |  | 

## Example

```python
from workato_platform.client.workato_api.models.connector_version import ConnectorVersion

# TODO update the JSON string below
json = "{}"
# create an instance of ConnectorVersion from a JSON string
connector_version_instance = ConnectorVersion.from_json(json)
# print the JSON string representation of the object
print(ConnectorVersion.to_json())

# convert the object into a dict
connector_version_dict = connector_version_instance.to_dict()
# create an instance of ConnectorVersion from a dict
connector_version_from_dict = ConnectorVersion.from_dict(connector_version_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


