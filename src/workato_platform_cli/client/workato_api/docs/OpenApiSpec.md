# OpenApiSpec


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content** | **str** | The OpenAPI spec as a JSON or YAML string | 
**format** | **str** | Format of the OpenAPI spec | 

## Example

```python
from workato_platform.client.workato_api.models.open_api_spec import OpenApiSpec

# TODO update the JSON string below
json = "{}"
# create an instance of OpenApiSpec from a JSON string
open_api_spec_instance = OpenApiSpec.from_json(json)
# print the JSON string representation of the object
print(OpenApiSpec.to_json())

# convert the object into a dict
open_api_spec_dict = open_api_spec_instance.to_dict()
# create an instance of OpenApiSpec from a dict
open_api_spec_from_dict = OpenApiSpec.from_dict(open_api_spec_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


