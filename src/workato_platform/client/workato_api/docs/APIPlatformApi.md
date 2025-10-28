# workato_platform.client.workato_api.APIPlatformApi

All URIs are relative to *https://www.workato.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_api_client**](APIPlatformApi.md#create_api_client) | **POST** /api/v2/api_clients | Create API client (v2)
[**create_api_collection**](APIPlatformApi.md#create_api_collection) | **POST** /api/api_collections | Create API collection
[**create_api_key**](APIPlatformApi.md#create_api_key) | **POST** /api/v2/api_clients/{api_client_id}/api_keys | Create an API key
[**disable_api_endpoint**](APIPlatformApi.md#disable_api_endpoint) | **PUT** /api/api_endpoints/{api_endpoint_id}/disable | Disable an API endpoint
[**enable_api_endpoint**](APIPlatformApi.md#enable_api_endpoint) | **PUT** /api/api_endpoints/{api_endpoint_id}/enable | Enable an API endpoint
[**list_api_clients**](APIPlatformApi.md#list_api_clients) | **GET** /api/v2/api_clients | List API clients (v2)
[**list_api_collections**](APIPlatformApi.md#list_api_collections) | **GET** /api/api_collections | List API collections
[**list_api_endpoints**](APIPlatformApi.md#list_api_endpoints) | **GET** /api/api_endpoints | List API endpoints
[**list_api_keys**](APIPlatformApi.md#list_api_keys) | **GET** /api/v2/api_clients/{api_client_id}/api_keys | List API keys
[**refresh_api_key_secret**](APIPlatformApi.md#refresh_api_key_secret) | **PUT** /api/v2/api_clients/{api_client_id}/api_keys/{api_key_id}/refresh_secret | Refresh API key secret


# **create_api_client**
> ApiClientResponse create_api_client(api_client_create_request)

Create API client (v2)

Create a new API client within a project with various authentication methods

### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform.client.workato_api
from workato_platform.client.workato_api.models.api_client_create_request import ApiClientCreateRequest
from workato_platform.client.workato_api.models.api_client_response import ApiClientResponse
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
    api_instance = workato_platform.client.workato_api.APIPlatformApi(api_client)
    api_client_create_request = workato_platform.client.workato_api.ApiClientCreateRequest() # ApiClientCreateRequest | 

    try:
        # Create API client (v2)
        api_response = await api_instance.create_api_client(api_client_create_request)
        print("The response of APIPlatformApi->create_api_client:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling APIPlatformApi->create_api_client: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **api_client_create_request** | [**ApiClientCreateRequest**](ApiClientCreateRequest.md)|  | 

### Return type

[**ApiClientResponse**](ApiClientResponse.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | API client created successfully |  -  |
**400** | Bad request |  -  |
**401** | Authentication required |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_api_collection**
> ApiCollection create_api_collection(api_collection_create_request)

Create API collection

Create a new API collection from an OpenAPI specification.
This generates both recipes and endpoints from the provided spec.


### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform.client.workato_api
from workato_platform.client.workato_api.models.api_collection import ApiCollection
from workato_platform.client.workato_api.models.api_collection_create_request import ApiCollectionCreateRequest
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
    api_instance = workato_platform.client.workato_api.APIPlatformApi(api_client)
    api_collection_create_request = workato_platform.client.workato_api.ApiCollectionCreateRequest() # ApiCollectionCreateRequest | 

    try:
        # Create API collection
        api_response = await api_instance.create_api_collection(api_collection_create_request)
        print("The response of APIPlatformApi->create_api_collection:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling APIPlatformApi->create_api_collection: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **api_collection_create_request** | [**ApiCollectionCreateRequest**](ApiCollectionCreateRequest.md)|  | 

### Return type

[**ApiCollection**](ApiCollection.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | API collection created successfully |  -  |
**400** | Bad request |  -  |
**401** | Authentication required |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_api_key**
> ApiKeyResponse create_api_key(api_client_id, api_key_create_request)

Create an API key

Create a new API key for an API client

### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform.client.workato_api
from workato_platform.client.workato_api.models.api_key_create_request import ApiKeyCreateRequest
from workato_platform.client.workato_api.models.api_key_response import ApiKeyResponse
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
    api_instance = workato_platform.client.workato_api.APIPlatformApi(api_client)
    api_client_id = 56 # int | Specify the ID of the API client to create the API key for
    api_key_create_request = workato_platform.client.workato_api.ApiKeyCreateRequest() # ApiKeyCreateRequest | 

    try:
        # Create an API key
        api_response = await api_instance.create_api_key(api_client_id, api_key_create_request)
        print("The response of APIPlatformApi->create_api_key:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling APIPlatformApi->create_api_key: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **api_client_id** | **int**| Specify the ID of the API client to create the API key for | 
 **api_key_create_request** | [**ApiKeyCreateRequest**](ApiKeyCreateRequest.md)|  | 

### Return type

[**ApiKeyResponse**](ApiKeyResponse.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | API key created successfully |  -  |
**400** | Bad request |  -  |
**401** | Authentication required |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **disable_api_endpoint**
> SuccessResponse disable_api_endpoint(api_endpoint_id)

Disable an API endpoint

Disables an active API endpoint. The endpoint can no longer be called by a client.


### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform.client.workato_api
from workato_platform.client.workato_api.models.success_response import SuccessResponse
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
    api_instance = workato_platform.client.workato_api.APIPlatformApi(api_client)
    api_endpoint_id = 56 # int | ID of the API endpoint

    try:
        # Disable an API endpoint
        api_response = await api_instance.disable_api_endpoint(api_endpoint_id)
        print("The response of APIPlatformApi->disable_api_endpoint:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling APIPlatformApi->disable_api_endpoint: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **api_endpoint_id** | **int**| ID of the API endpoint | 

### Return type

[**SuccessResponse**](SuccessResponse.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | API endpoint disabled successfully |  -  |
**401** | Authentication required |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **enable_api_endpoint**
> SuccessResponse enable_api_endpoint(api_endpoint_id)

Enable an API endpoint

Enables an API endpoint. You must start the associated recipe to enable
the API endpoint successfully.


### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform.client.workato_api
from workato_platform.client.workato_api.models.success_response import SuccessResponse
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
    api_instance = workato_platform.client.workato_api.APIPlatformApi(api_client)
    api_endpoint_id = 56 # int | ID of the API endpoint

    try:
        # Enable an API endpoint
        api_response = await api_instance.enable_api_endpoint(api_endpoint_id)
        print("The response of APIPlatformApi->enable_api_endpoint:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling APIPlatformApi->enable_api_endpoint: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **api_endpoint_id** | **int**| ID of the API endpoint | 

### Return type

[**SuccessResponse**](SuccessResponse.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | API endpoint enabled successfully |  -  |
**401** | Authentication required |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_api_clients**
> ApiClientListResponse list_api_clients(project_id=project_id, page=page, per_page=per_page, cert_bundle_ids=cert_bundle_ids)

List API clients (v2)

List all API clients. This endpoint includes the project_id of the API client
in the response.


### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform.client.workato_api
from workato_platform.client.workato_api.models.api_client_list_response import ApiClientListResponse
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
    api_instance = workato_platform.client.workato_api.APIPlatformApi(api_client)
    project_id = 56 # int | The ID of a specific project. Retrieve a list of project IDs with the list projects endpoint (optional)
    page = 1 # int | Page number (optional) (default to 1)
    per_page = 100 # int | Page size. The maximum page size is 100 (optional) (default to 100)
    cert_bundle_ids = [56] # List[int] | Filter clients by certificate bundle IDs. Returns only clients associated with the specified certificate bundles (optional)

    try:
        # List API clients (v2)
        api_response = await api_instance.list_api_clients(project_id=project_id, page=page, per_page=per_page, cert_bundle_ids=cert_bundle_ids)
        print("The response of APIPlatformApi->list_api_clients:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling APIPlatformApi->list_api_clients: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**| The ID of a specific project. Retrieve a list of project IDs with the list projects endpoint | [optional] 
 **page** | **int**| Page number | [optional] [default to 1]
 **per_page** | **int**| Page size. The maximum page size is 100 | [optional] [default to 100]
 **cert_bundle_ids** | [**List[int]**](int.md)| Filter clients by certificate bundle IDs. Returns only clients associated with the specified certificate bundles | [optional] 

### Return type

[**ApiClientListResponse**](ApiClientListResponse.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of API clients retrieved successfully |  -  |
**401** | Authentication required |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_api_collections**
> List[ApiCollection] list_api_collections(per_page=per_page, page=page)

List API collections

List all API collections. The endpoint returns the project_id of the project
to which the collections belong in the response.


### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform.client.workato_api
from workato_platform.client.workato_api.models.api_collection import ApiCollection
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
    api_instance = workato_platform.client.workato_api.APIPlatformApi(api_client)
    per_page = 100 # int | Number of API collections to return in a single page (optional) (default to 100)
    page = 1 # int | Page number of the API collections to fetch (optional) (default to 1)

    try:
        # List API collections
        api_response = await api_instance.list_api_collections(per_page=per_page, page=page)
        print("The response of APIPlatformApi->list_api_collections:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling APIPlatformApi->list_api_collections: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **per_page** | **int**| Number of API collections to return in a single page | [optional] [default to 100]
 **page** | **int**| Page number of the API collections to fetch | [optional] [default to 1]

### Return type

[**List[ApiCollection]**](ApiCollection.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of API collections retrieved successfully |  -  |
**401** | Authentication required |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_api_endpoints**
> List[ApiEndpoint] list_api_endpoints(api_collection_id=api_collection_id, per_page=per_page, page=page)

List API endpoints

Lists all API endpoints. Specify the api_collection_id to obtain the list
of endpoints in a specific collection.


### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform.client.workato_api
from workato_platform.client.workato_api.models.api_endpoint import ApiEndpoint
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
    api_instance = workato_platform.client.workato_api.APIPlatformApi(api_client)
    api_collection_id = 56 # int | ID of the API collection. If not provided, all API endpoints are returned (optional)
    per_page = 100 # int | Number of API endpoints to return in a single page (optional) (default to 100)
    page = 1 # int | Page number of the API endpoints to fetch (optional) (default to 1)

    try:
        # List API endpoints
        api_response = await api_instance.list_api_endpoints(api_collection_id=api_collection_id, per_page=per_page, page=page)
        print("The response of APIPlatformApi->list_api_endpoints:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling APIPlatformApi->list_api_endpoints: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **api_collection_id** | **int**| ID of the API collection. If not provided, all API endpoints are returned | [optional] 
 **per_page** | **int**| Number of API endpoints to return in a single page | [optional] [default to 100]
 **page** | **int**| Page number of the API endpoints to fetch | [optional] [default to 1]

### Return type

[**List[ApiEndpoint]**](ApiEndpoint.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of API endpoints retrieved successfully |  -  |
**401** | Authentication required |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_api_keys**
> ApiKeyListResponse list_api_keys(api_client_id)

List API keys

Retrieve all API keys for an API client. Provide the api_client_id parameter
to filter keys for a specific client.


### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform.client.workato_api
from workato_platform.client.workato_api.models.api_key_list_response import ApiKeyListResponse
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
    api_instance = workato_platform.client.workato_api.APIPlatformApi(api_client)
    api_client_id = 56 # int | Filter API keys for a specific API client

    try:
        # List API keys
        api_response = await api_instance.list_api_keys(api_client_id)
        print("The response of APIPlatformApi->list_api_keys:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling APIPlatformApi->list_api_keys: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **api_client_id** | **int**| Filter API keys for a specific API client | 

### Return type

[**ApiKeyListResponse**](ApiKeyListResponse.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of API keys retrieved successfully |  -  |
**401** | Authentication required |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **refresh_api_key_secret**
> ApiKeyResponse refresh_api_key_secret(api_client_id, api_key_id)

Refresh API key secret

Refresh the authentication token or OAuth 2.0 client secret for an API key.


### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform.client.workato_api
from workato_platform.client.workato_api.models.api_key_response import ApiKeyResponse
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
    api_instance = workato_platform.client.workato_api.APIPlatformApi(api_client)
    api_client_id = 56 # int | ID of the API client that owns the API key
    api_key_id = 56 # int | ID of the API key to refresh

    try:
        # Refresh API key secret
        api_response = await api_instance.refresh_api_key_secret(api_client_id, api_key_id)
        print("The response of APIPlatformApi->refresh_api_key_secret:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling APIPlatformApi->refresh_api_key_secret: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **api_client_id** | **int**| ID of the API client that owns the API key | 
 **api_key_id** | **int**| ID of the API key to refresh | 

### Return type

[**ApiKeyResponse**](ApiKeyResponse.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | API key secret refreshed successfully |  -  |
**401** | Authentication required |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

