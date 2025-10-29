# CustomConnector


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**name** | **str** |  | 
**title** | **str** |  | 
**latest_released_version** | **int** |  | 
**latest_released_version_note** | **str** |  | 
**released_versions** | [**List[ConnectorVersion]**](ConnectorVersion.md) |  | 
**static_webhook_url** | **str** |  | 

## Example

```python
from workato_platform_cli.client.workato_api.models.custom_connector import CustomConnector

# TODO update the JSON string below
json = "{}"
# create an instance of CustomConnector from a JSON string
custom_connector_instance = CustomConnector.from_json(json)
# print the JSON string representation of the object
print(CustomConnector.to_json())

# convert the object into a dict
custom_connector_dict = custom_connector_instance.to_dict()
# create an instance of CustomConnector from a dict
custom_connector_from_dict = CustomConnector.from_dict(custom_connector_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


