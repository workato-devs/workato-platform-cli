# workato_platform.client.workato_api.ProjectsApi

All URIs are relative to *https://www.workato.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_project**](ProjectsApi.md#delete_project) | **DELETE** /api/projects/{project_id} | Delete a project
[**list_projects**](ProjectsApi.md#list_projects) | **GET** /api/projects | List projects


# **delete_project**
> SuccessResponse delete_project(project_id)

Delete a project

Delete a project and all of its contents. This includes all child folders,
recipes, connections, and Workflow apps assets inside the project.


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
    api_instance = workato_platform.client.workato_api.ProjectsApi(api_client)
    project_id = 56 # int | The ID of the project to delete

    try:
        # Delete a project
        api_response = await api_instance.delete_project(project_id)
        print("The response of ProjectsApi->delete_project:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectsApi->delete_project: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **int**| The ID of the project to delete | 

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
**200** | Project deleted successfully |  -  |
**401** | Authentication required |  -  |
**403** | Permission denied |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_projects**
> List[Project] list_projects(page=page, per_page=per_page)

List projects

Returns a list of projects belonging to the authenticated user with pagination support

### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform.client.workato_api
from workato_platform.client.workato_api.models.project import Project
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
    api_instance = workato_platform.client.workato_api.ProjectsApi(api_client)
    page = 1 # int | Page number (optional) (default to 1)
    per_page = 100 # int | Number of projects per page (optional) (default to 100)

    try:
        # List projects
        api_response = await api_instance.list_projects(page=page, per_page=per_page)
        print("The response of ProjectsApi->list_projects:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectsApi->list_projects: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int**| Page number | [optional] [default to 1]
 **per_page** | **int**| Number of projects per page | [optional] [default to 100]

### Return type

[**List[Project]**](Project.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of projects retrieved successfully |  -  |
**401** | Authentication required |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

