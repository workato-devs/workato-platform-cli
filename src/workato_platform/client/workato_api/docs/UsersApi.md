# workato_platform.client.workato_api.UsersApi

All URIs are relative to *https://www.workato.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_workspace_details**](UsersApi.md#get_workspace_details) | **GET** /api/users/me | Get current user information


# **get_workspace_details**
> User get_workspace_details()

Get current user information

Returns information about the authenticated user

### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform.client.workato_api
from workato_platform.client.workato_api.models.user import User
from workato_platform.client.workato_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://www.workato.com
# See configuration.py for a list of all supported configuration parameters.
configuration = workato_platform.client.workato_api.Configuration(
    host = "https://www.workato.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: BearerAuth
configuration = workato_platform.client.workato_api.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with workato_platform.client.workato_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = workato_platform.client.workato_api.UsersApi(api_client)

    try:
        # Get current user information
        api_response = await api_instance.get_workspace_details()
        print("The response of UsersApi->get_workspace_details:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UsersApi->get_workspace_details: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**User**](User.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | User information retrieved successfully |  -  |
**401** | Authentication required |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

