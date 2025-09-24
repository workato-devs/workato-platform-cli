# UpsertProjectPropertiesRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**properties** | **Dict[str, str]** | Contains the names and values of the properties you plan to upsert. Property names are limited to 100 characters, values to 1,024 characters.  | 

## Example

```python
from workato_platform.client.workato_api.models.upsert_project_properties_request import UpsertProjectPropertiesRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpsertProjectPropertiesRequest from a JSON string
upsert_project_properties_request_instance = UpsertProjectPropertiesRequest.from_json(json)
# print the JSON string representation of the object
print(UpsertProjectPropertiesRequest.to_json())

# convert the object into a dict
upsert_project_properties_request_dict = upsert_project_properties_request_instance.to_dict()
# create an instance of UpsertProjectPropertiesRequest from a dict
upsert_project_properties_request_from_dict = UpsertProjectPropertiesRequest.from_dict(upsert_project_properties_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


