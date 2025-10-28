# AssetReference


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | ID of the dependency | 
**type** | **str** | Type of dependent asset | 
**checked** | **bool** | Determines if the asset is included in the manifest | [optional] [default to True]
**version** | **int** | The version of the asset | [optional] 
**folder** | **str** | The folder that contains the asset | [optional] [default to '']
**absolute_path** | **str** | The absolute path of the asset | 
**root_folder** | **bool** | Name root folder | [optional] [default to False]
**unreachable** | **bool** | Whether the asset is unreachable | [optional] [default to False]
**zip_name** | **str** | Name in the exported zip file | [optional] 

## Example

```python
from workato_platform.client.workato_api.models.asset_reference import AssetReference

# TODO update the JSON string below
json = "{}"
# create an instance of AssetReference from a JSON string
asset_reference_instance = AssetReference.from_json(json)
# print the JSON string representation of the object
print(AssetReference.to_json())

# convert the object into a dict
asset_reference_dict = asset_reference_instance.to_dict()
# create an instance of AssetReference from a dict
asset_reference_from_dict = AssetReference.from_dict(asset_reference_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


