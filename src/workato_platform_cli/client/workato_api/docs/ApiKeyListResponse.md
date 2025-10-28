# ApiKeyListResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**List[ApiKey]**](ApiKey.md) |  | 
**count** | **int** | Total number of API keys | 
**page** | **int** | Current page number | 
**per_page** | **int** | Number of items per page | 

## Example

```python
from workato_platform.client.workato_api.models.api_key_list_response import ApiKeyListResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ApiKeyListResponse from a JSON string
api_key_list_response_instance = ApiKeyListResponse.from_json(json)
# print the JSON string representation of the object
print(ApiKeyListResponse.to_json())

# convert the object into a dict
api_key_list_response_dict = api_key_list_response_instance.to_dict()
# create an instance of ApiKeyListResponse from a dict
api_key_list_response_from_dict = ApiKeyListResponse.from_dict(api_key_list_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


