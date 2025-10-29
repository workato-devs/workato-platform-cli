# RecipeConnectionUpdateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**adapter_name** | **str** | The internal name of the connector | 
**connection_id** | **int** | The ID of the connection that replaces the existing one | 

## Example

```python
from workato_platform_cli.client.workato_api.models.recipe_connection_update_request import RecipeConnectionUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RecipeConnectionUpdateRequest from a JSON string
recipe_connection_update_request_instance = RecipeConnectionUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(RecipeConnectionUpdateRequest.to_json())

# convert the object into a dict
recipe_connection_update_request_dict = recipe_connection_update_request_instance.to_dict()
# create an instance of RecipeConnectionUpdateRequest from a dict
recipe_connection_update_request_from_dict = RecipeConnectionUpdateRequest.from_dict(recipe_connection_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


