# ApiCollection


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**name** | **str** |  | 
**project_id** | **str** |  | 
**url** | **str** |  | 
**api_spec_url** | **str** |  | 
**version** | **str** |  | 
**created_at** | **datetime** |  | 
**updated_at** | **datetime** |  | 
**message** | **str** | Only present in creation/import responses | [optional] 
**import_results** | [**ImportResults**](ImportResults.md) |  | [optional] 

## Example

```python
from workato_platform_cli.client.workato_api.models.api_collection import ApiCollection

# TODO update the JSON string below
json = "{}"
# create an instance of ApiCollection from a JSON string
api_collection_instance = ApiCollection.from_json(json)
# print the JSON string representation of the object
print(ApiCollection.to_json())

# convert the object into a dict
api_collection_dict = api_collection_instance.to_dict()
# create an instance of ApiCollection from a dict
api_collection_from_dict = ApiCollection.from_dict(api_collection_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


