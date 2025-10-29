# OAuthUrlResponseData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**url** | **str** | The OAuth authorization URL | 

## Example

```python
from workato_platform_cli.client.workato_api.models.o_auth_url_response_data import OAuthUrlResponseData

# TODO update the JSON string below
json = "{}"
# create an instance of OAuthUrlResponseData from a JSON string
o_auth_url_response_data_instance = OAuthUrlResponseData.from_json(json)
# print the JSON string representation of the object
print(OAuthUrlResponseData.to_json())

# convert the object into a dict
o_auth_url_response_data_dict = o_auth_url_response_data_instance.to_dict()
# create an instance of OAuthUrlResponseData from a dict
o_auth_url_response_data_from_dict = OAuthUrlResponseData.from_dict(o_auth_url_response_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


