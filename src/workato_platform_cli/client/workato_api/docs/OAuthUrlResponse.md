# OAuthUrlResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**OAuthUrlResponseData**](OAuthUrlResponseData.md) |  | 

## Example

```python
from workato_platform.client.workato_api.models.o_auth_url_response import OAuthUrlResponse

# TODO update the JSON string below
json = "{}"
# create an instance of OAuthUrlResponse from a JSON string
o_auth_url_response_instance = OAuthUrlResponse.from_json(json)
# print the JSON string representation of the object
print(OAuthUrlResponse.to_json())

# convert the object into a dict
o_auth_url_response_dict = o_auth_url_response_instance.to_dict()
# create an instance of OAuthUrlResponse from a dict
o_auth_url_response_from_dict = OAuthUrlResponse.from_dict(o_auth_url_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


