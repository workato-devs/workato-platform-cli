# PicklistRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**pick_list_name** | **str** | Name of the pick list | 
**pick_list_params** | **Dict[str, object]** | Picklist parameters, required in some picklists | [optional] 

## Example

```python
from workato_platform.client.workato_api.models.picklist_request import PicklistRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PicklistRequest from a JSON string
picklist_request_instance = PicklistRequest.from_json(json)
# print the JSON string representation of the object
print(PicklistRequest.to_json())

# convert the object into a dict
picklist_request_dict = picklist_request_instance.to_dict()
# create an instance of PicklistRequest from a dict
picklist_request_from_dict = PicklistRequest.from_dict(picklist_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


