# workato_platform_cli.client.workato_api.PackagesApi

All URIs are relative to *https://www.workato.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**download_package**](PackagesApi.md#download_package) | **GET** /api/packages/{package_id}/download | Download package
[**export_package**](PackagesApi.md#export_package) | **POST** /api/packages/export/{id} | Export a package based on a manifest
[**get_package**](PackagesApi.md#get_package) | **GET** /api/packages/{package_id} | Get package details
[**import_package**](PackagesApi.md#import_package) | **POST** /api/packages/import/{id} | Import a package into a folder


# **download_package**
> bytearray download_package(package_id)

Download package

Downloads a package. Returns a redirect to the package content or the binary content directly.
Use the -L flag in cURL to follow redirects.


### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform_cli.client.workato_api
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
    api_instance = workato_platform_cli.client.workato_api.PackagesApi(api_client)
    package_id = 56 # int | Package ID

    try:
        # Download package
        api_response = await api_instance.download_package(package_id)
        print("The response of PackagesApi->download_package:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PackagesApi->download_package: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **package_id** | **int**| Package ID | 

### Return type

**bytearray**

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/zip, application/octet-stream, application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Package binary content |  -  |
**302** | Redirect to package download |  * Location - URL to download the package content <br>  |
**401** | Authentication required |  -  |
**404** | Package not found or doesn&#39;t have content |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **export_package**
> PackageResponse export_package(id)

Export a package based on a manifest

Export a package based on a manifest.

**ENDPOINT PRIVILEGES ALSO PROVIDE ACCESS TO ASSETS**

When you provide an API client with privileges to this endpoint, the API client
is also granted the ability to view other assets like recipes, lookup tables,
Event topics, and message templates by examining the resulting zip file.

This is an asynchronous request. Use GET package by ID endpoint to get details
of the exported package.

**INCLUDE TAGS WHEN CREATING THE EXPORT MANIFEST**

To include tags in the exported package, set the include_tags attribute to true
when calling the Create an export manifest endpoint.


### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform_cli.client.workato_api
from workato_platform_cli.client.workato_api.models.package_response import PackageResponse
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
    api_instance = workato_platform_cli.client.workato_api.PackagesApi(api_client)
    id = 'id_example' # str | Export manifest ID

    try:
        # Export a package based on a manifest
        api_response = await api_instance.export_package(id)
        print("The response of PackagesApi->export_package:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PackagesApi->export_package: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Export manifest ID | 

### Return type

[**PackageResponse**](PackageResponse.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Export package creation triggered successfully |  -  |
**401** | Authentication required |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_package**
> PackageDetailsResponse get_package(package_id)

Get package details

Get details of an imported or exported package including status

### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform_cli.client.workato_api
from workato_platform_cli.client.workato_api.models.package_details_response import PackageDetailsResponse
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
    api_instance = workato_platform_cli.client.workato_api.PackagesApi(api_client)
    package_id = 56 # int | Package ID

    try:
        # Get package details
        api_response = await api_instance.get_package(package_id)
        print("The response of PackagesApi->get_package:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PackagesApi->get_package: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **package_id** | **int**| Package ID | 

### Return type

[**PackageDetailsResponse**](PackageDetailsResponse.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Package details retrieved successfully |  -  |
**401** | Authentication required |  -  |
**404** | Package not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **import_package**
> PackageResponse import_package(id, body, restart_recipes=restart_recipes, include_tags=include_tags, folder_id_for_home_assets=folder_id_for_home_assets)

Import a package into a folder

Import a package in zip file format into a folder. This endpoint allows an API client
to create or update assets, such as recipes, lookup tables, event topics, and message
templates, through package imports.

This is an asynchronous request. Use GET package by ID endpoint to get details of
the imported package.

The input (zip file) is an application/octet-stream payload containing package content.


### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform_cli.client.workato_api
from workato_platform_cli.client.workato_api.models.package_response import PackageResponse
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
    api_instance = workato_platform_cli.client.workato_api.PackagesApi(api_client)
    id = 56 # int | Folder ID
    body = None # bytearray | 
    restart_recipes = False # bool | Value must be true to allow the restarting of running recipes during import. Packages cannot be imported if there are running recipes and this parameter equals false or is not provided.  (optional) (default to False)
    include_tags = False # bool | Specifies whether to preserve tags assigned to assets when the package is imported into the folder. Tags are excluded from the import when set to false.  (optional) (default to False)
    folder_id_for_home_assets = 56 # int | The ID of a folder to store assets in instead of the root folder. The folder specified must be accessible to the API client and cannot be the root folder. This parameter is conditionally required if you are importing a package that contains root folder assets and your workspace Home assets folder has been converted to a Home assets project.  (optional)

    try:
        # Import a package into a folder
        api_response = await api_instance.import_package(id, body, restart_recipes=restart_recipes, include_tags=include_tags, folder_id_for_home_assets=folder_id_for_home_assets)
        print("The response of PackagesApi->import_package:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PackagesApi->import_package: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**| Folder ID | 
 **body** | **bytearray**|  | 
 **restart_recipes** | **bool**| Value must be true to allow the restarting of running recipes during import. Packages cannot be imported if there are running recipes and this parameter equals false or is not provided.  | [optional] [default to False]
 **include_tags** | **bool**| Specifies whether to preserve tags assigned to assets when the package is imported into the folder. Tags are excluded from the import when set to false.  | [optional] [default to False]
 **folder_id_for_home_assets** | **int**| The ID of a folder to store assets in instead of the root folder. The folder specified must be accessible to the API client and cannot be the root folder. This parameter is conditionally required if you are importing a package that contains root folder assets and your workspace Home assets folder has been converted to a Home assets project.  | [optional] 

### Return type

[**PackageResponse**](PackageResponse.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: application/octet-stream
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Package import initiated successfully |  -  |
**400** | Bad request |  -  |
**401** | Authentication required |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

