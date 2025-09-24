# RuntimeUserConnectionCreateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**parent_id** | **int** | ID of parent OAuth connector (connection must be established) | 
**name** | **str** | Optional name for the runtime user connection | [optional] 
**folder_id** | **int** | Folder to put connection (uses current project if not specified) | 
**external_id** | **str** | End user string ID for identifying the connection | 
**callback_url** | **str** | Optional URL called back after successful token acquisition | [optional] 
**redirect_url** | **str** | Optional URL where user is redirected after successful authorization | [optional] 

## Example

```python
from workato_platform.client.workato_api.models.runtime_user_connection_create_request import RuntimeUserConnectionCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RuntimeUserConnectionCreateRequest from a JSON string
runtime_user_connection_create_request_instance = RuntimeUserConnectionCreateRequest.from_json(json)
# print the JSON string representation of the object
print(RuntimeUserConnectionCreateRequest.to_json())

# convert the object into a dict
runtime_user_connection_create_request_dict = runtime_user_connection_create_request_instance.to_dict()
# create an instance of RuntimeUserConnectionCreateRequest from a dict
runtime_user_connection_create_request_from_dict = RuntimeUserConnectionCreateRequest.from_dict(runtime_user_connection_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


