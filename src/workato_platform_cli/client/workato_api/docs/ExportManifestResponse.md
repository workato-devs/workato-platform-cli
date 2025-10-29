# ExportManifestResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**result** | [**ExportManifestResponseResult**](ExportManifestResponseResult.md) |  | 

## Example

```python
from workato_platform_cli.client.workato_api.models.export_manifest_response import ExportManifestResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ExportManifestResponse from a JSON string
export_manifest_response_instance = ExportManifestResponse.from_json(json)
# print the JSON string representation of the object
print(ExportManifestResponse.to_json())

# convert the object into a dict
export_manifest_response_dict = export_manifest_response_instance.to_dict()
# create an instance of ExportManifestResponse from a dict
export_manifest_response_from_dict = ExportManifestResponse.from_dict(export_manifest_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


