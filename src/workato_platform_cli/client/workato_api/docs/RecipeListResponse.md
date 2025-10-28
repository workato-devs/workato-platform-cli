# RecipeListResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[Recipe]**](Recipe.md) |  | 

## Example

```python
from workato_platform.client.workato_api.models.recipe_list_response import RecipeListResponse

# TODO update the JSON string below
json = "{}"
# create an instance of RecipeListResponse from a JSON string
recipe_list_response_instance = RecipeListResponse.from_json(json)
# print the JSON string representation of the object
print(RecipeListResponse.to_json())

# convert the object into a dict
recipe_list_response_dict = recipe_list_response_instance.to_dict()
# create an instance of RecipeListResponse from a dict
recipe_list_response_from_dict = RecipeListResponse.from_dict(recipe_list_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


