# workato_platform_cli.client.workato_api.ConnectionsApi

All URIs are relative to *https://www.workato.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_connection**](ConnectionsApi.md#create_connection) | **POST** /api/connections | Create a connection
[**create_runtime_user_connection**](ConnectionsApi.md#create_runtime_user_connection) | **POST** /api/connections/runtime_user_connections | Create OAuth runtime user connection
[**get_connection_oauth_url**](ConnectionsApi.md#get_connection_oauth_url) | **GET** /api/connections/runtime_user_connections/{connection_id}/get_oauth_url | Get OAuth URL for connection
[**get_connection_picklist**](ConnectionsApi.md#get_connection_picklist) | **POST** /api/connections/{connection_id}/pick_list | Get picklist values
[**list_connections**](ConnectionsApi.md#list_connections) | **GET** /api/connections | List connections
[**update_connection**](ConnectionsApi.md#update_connection) | **PUT** /api/connections/{connection_id} | Update a connection


# **create_connection**
> Connection create_connection(connection_create_request)

Create a connection

Create a new connection. Supports creating shell connections or
fully authenticated connections. Does not support OAuth connections
for authentication, but can create shell connections for OAuth providers.


### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform_cli.client.workato_api
from workato_platform_cli.client.workato_api.models.connection import Connection
from workato_platform_cli.client.workato_api.models.connection_create_request import ConnectionCreateRequest
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
    api_instance = workato_platform_cli.client.workato_api.ConnectionsApi(api_client)
    connection_create_request = workato_platform_cli.client.workato_api.ConnectionCreateRequest() # ConnectionCreateRequest | 

    try:
        # Create a connection
        api_response = await api_instance.create_connection(connection_create_request)
        print("The response of ConnectionsApi->create_connection:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConnectionsApi->create_connection: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connection_create_request** | [**ConnectionCreateRequest**](ConnectionCreateRequest.md)|  | 

### Return type

[**Connection**](Connection.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Connection created successfully |  -  |
**400** | Bad request |  -  |
**401** | Authentication required |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_runtime_user_connection**
> RuntimeUserConnectionResponse create_runtime_user_connection(runtime_user_connection_create_request)

Create OAuth runtime user connection

Creates an OAuth runtime user connection. The parent connection must be
an established OAuth connection. This initiates the OAuth flow and provides
a URL for end user authorization.


### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform_cli.client.workato_api
from workato_platform_cli.client.workato_api.models.runtime_user_connection_create_request import RuntimeUserConnectionCreateRequest
from workato_platform_cli.client.workato_api.models.runtime_user_connection_response import RuntimeUserConnectionResponse
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
    api_instance = workato_platform_cli.client.workato_api.ConnectionsApi(api_client)
    runtime_user_connection_create_request = workato_platform_cli.client.workato_api.RuntimeUserConnectionCreateRequest() # RuntimeUserConnectionCreateRequest | 

    try:
        # Create OAuth runtime user connection
        api_response = await api_instance.create_runtime_user_connection(runtime_user_connection_create_request)
        print("The response of ConnectionsApi->create_runtime_user_connection:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConnectionsApi->create_runtime_user_connection: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **runtime_user_connection_create_request** | [**RuntimeUserConnectionCreateRequest**](RuntimeUserConnectionCreateRequest.md)|  | 

### Return type

[**RuntimeUserConnectionResponse**](RuntimeUserConnectionResponse.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Runtime user connection created successfully |  -  |
**400** | Bad request |  -  |
**401** | Authentication required |  -  |
**404** | Parent connection not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_connection_oauth_url**
> OAuthUrlResponse get_connection_oauth_url(connection_id)

Get OAuth URL for connection

Get the OAuth URL for a runtime user connection. This endpoint is used
to retrieve the OAuth authorization URL for establishing or re-authorizing
a connection.


### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform_cli.client.workato_api
from workato_platform_cli.client.workato_api.models.o_auth_url_response import OAuthUrlResponse
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
    api_instance = workato_platform_cli.client.workato_api.ConnectionsApi(api_client)
    connection_id = 56 # int | Connection ID

    try:
        # Get OAuth URL for connection
        api_response = await api_instance.get_connection_oauth_url(connection_id)
        print("The response of ConnectionsApi->get_connection_oauth_url:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConnectionsApi->get_connection_oauth_url: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connection_id** | **int**| Connection ID | 

### Return type

[**OAuthUrlResponse**](OAuthUrlResponse.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OAuth URL retrieved successfully |  -  |
**401** | Authentication required |  -  |
**404** | Connection not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_connection_picklist**
> PicklistResponse get_connection_picklist(connection_id, picklist_request)

Get picklist values

Obtains a list of picklist values for a specified connection in a workspace.
This endpoint allows you to retrieve dynamic lists of values that can be
used in forms or dropdowns for the connected application.


### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform_cli.client.workato_api
from workato_platform_cli.client.workato_api.models.picklist_request import PicklistRequest
from workato_platform_cli.client.workato_api.models.picklist_response import PicklistResponse
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
    api_instance = workato_platform_cli.client.workato_api.ConnectionsApi(api_client)
    connection_id = 56 # int | ID of the connection. This can be found in the URL of the app connection or is the result of the List connections endpoint. 
    picklist_request = workato_platform_cli.client.workato_api.PicklistRequest() # PicklistRequest | 

    try:
        # Get picklist values
        api_response = await api_instance.get_connection_picklist(connection_id, picklist_request)
        print("The response of ConnectionsApi->get_connection_picklist:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConnectionsApi->get_connection_picklist: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connection_id** | **int**| ID of the connection. This can be found in the URL of the app connection or is the result of the List connections endpoint.  | 
 **picklist_request** | [**PicklistRequest**](PicklistRequest.md)|  | 

### Return type

[**PicklistResponse**](PicklistResponse.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Picklist values retrieved successfully |  -  |
**400** | Bad request |  -  |
**401** | Authentication required |  -  |
**404** | Connection not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_connections**
> List[Connection] list_connections(folder_id=folder_id, parent_id=parent_id, external_id=external_id, include_runtime_connections=include_runtime_connections, includes=includes)

List connections

Returns all connections and associated data for the authenticated user

### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform_cli.client.workato_api
from workato_platform_cli.client.workato_api.models.connection import Connection
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
    api_instance = workato_platform_cli.client.workato_api.ConnectionsApi(api_client)
    folder_id = 56 # int | Folder ID of the connection (optional)
    parent_id = 56 # int | Parent ID of the connection (must be same provider) (optional)
    external_id = 'external_id_example' # str | External identifier for the connection (optional)
    include_runtime_connections = True # bool | When \"true\", include all runtime user connections (optional)
    includes = ['includes_example'] # List[str] | Additional fields to include (e.g., tags) (optional)

    try:
        # List connections
        api_response = await api_instance.list_connections(folder_id=folder_id, parent_id=parent_id, external_id=external_id, include_runtime_connections=include_runtime_connections, includes=includes)
        print("The response of ConnectionsApi->list_connections:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConnectionsApi->list_connections: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **folder_id** | **int**| Folder ID of the connection | [optional] 
 **parent_id** | **int**| Parent ID of the connection (must be same provider) | [optional] 
 **external_id** | **str**| External identifier for the connection | [optional] 
 **include_runtime_connections** | **bool**| When \&quot;true\&quot;, include all runtime user connections | [optional] 
 **includes** | [**List[str]**](str.md)| Additional fields to include (e.g., tags) | [optional] 

### Return type

[**List[Connection]**](Connection.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of connections retrieved successfully |  -  |
**401** | Authentication required |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_connection**
> Connection update_connection(connection_id, connection_update_request=connection_update_request)

Update a connection

Updates a connection in a non-embedded workspace. Allows updating connection
metadata and parameters without requiring full re-creation.


### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform_cli.client.workato_api
from workato_platform_cli.client.workato_api.models.connection import Connection
from workato_platform_cli.client.workato_api.models.connection_update_request import ConnectionUpdateRequest
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
    api_instance = workato_platform_cli.client.workato_api.ConnectionsApi(api_client)
    connection_id = 56 # int | The ID of the connection
    connection_update_request = workato_platform_cli.client.workato_api.ConnectionUpdateRequest() # ConnectionUpdateRequest |  (optional)

    try:
        # Update a connection
        api_response = await api_instance.update_connection(connection_id, connection_update_request=connection_update_request)
        print("The response of ConnectionsApi->update_connection:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConnectionsApi->update_connection: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connection_id** | **int**| The ID of the connection | 
 **connection_update_request** | [**ConnectionUpdateRequest**](ConnectionUpdateRequest.md)|  | [optional] 

### Return type

[**Connection**](Connection.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Connection updated successfully |  -  |
**400** | Bad request |  -  |
**401** | Authentication required |  -  |
**404** | Connection not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

