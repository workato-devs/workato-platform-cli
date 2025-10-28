# ExportManifestRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of the new manifest | 
**assets** | [**List[AssetReference]**](AssetReference.md) | Dependent assets to include in the manifest | [optional] 
**folder_id** | **int** | The ID of the folder containing the assets | [optional] 
**include_test_cases** | **bool** | Whether the manifest includes test cases | [optional] [default to False]
**auto_generate_assets** | **bool** | Auto-generates assets from a folder | [optional] [default to False]
**include_data** | **bool** | Include data from automatic asset generation | [optional] [default to False]
**include_tags** | **bool** | Include tags assigned to assets in the export manifest | [optional] [default to False]

## Example

```python
from workato_platform.client.workato_api.models.export_manifest_request import ExportManifestRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ExportManifestRequest from a JSON string
export_manifest_request_instance = ExportManifestRequest.from_json(json)
# print the JSON string representation of the object
print(ExportManifestRequest.to_json())

# convert the object into a dict
export_manifest_request_dict = export_manifest_request_instance.to_dict()
# create an instance of ExportManifestRequest from a dict
export_manifest_request_from_dict = ExportManifestRequest.from_dict(export_manifest_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


