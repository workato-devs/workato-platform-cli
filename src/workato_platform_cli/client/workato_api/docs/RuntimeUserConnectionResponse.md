# RuntimeUserConnectionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**RuntimeUserConnectionResponseData**](RuntimeUserConnectionResponseData.md) |  | 

## Example

```python
from workato_platform.client.workato_api.models.runtime_user_connection_response import RuntimeUserConnectionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of RuntimeUserConnectionResponse from a JSON string
runtime_user_connection_response_instance = RuntimeUserConnectionResponse.from_json(json)
# print the JSON string representation of the object
print(RuntimeUserConnectionResponse.to_json())

# convert the object into a dict
runtime_user_connection_response_dict = runtime_user_connection_response_instance.to_dict()
# create an instance of RuntimeUserConnectionResponse from a dict
runtime_user_connection_response_from_dict = RuntimeUserConnectionResponse.from_dict(runtime_user_connection_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


