# CustomConnectorCodeResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**CustomConnectorCodeResponseData**](CustomConnectorCodeResponseData.md) |  | 

## Example

```python
from workato_platform.client.workato_api.models.custom_connector_code_response import CustomConnectorCodeResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CustomConnectorCodeResponse from a JSON string
custom_connector_code_response_instance = CustomConnectorCodeResponse.from_json(json)
# print the JSON string representation of the object
print(CustomConnectorCodeResponse.to_json())

# convert the object into a dict
custom_connector_code_response_dict = custom_connector_code_response_instance.to_dict()
# create an instance of CustomConnectorCodeResponse from a dict
custom_connector_code_response_from_dict = CustomConnectorCodeResponse.from_dict(custom_connector_code_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


