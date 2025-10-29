# ApiEndpoint


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**api_collection_id** | **int** |  | 
**flow_id** | **int** |  | 
**name** | **str** |  | 
**method** | **str** |  | 
**url** | **str** |  | 
**legacy_url** | **str** |  | [optional] 
**base_path** | **str** |  | 
**path** | **str** |  | 
**active** | **bool** |  | 
**legacy** | **bool** |  | 
**created_at** | **datetime** |  | 
**updated_at** | **datetime** |  | 

## Example

```python
from workato_platform_cli.client.workato_api.models.api_endpoint import ApiEndpoint

# TODO update the JSON string below
json = "{}"
# create an instance of ApiEndpoint from a JSON string
api_endpoint_instance = ApiEndpoint.from_json(json)
# print the JSON string representation of the object
print(ApiEndpoint.to_json())

# convert the object into a dict
api_endpoint_dict = api_endpoint_instance.to_dict()
# create an instance of ApiEndpoint from a dict
api_endpoint_from_dict = ApiEndpoint.from_dict(api_endpoint_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


