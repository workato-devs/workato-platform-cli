# workato_platform_cli.client.workato_api.ExportApi

All URIs are relative to *https://www.workato.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_export_manifest**](ExportApi.md#create_export_manifest) | **POST** /api/export_manifests | Create an export manifest
[**list_assets_in_folder**](ExportApi.md#list_assets_in_folder) | **GET** /api/export_manifests/folder_assets | View assets in a folder


# **create_export_manifest**
> ExportManifestResponse create_export_manifest(create_export_manifest_request)

Create an export manifest

Create an export manifest for exporting assets

### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform_cli.client.workato_api
from workato_platform_cli.client.workato_api.models.create_export_manifest_request import CreateExportManifestRequest
from workato_platform_cli.client.workato_api.models.export_manifest_response import ExportManifestResponse
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
    api_instance = workato_platform_cli.client.workato_api.ExportApi(api_client)
    create_export_manifest_request = workato_platform_cli.client.workato_api.CreateExportManifestRequest() # CreateExportManifestRequest | 

    try:
        # Create an export manifest
        api_response = await api_instance.create_export_manifest(create_export_manifest_request)
        print("The response of ExportApi->create_export_manifest:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExportApi->create_export_manifest: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_export_manifest_request** | [**CreateExportManifestRequest**](CreateExportManifestRequest.md)|  | 

### Return type

[**ExportManifestResponse**](ExportManifestResponse.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Export manifest created successfully |  -  |
**400** | Bad request |  -  |
**401** | Authentication required |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_assets_in_folder**
> FolderAssetsResponse list_assets_in_folder(folder_id=folder_id, include_test_cases=include_test_cases, include_data=include_data)

View assets in a folder

View assets in a folder. Useful for creating or updating export manifests.


### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform_cli.client.workato_api
from workato_platform_cli.client.workato_api.models.folder_assets_response import FolderAssetsResponse
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
    api_instance = workato_platform_cli.client.workato_api.ExportApi(api_client)
    folder_id = 56 # int | The ID of the folder containing the assets (optional)
    include_test_cases = False # bool | Include test cases (currently not supported) (optional) (default to False)
    include_data = False # bool | Include data from the list of assets (optional) (default to False)

    try:
        # View assets in a folder
        api_response = await api_instance.list_assets_in_folder(folder_id=folder_id, include_test_cases=include_test_cases, include_data=include_data)
        print("The response of ExportApi->list_assets_in_folder:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExportApi->list_assets_in_folder: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **folder_id** | **int**| The ID of the folder containing the assets | [optional] 
 **include_test_cases** | **bool**| Include test cases (currently not supported) | [optional] [default to False]
 **include_data** | **bool**| Include data from the list of assets | [optional] [default to False]

### Return type

[**FolderAssetsResponse**](FolderAssetsResponse.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Folder assets retrieved successfully |  -  |
**401** | Authentication required |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

