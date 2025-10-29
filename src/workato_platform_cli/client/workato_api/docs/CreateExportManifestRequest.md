# CreateExportManifestRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**export_manifest** | [**ExportManifestRequest**](ExportManifestRequest.md) |  | 

## Example

```python
from workato_platform_cli.client.workato_api.models.create_export_manifest_request import CreateExportManifestRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateExportManifestRequest from a JSON string
create_export_manifest_request_instance = CreateExportManifestRequest.from_json(json)
# print the JSON string representation of the object
print(CreateExportManifestRequest.to_json())

# convert the object into a dict
create_export_manifest_request_dict = create_export_manifest_request_instance.to_dict()
# create an instance of CreateExportManifestRequest from a dict
create_export_manifest_request_from_dict = CreateExportManifestRequest.from_dict(create_export_manifest_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


