# PlatformConnector


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**title** | **str** |  | 
**categories** | **List[str]** |  | 
**oauth** | **bool** |  | 
**deprecated** | **bool** |  | 
**secondary** | **bool** |  | 
**triggers** | [**List[ConnectorAction]**](ConnectorAction.md) |  | 
**actions** | [**List[ConnectorAction]**](ConnectorAction.md) |  | 

## Example

```python
from workato_platform_cli.client.workato_api.models.platform_connector import PlatformConnector

# TODO update the JSON string below
json = "{}"
# create an instance of PlatformConnector from a JSON string
platform_connector_instance = PlatformConnector.from_json(json)
# print the JSON string representation of the object
print(PlatformConnector.to_json())

# convert the object into a dict
platform_connector_dict = platform_connector_instance.to_dict()
# create an instance of PlatformConnector from a dict
platform_connector_from_dict = PlatformConnector.from_dict(platform_connector_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


