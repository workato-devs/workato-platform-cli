# Recipe


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**user_id** | **int** |  | 
**name** | **str** |  | 
**created_at** | **datetime** |  | 
**updated_at** | **datetime** |  | 
**copy_count** | **int** |  | 
**trigger_application** | **str** |  | [optional] 
**action_applications** | **List[str]** |  | 
**applications** | **List[str]** |  | 
**description** | **str** |  | 
**parameters_schema** | **List[object]** |  | 
**parameters** | **object** |  | 
**webhook_url** | **str** |  | 
**folder_id** | **int** |  | 
**running** | **bool** |  | 
**job_succeeded_count** | **int** |  | 
**job_failed_count** | **int** |  | 
**lifetime_task_count** | **int** |  | 
**last_run_at** | **datetime** |  | [optional] 
**stopped_at** | **datetime** |  | [optional] 
**version_no** | **int** |  | 
**stop_cause** | **str** |  | 
**config** | [**List[RecipeConfigInner]**](RecipeConfigInner.md) |  | 
**trigger_closure** | **object** |  | 
**code** | **str** | Recipe code (may be truncated if exclude_code is true) | 
**author_name** | **str** |  | 
**version_author_name** | **str** |  | 
**version_author_email** | **str** |  | 
**version_comment** | **str** |  | 
**tags** | **List[str]** |  | [optional] 

## Example

```python
from workato_platform_cli.client.workato_api.models.recipe import Recipe

# TODO update the JSON string below
json = "{}"
# create an instance of Recipe from a JSON string
recipe_instance = Recipe.from_json(json)
# print the JSON string representation of the object
print(Recipe.to_json())

# convert the object into a dict
recipe_dict = recipe_instance.to_dict()
# create an instance of Recipe from a dict
recipe_from_dict = Recipe.from_dict(recipe_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


