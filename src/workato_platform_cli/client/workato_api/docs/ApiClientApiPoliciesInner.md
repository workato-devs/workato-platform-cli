# ApiClientApiPoliciesInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 

## Example

```python
from workato_platform.client.workato_api.models.api_client_api_policies_inner import ApiClientApiPoliciesInner

# TODO update the JSON string below
json = "{}"
# create an instance of ApiClientApiPoliciesInner from a JSON string
api_client_api_policies_inner_instance = ApiClientApiPoliciesInner.from_json(json)
# print the JSON string representation of the object
print(ApiClientApiPoliciesInner.to_json())

# convert the object into a dict
api_client_api_policies_inner_dict = api_client_api_policies_inner_instance.to_dict()
# create an instance of ApiClientApiPoliciesInner from a dict
api_client_api_policies_inner_from_dict = ApiClientApiPoliciesInner.from_dict(api_client_api_policies_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


