# workato_platform.client.workato_api.PropertiesApi

All URIs are relative to *https://www.workato.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_project_properties**](PropertiesApi.md#list_project_properties) | **GET** /api/properties | List project properties
[**upsert_project_properties**](PropertiesApi.md#upsert_project_properties) | **POST** /api/properties | Upsert project properties


# **list_project_properties**
> Dict[str, str] list_project_properties(prefix, project_id)

List project properties

Returns a list of project-level properties belonging to a specific project in a
customer workspace that matches a project_id you specify. You must also include
a prefix. For example, if you provide the prefix salesforce_sync., any project
property with a name beginning with salesforce_sync., such as
salesforce_sync.admin_email, with the project_id you provided is returned.


### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform.client.workato_api
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
    api_instance = workato_platform.client.workato_api.PropertiesApi(api_client)
    prefix = 'salesforce_sync.' # str | Returns properties that contain the prefix you provided. For example, if the prefix is salesforce_sync. the property salesforce_sync.admin_email is returned. 
    project_id = 523144 # int | Returns project-level properties that match the project_id you specify. If this parameter is not present, this call returns environment properties. 

    try:
        # List project properties
        api_response = await api_instance.list_project_properties(prefix, project_id)
        print("The response of PropertiesApi->list_project_properties:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PropertiesApi->list_project_properties: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **prefix** | **str**| Returns properties that contain the prefix you provided. For example, if the prefix is salesforce_sync. the property salesforce_sync.admin_email is returned.  | 
 **project_id** | **int**| Returns project-level properties that match the project_id you specify. If this parameter is not present, this call returns environment properties.  | 

### Return type

**Dict[str, str]**

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Project properties retrieved successfully |  -  |
**401** | Authentication required |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upsert_project_properties**
> SuccessResponse upsert_project_properties(project_id, upsert_project_properties_request)

Upsert project properties

Upserts project properties belonging to a specific project in a customer workspace
that matches a project_id you specify. This endpoint maps to properties based on
the names you provide in the request.

## Property Limits
- Maximum number of project properties per project: 1,000
- Maximum length of project property name: 100 characters
- Maximum length of project property value: 1,024 characters


### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform.client.workato_api
from workato_platform.client.workato_api.models.success_response import SuccessResponse
from workato_platform.client.workato_api.models.upsert_project_properties_request import UpsertProjectPropertiesRequest
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
    api_instance = workato_platform.client.workato_api.PropertiesApi(api_client)
    project_id = 523144 # int | Provide the project ID that contains the project properties you plan to upsert. If this parameter is not present, this call upserts environment properties. 
    upsert_project_properties_request = workato_platform.client.workato_api.UpsertProjectPropertiesRequest() # UpsertProjectPropertiesRequest | 

    try:
        # Upsert project properties
        api_response = await api_instance.upsert_project_properties(project_id, upsert_project_properties_request)
        print("The response of PropertiesApi->upsert_project_properties:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PropertiesApi->upsert_project_properties: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**| Provide the project ID that contains the project properties you plan to upsert. If this parameter is not present, this call upserts environment properties.  | 
 **upsert_project_properties_request** | [**UpsertProjectPropertiesRequest**](UpsertProjectPropertiesRequest.md)|  | 

### Return type

[**SuccessResponse**](SuccessResponse.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Project properties upserted successfully |  -  |
**400** | Bad request |  -  |
**401** | Authentication required |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

