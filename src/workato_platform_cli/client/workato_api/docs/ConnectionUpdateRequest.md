# ConnectionUpdateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of the connection | [optional] 
**parent_id** | **int** | The ID of the parent connection (must be same provider type) | [optional] 
**folder_id** | **int** | The ID of the project or folder containing the connection | [optional] 
**external_id** | **str** | The external ID assigned to the connection | [optional] 
**shell_connection** | **bool** | Specifies whether the connection is a shell connection or authenticated connection. If false, credentials are passed and connection is tested. If true, credentials are passed but connection isn&#39;t tested.  | [optional] [default to False]
**input** | **Dict[str, object]** | Connection parameters (varies by provider) | [optional] 

## Example

```python
from workato_platform_cli.client.workato_api.models.connection_update_request import ConnectionUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ConnectionUpdateRequest from a JSON string
connection_update_request_instance = ConnectionUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(ConnectionUpdateRequest.to_json())

# convert the object into a dict
connection_update_request_dict = connection_update_request_instance.to_dict()
# create an instance of ConnectionUpdateRequest from a dict
connection_update_request_from_dict = ConnectionUpdateRequest.from_dict(connection_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


