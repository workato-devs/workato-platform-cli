# FolderAssetsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**result** | [**FolderAssetsResponseResult**](FolderAssetsResponseResult.md) |  | 

## Example

```python
from workato_platform_cli.client.workato_api.models.folder_assets_response import FolderAssetsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of FolderAssetsResponse from a JSON string
folder_assets_response_instance = FolderAssetsResponse.from_json(json)
# print the JSON string representation of the object
print(FolderAssetsResponse.to_json())

# convert the object into a dict
folder_assets_response_dict = folder_assets_response_instance.to_dict()
# create an instance of FolderAssetsResponse from a dict
folder_assets_response_from_dict = FolderAssetsResponse.from_dict(folder_assets_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


