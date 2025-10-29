# ApiKey


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**name** | **str** |  | 
**auth_type** | **str** |  | 
**ip_allow_list** | **List[str]** | List of IP addresses in the allowlist | [optional] 
**ip_deny_list** | **List[str]** | List of IP addresses to deny requests from | [optional] 
**active** | **bool** |  | 
**active_since** | **datetime** |  | 
**auth_token** | **str** | The generated API token | 

## Example

```python
from workato_platform_cli.client.workato_api.models.api_key import ApiKey

# TODO update the JSON string below
json = "{}"
# create an instance of ApiKey from a JSON string
api_key_instance = ApiKey.from_json(json)
# print the JSON string representation of the object
print(ApiKey.to_json())

# convert the object into a dict
api_key_dict = api_key_instance.to_dict()
# create an instance of ApiKey from a dict
api_key_from_dict = ApiKey.from_dict(api_key_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


