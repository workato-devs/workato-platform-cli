# CreateFolderRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of the folder | 
**parent_id** | **str** | Parent folder ID. Defaults to Home folder if not specified | [optional] 

## Example

```python
from workato_platform.client.workato_api.models.create_folder_request import CreateFolderRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateFolderRequest from a JSON string
create_folder_request_instance = CreateFolderRequest.from_json(json)
# print the JSON string representation of the object
print(CreateFolderRequest.to_json())

# convert the object into a dict
create_folder_request_dict = create_folder_request_instance.to_dict()
# create an instance of CreateFolderRequest from a dict
create_folder_request_from_dict = CreateFolderRequest.from_dict(create_folder_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


