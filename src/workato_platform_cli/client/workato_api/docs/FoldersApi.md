# workato_platform_cli.client.workato_api.FoldersApi

All URIs are relative to *https://www.workato.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_folder**](FoldersApi.md#create_folder) | **POST** /api/folders | Create a folder
[**list_folders**](FoldersApi.md#list_folders) | **GET** /api/folders | List folders


# **create_folder**
> FolderCreationResponse create_folder(create_folder_request)

Create a folder

Creates a new folder in the specified parent folder. If no parent folder ID
is specified, creates the folder as a top-level folder in the home folder.


### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform_cli.client.workato_api
from workato_platform_cli.client.workato_api.models.create_folder_request import CreateFolderRequest
from workato_platform_cli.client.workato_api.models.folder_creation_response import FolderCreationResponse
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
    api_instance = workato_platform_cli.client.workato_api.FoldersApi(api_client)
    create_folder_request = workato_platform_cli.client.workato_api.CreateFolderRequest() # CreateFolderRequest | 

    try:
        # Create a folder
        api_response = await api_instance.create_folder(create_folder_request)
        print("The response of FoldersApi->create_folder:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FoldersApi->create_folder: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_folder_request** | [**CreateFolderRequest**](CreateFolderRequest.md)|  | 

### Return type

[**FolderCreationResponse**](FolderCreationResponse.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Folder created successfully |  -  |
**400** | Bad request |  -  |
**401** | Authentication required |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_folders**
> List[Folder] list_folders(parent_id=parent_id, page=page, per_page=per_page)

List folders

Lists all folders.

### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform_cli.client.workato_api
from workato_platform_cli.client.workato_api.models.folder import Folder
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
    api_instance = workato_platform_cli.client.workato_api.FoldersApi(api_client)
    parent_id = 56 # int | Parent folder ID. Defaults to Home folder. (optional)
    page = 1 # int | Page number. Defaults to 1. (optional) (default to 1)
    per_page = 100 # int | Page size. Defaults to 100 (maximum is 100). (optional) (default to 100)

    try:
        # List folders
        api_response = await api_instance.list_folders(parent_id=parent_id, page=page, per_page=per_page)
        print("The response of FoldersApi->list_folders:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FoldersApi->list_folders: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **parent_id** | **int**| Parent folder ID. Defaults to Home folder. | [optional] 
 **page** | **int**| Page number. Defaults to 1. | [optional] [default to 1]
 **per_page** | **int**| Page size. Defaults to 100 (maximum is 100). | [optional] [default to 100]

### Return type

[**List[Folder]**](Folder.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of folders retrieved successfully |  -  |
**401** | Authentication required |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

