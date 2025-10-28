# PackageDetailsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**operation_type** | **str** |  | 
**status** | **str** |  | 
**export_manifest_id** | **int** |  | [optional] 
**download_url** | **str** |  | [optional] 
**error** | **str** | Error message when status is failed | [optional] 
**recipe_status** | [**List[PackageDetailsResponseRecipeStatusInner]**](PackageDetailsResponseRecipeStatusInner.md) |  | [optional] 

## Example

```python
from workato_platform.client.workato_api.models.package_details_response import PackageDetailsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PackageDetailsResponse from a JSON string
package_details_response_instance = PackageDetailsResponse.from_json(json)
# print the JSON string representation of the object
print(PackageDetailsResponse.to_json())

# convert the object into a dict
package_details_response_dict = package_details_response_instance.to_dict()
# create an instance of PackageDetailsResponse from a dict
package_details_response_from_dict = PackageDetailsResponse.from_dict(package_details_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


