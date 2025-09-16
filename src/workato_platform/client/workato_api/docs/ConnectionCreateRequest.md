# ConnectionCreateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of the connection | 
**provider** | **str** | The application type of the connection | 
**parent_id** | **int** | The ID of the parent connection (must be same provider type) | [optional] 
**folder_id** | **int** | The ID of the project or folder containing the connection | [optional] 
**external_id** | **str** | The external ID assigned to the connection | [optional] 
**shell_connection** | **bool** | Specifies whether the connection is a shell connection or authenticated connection. If false, credentials are passed and connection is tested. If true, credentials are passed but connection isn&#39;t tested.  | [optional] [default to False]
**input** | **Dict[str, object]** | Connection parameters (varies by provider) | [optional] 

## Example

```python
from workato_platform.client.workato_api.models.connection_create_request import ConnectionCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ConnectionCreateRequest from a JSON string
connection_create_request_instance = ConnectionCreateRequest.from_json(json)
# print the JSON string representation of the object
print(ConnectionCreateRequest.to_json())

# convert the object into a dict
connection_create_request_dict = connection_create_request_instance.to_dict()
# create an instance of ConnectionCreateRequest from a dict
connection_create_request_from_dict = ConnectionCreateRequest.from_dict(connection_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


