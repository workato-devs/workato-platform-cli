# PicklistResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | **List[List[object]]** | Array of picklist value tuples [display_name, value, null, boolean] | 

## Example

```python
from workato_platform_cli.client.workato_api.models.picklist_response import PicklistResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PicklistResponse from a JSON string
picklist_response_instance = PicklistResponse.from_json(json)
# print the JSON string representation of the object
print(PicklistResponse.to_json())

# convert the object into a dict
picklist_response_dict = picklist_response_instance.to_dict()
# create an instance of PicklistResponse from a dict
picklist_response_from_dict = PicklistResponse.from_dict(picklist_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


