# RecipeConfigInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**keyword** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**provider** | **str** |  | [optional] 
**skip_validation** | **bool** |  | [optional] 
**account_id** | **int** |  | [optional] 

## Example

```python
from workato_platform.client.workato_api.models.recipe_config_inner import RecipeConfigInner

# TODO update the JSON string below
json = "{}"
# create an instance of RecipeConfigInner from a JSON string
recipe_config_inner_instance = RecipeConfigInner.from_json(json)
# print the JSON string representation of the object
print(RecipeConfigInner.to_json())

# convert the object into a dict
recipe_config_inner_dict = recipe_config_inner_instance.to_dict()
# create an instance of RecipeConfigInner from a dict
recipe_config_inner_from_dict = RecipeConfigInner.from_dict(recipe_config_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


