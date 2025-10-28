# workato_platform.client.workato_api.DataTablesApi

All URIs are relative to *https://www.workato.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_data_table**](DataTablesApi.md#create_data_table) | **POST** /api/data_tables | Create data table
[**list_data_tables**](DataTablesApi.md#list_data_tables) | **GET** /api/data_tables | List data tables


# **create_data_table**
> DataTableCreateResponse create_data_table(data_table_create_request)

Create data table

Creates a data table in a folder you specify

### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform.client.workato_api
from workato_platform.client.workato_api.models.data_table_create_request import DataTableCreateRequest
from workato_platform.client.workato_api.models.data_table_create_response import DataTableCreateResponse
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
    api_instance = workato_platform.client.workato_api.DataTablesApi(api_client)
    data_table_create_request = workato_platform.client.workato_api.DataTableCreateRequest() # DataTableCreateRequest | 

    try:
        # Create data table
        api_response = await api_instance.create_data_table(data_table_create_request)
        print("The response of DataTablesApi->create_data_table:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataTablesApi->create_data_table: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **data_table_create_request** | [**DataTableCreateRequest**](DataTableCreateRequest.md)|  | 

### Return type

[**DataTableCreateResponse**](DataTableCreateResponse.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Data table created successfully |  -  |
**400** | Bad request |  -  |
**401** | Authentication required |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_data_tables**
> DataTableListResponse list_data_tables(page=page, per_page=per_page)

List data tables

Returns a list of all data tables in your workspace

### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform.client.workato_api
from workato_platform.client.workato_api.models.data_table_list_response import DataTableListResponse
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
    api_instance = workato_platform.client.workato_api.DataTablesApi(api_client)
    page = 1 # int | Page number of the data tables to fetch (optional) (default to 1)
    per_page = 100 # int | Page size (max 100) (optional) (default to 100)

    try:
        # List data tables
        api_response = await api_instance.list_data_tables(page=page, per_page=per_page)
        print("The response of DataTablesApi->list_data_tables:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataTablesApi->list_data_tables: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int**| Page number of the data tables to fetch | [optional] [default to 1]
 **per_page** | **int**| Page size (max 100) | [optional] [default to 100]

### Return type

[**DataTableListResponse**](DataTableListResponse.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Data tables retrieved successfully |  -  |
**401** | Authentication required |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

