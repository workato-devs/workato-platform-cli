# CustomConnectorListResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**result** | [**List[CustomConnector]**](CustomConnector.md) |  | 

## Example

```python
from workato_platform_cli.client.workato_api.models.custom_connector_list_response import CustomConnectorListResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CustomConnectorListResponse from a JSON string
custom_connector_list_response_instance = CustomConnectorListResponse.from_json(json)
# print the JSON string representation of the object
print(CustomConnectorListResponse.to_json())

# convert the object into a dict
custom_connector_list_response_dict = custom_connector_list_response_instance.to_dict()
# create an instance of CustomConnectorListResponse from a dict
custom_connector_list_response_from_dict = CustomConnectorListResponse.from_dict(custom_connector_list_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


