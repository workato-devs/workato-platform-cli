# CustomConnectorCodeResponseData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **str** | The connector code as a stringified value | 

## Example

```python
from workato_platform.client.workato_api.models.custom_connector_code_response_data import CustomConnectorCodeResponseData

# TODO update the JSON string below
json = "{}"
# create an instance of CustomConnectorCodeResponseData from a JSON string
custom_connector_code_response_data_instance = CustomConnectorCodeResponseData.from_json(json)
# print the JSON string representation of the object
print(CustomConnectorCodeResponseData.to_json())

# convert the object into a dict
custom_connector_code_response_data_dict = custom_connector_code_response_data_instance.to_dict()
# create an instance of CustomConnectorCodeResponseData from a dict
custom_connector_code_response_data_from_dict = CustomConnectorCodeResponseData.from_dict(custom_connector_code_response_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


