# ApiClient


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**name** | **str** |  | 
**description** | **str** |  | [optional] 
**active_api_keys_count** | **int** |  | [optional] 
**total_api_keys_count** | **int** |  | [optional] 
**created_at** | **datetime** |  | 
**updated_at** | **datetime** |  | 
**logo** | **str** | URL to the client&#39;s logo image | 
**logo_2x** | **str** | URL to the client&#39;s high-resolution logo image | 
**is_legacy** | **bool** |  | 
**email** | **str** |  | [optional] 
**auth_type** | **str** |  | 
**api_token** | **str** | API token (only returned for token auth type) | [optional] 
**mtls_enabled** | **bool** |  | [optional] 
**validation_formula** | **str** |  | [optional] 
**cert_bundle_ids** | **List[int]** |  | [optional] 
**api_policies** | [**List[ApiClientApiPoliciesInner]**](ApiClientApiPoliciesInner.md) | List of API policies associated with the client | 
**api_collections** | [**List[ApiClientApiCollectionsInner]**](ApiClientApiCollectionsInner.md) | List of API collections associated with the client | 

## Example

```python
from workato_platform_cli.client.workato_api.models.api_client import ApiClient

# TODO update the JSON string below
json = "{}"
# create an instance of ApiClient from a JSON string
api_client_instance = ApiClient.from_json(json)
# print the JSON string representation of the object
print(ApiClient.to_json())

# convert the object into a dict
api_client_dict = api_client_instance.to_dict()
# create an instance of ApiClient from a dict
api_client_from_dict = ApiClient.from_dict(api_client_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


