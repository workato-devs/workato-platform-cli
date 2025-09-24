# ApiCollectionCreateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of the API collection | 
**project_id** | **int** | ID of the project to associate the collection with | [optional] 
**proxy_connection_id** | **int** | ID of a proxy connection for proxy mode | [optional] 
**openapi_spec** | [**OpenApiSpec**](OpenApiSpec.md) |  | [optional] 

## Example

```python
from workato_platform.client.workato_api.models.api_collection_create_request import ApiCollectionCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ApiCollectionCreateRequest from a JSON string
api_collection_create_request_instance = ApiCollectionCreateRequest.from_json(json)
# print the JSON string representation of the object
print(ApiCollectionCreateRequest.to_json())

# convert the object into a dict
api_collection_create_request_dict = api_collection_create_request_instance.to_dict()
# create an instance of ApiCollectionCreateRequest from a dict
api_collection_create_request_from_dict = ApiCollectionCreateRequest.from_dict(api_collection_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


