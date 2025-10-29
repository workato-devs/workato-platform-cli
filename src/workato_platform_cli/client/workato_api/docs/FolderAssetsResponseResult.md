# FolderAssetsResponseResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**assets** | [**List[Asset]**](Asset.md) |  | 

## Example

```python
from workato_platform_cli.client.workato_api.models.folder_assets_response_result import FolderAssetsResponseResult

# TODO update the JSON string below
json = "{}"
# create an instance of FolderAssetsResponseResult from a JSON string
folder_assets_response_result_instance = FolderAssetsResponseResult.from_json(json)
# print the JSON string representation of the object
print(FolderAssetsResponseResult.to_json())

# convert the object into a dict
folder_assets_response_result_dict = folder_assets_response_result_instance.to_dict()
# create an instance of FolderAssetsResponseResult from a dict
folder_assets_response_result_from_dict = FolderAssetsResponseResult.from_dict(folder_assets_response_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


