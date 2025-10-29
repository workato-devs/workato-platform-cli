# ExportManifestResponseResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**name** | **str** |  | 
**last_exported_at** | **datetime** |  | 
**created_at** | **datetime** |  | 
**updated_at** | **datetime** |  | 
**deleted_at** | **datetime** |  | 
**project_path** | **str** |  | 
**status** | **str** |  | 

## Example

```python
from workato_platform_cli.client.workato_api.models.export_manifest_response_result import ExportManifestResponseResult

# TODO update the JSON string below
json = "{}"
# create an instance of ExportManifestResponseResult from a JSON string
export_manifest_response_result_instance = ExportManifestResponseResult.from_json(json)
# print the JSON string representation of the object
print(ExportManifestResponseResult.to_json())

# convert the object into a dict
export_manifest_response_result_dict = export_manifest_response_result_instance.to_dict()
# create an instance of ExportManifestResponseResult from a dict
export_manifest_response_result_from_dict = ExportManifestResponseResult.from_dict(export_manifest_response_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


