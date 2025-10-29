# RuntimeUserConnectionResponseData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | The ID of the created runtime user connection | 
**url** | **str** | OAuth URL for user authorization | 

## Example

```python
from workato_platform_cli.client.workato_api.models.runtime_user_connection_response_data import RuntimeUserConnectionResponseData

# TODO update the JSON string below
json = "{}"
# create an instance of RuntimeUserConnectionResponseData from a JSON string
runtime_user_connection_response_data_instance = RuntimeUserConnectionResponseData.from_json(json)
# print the JSON string representation of the object
print(RuntimeUserConnectionResponseData.to_json())

# convert the object into a dict
runtime_user_connection_response_data_dict = runtime_user_connection_response_data_instance.to_dict()
# create an instance of RuntimeUserConnectionResponseData from a dict
runtime_user_connection_response_data_from_dict = RuntimeUserConnectionResponseData.from_dict(runtime_user_connection_response_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


