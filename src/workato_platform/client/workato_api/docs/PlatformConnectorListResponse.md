# PlatformConnectorListResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[PlatformConnector]**](PlatformConnector.md) |  | 
**count** | **int** |  | 
**page** | **int** |  | 
**per_page** | **int** |  | 

## Example

```python
from workato_platform.client.workato_api.models.platform_connector_list_response import PlatformConnectorListResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PlatformConnectorListResponse from a JSON string
platform_connector_list_response_instance = PlatformConnectorListResponse.from_json(json)
# print the JSON string representation of the object
print(PlatformConnectorListResponse.to_json())

# convert the object into a dict
platform_connector_list_response_dict = platform_connector_list_response_instance.to_dict()
# create an instance of PlatformConnectorListResponse from a dict
platform_connector_list_response_from_dict = PlatformConnectorListResponse.from_dict(platform_connector_list_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


