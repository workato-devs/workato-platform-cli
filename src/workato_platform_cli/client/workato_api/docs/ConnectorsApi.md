# workato_platform_cli.client.workato_api.ConnectorsApi

All URIs are relative to *https://www.workato.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_custom_connector_code**](ConnectorsApi.md#get_custom_connector_code) | **GET** /api/custom_connectors/{id}/code | Get custom connector code
[**list_custom_connectors**](ConnectorsApi.md#list_custom_connectors) | **GET** /api/custom_connectors | List custom connectors
[**list_platform_connectors**](ConnectorsApi.md#list_platform_connectors) | **GET** /api/integrations/all | List platform connectors


# **get_custom_connector_code**
> CustomConnectorCodeResponse get_custom_connector_code(id)

Get custom connector code

Fetch the code for a specific custom connector

### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform_cli.client.workato_api
from workato_platform_cli.client.workato_api.models.custom_connector_code_response import CustomConnectorCodeResponse
from workato_platform_cli.client.workato_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://www.workato.com
# See configuration.py for a list of all supported configuration parameters.
configuration = workato_platform_cli.client.workato_api.Configuration(
    host = "https://www.workato.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: BearerAuth
configuration = workato_platform_cli.client.workato_api.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with workato_platform_cli.client.workato_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = workato_platform_cli.client.workato_api.ConnectorsApi(api_client)
    id = 56 # int | The ID of the custom connector

    try:
        # Get custom connector code
        api_response = await api_instance.get_custom_connector_code(id)
        print("The response of ConnectorsApi->get_custom_connector_code:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConnectorsApi->get_custom_connector_code: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| The ID of the custom connector | 

### Return type

[**CustomConnectorCodeResponse**](CustomConnectorCodeResponse.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Custom connector code retrieved successfully |  -  |
**401** | Authentication required |  -  |
**404** | Custom connector not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_custom_connectors**
> CustomConnectorListResponse list_custom_connectors()

List custom connectors

Returns a list of all custom connectors

### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform_cli.client.workato_api
from workato_platform_cli.client.workato_api.models.custom_connector_list_response import CustomConnectorListResponse
from workato_platform_cli.client.workato_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://www.workato.com
# See configuration.py for a list of all supported configuration parameters.
configuration = workato_platform_cli.client.workato_api.Configuration(
    host = "https://www.workato.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: BearerAuth
configuration = workato_platform_cli.client.workato_api.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with workato_platform_cli.client.workato_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = workato_platform_cli.client.workato_api.ConnectorsApi(api_client)

    try:
        # List custom connectors
        api_response = await api_instance.list_custom_connectors()
        print("The response of ConnectorsApi->list_custom_connectors:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConnectorsApi->list_custom_connectors: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**CustomConnectorListResponse**](CustomConnectorListResponse.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Custom connectors retrieved successfully |  -  |
**401** | Authentication required |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_platform_connectors**
> PlatformConnectorListResponse list_platform_connectors(page=page, per_page=per_page)

List platform connectors

Returns a paginated list of all connectors and associated metadata including
triggers and actions. This includes both standard and platform connectors.


### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform_cli.client.workato_api
from workato_platform_cli.client.workato_api.models.platform_connector_list_response import PlatformConnectorListResponse
from workato_platform_cli.client.workato_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://www.workato.com
# See configuration.py for a list of all supported configuration parameters.
configuration = workato_platform_cli.client.workato_api.Configuration(
    host = "https://www.workato.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: BearerAuth
configuration = workato_platform_cli.client.workato_api.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with workato_platform_cli.client.workato_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = workato_platform_cli.client.workato_api.ConnectorsApi(api_client)
    page = 1 # int | Page number (optional) (default to 1)
    per_page = 1 # int | Number of records per page (max 100) (optional) (default to 1)

    try:
        # List platform connectors
        api_response = await api_instance.list_platform_connectors(page=page, per_page=per_page)
        print("The response of ConnectorsApi->list_platform_connectors:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConnectorsApi->list_platform_connectors: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int**| Page number | [optional] [default to 1]
 **per_page** | **int**| Number of records per page (max 100) | [optional] [default to 1]

### Return type

[**PlatformConnectorListResponse**](PlatformConnectorListResponse.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Platform connectors retrieved successfully |  -  |
**401** | Authentication required |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

