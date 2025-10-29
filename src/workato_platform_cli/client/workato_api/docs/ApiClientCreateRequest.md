# ApiClientCreateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of the client | 
**description** | **str** | Description of the client | [optional] 
**project_id** | **int** | ID of the project to create the client in | [optional] 
**api_portal_id** | **int** | ID of the API portal to assign the client | [optional] 
**email** | **str** | Email address for the client (required if api_portal_id provided) | [optional] 
**api_collection_ids** | **List[int]** | IDs of API collections to assign to the client | 
**api_policy_id** | **int** | ID of the API policy to apply | [optional] 
**auth_type** | **str** | Authentication method | 
**jwt_method** | **str** | JWT signing method (required when auth_type is jwt) | [optional] 
**jwt_secret** | **str** | HMAC shared secret or RSA public key (required when auth_type is jwt) | [optional] 
**oidc_issuer** | **str** | Discovery URL for OIDC identity provider | [optional] 
**oidc_jwks_uri** | **str** | JWKS URL for OIDC identity provider | [optional] 
**access_profile_claim** | **str** | JWT claim key for access profile identification | [optional] 
**required_claims** | **List[str]** | List of claims to enforce | [optional] 
**allowed_issuers** | **List[str]** | List of allowed issuers | [optional] 
**mtls_enabled** | **bool** | Whether mutual TLS is enabled | [optional] 
**validation_formula** | **str** | Formula to validate client certificates | [optional] 
**cert_bundle_ids** | **List[int]** | Certificate bundle IDs for mTLS | [optional] 

## Example

```python
from workato_platform_cli.client.workato_api.models.api_client_create_request import ApiClientCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ApiClientCreateRequest from a JSON string
api_client_create_request_instance = ApiClientCreateRequest.from_json(json)
# print the JSON string representation of the object
print(ApiClientCreateRequest.to_json())

# convert the object into a dict
api_client_create_request_dict = api_client_create_request_instance.to_dict()
# create an instance of ApiClientCreateRequest from a dict
api_client_create_request_from_dict = ApiClientCreateRequest.from_dict(api_client_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


