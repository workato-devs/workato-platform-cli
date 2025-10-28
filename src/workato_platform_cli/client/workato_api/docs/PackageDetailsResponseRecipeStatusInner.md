# PackageDetailsResponseRecipeStatusInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**import_result** | **str** |  | [optional] 

## Example

```python
from workato_platform.client.workato_api.models.package_details_response_recipe_status_inner import PackageDetailsResponseRecipeStatusInner

# TODO update the JSON string below
json = "{}"
# create an instance of PackageDetailsResponseRecipeStatusInner from a JSON string
package_details_response_recipe_status_inner_instance = PackageDetailsResponseRecipeStatusInner.from_json(json)
# print the JSON string representation of the object
print(PackageDetailsResponseRecipeStatusInner.to_json())

# convert the object into a dict
package_details_response_recipe_status_inner_dict = package_details_response_recipe_status_inner_instance.to_dict()
# create an instance of PackageDetailsResponseRecipeStatusInner from a dict
package_details_response_recipe_status_inner_from_dict = PackageDetailsResponseRecipeStatusInner.from_dict(package_details_response_recipe_status_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


