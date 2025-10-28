# FolderCreationResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**name** | **str** |  | 
**parent_id** | **int** |  | 
**created_at** | **datetime** |  | 
**updated_at** | **datetime** |  | 
**project_id** | **int** |  | 
**is_project** | **bool** |  | 

## Example

```python
from workato_platform.client.workato_api.models.folder_creation_response import FolderCreationResponse

# TODO update the JSON string below
json = "{}"
# create an instance of FolderCreationResponse from a JSON string
folder_creation_response_instance = FolderCreationResponse.from_json(json)
# print the JSON string representation of the object
print(FolderCreationResponse.to_json())

# convert the object into a dict
folder_creation_response_dict = folder_creation_response_instance.to_dict()
# create an instance of FolderCreationResponse from a dict
folder_creation_response_from_dict = FolderCreationResponse.from_dict(folder_creation_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


