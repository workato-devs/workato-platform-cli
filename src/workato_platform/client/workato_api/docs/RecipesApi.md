# workato_platform.client.workato_api.RecipesApi

All URIs are relative to *https://www.workato.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_recipes**](RecipesApi.md#list_recipes) | **GET** /api/recipes | List recipes
[**start_recipe**](RecipesApi.md#start_recipe) | **PUT** /api/recipes/{recipe_id}/start | Start a recipe
[**stop_recipe**](RecipesApi.md#stop_recipe) | **PUT** /api/recipes/{recipe_id}/stop | Stop a recipe
[**update_recipe_connection**](RecipesApi.md#update_recipe_connection) | **PUT** /api/recipes/{recipe_id}/connect | Update a connection for a recipe


# **list_recipes**
> RecipeListResponse list_recipes(adapter_names_all=adapter_names_all, adapter_names_any=adapter_names_any, folder_id=folder_id, order=order, page=page, per_page=per_page, running=running, since_id=since_id, stopped_after=stopped_after, stop_cause=stop_cause, updated_after=updated_after, includes=includes, exclude_code=exclude_code)

List recipes

Returns a list of recipes belonging to the authenticated user.
Recipes are returned in descending ID order.


### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform.client.workato_api
from workato_platform.client.workato_api.models.recipe_list_response import RecipeListResponse
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
    api_instance = workato_platform.client.workato_api.RecipesApi(api_client)
    adapter_names_all = 'adapter_names_all_example' # str | Comma-separated adapter names (recipes must use ALL) (optional)
    adapter_names_any = 'adapter_names_any_example' # str | Comma-separated adapter names (recipes must use ANY) (optional)
    folder_id = 56 # int | Return recipes in specified folder (optional)
    order = 'order_example' # str | Set ordering method (optional)
    page = 1 # int | Page number (optional) (default to 1)
    per_page = 100 # int | Number of recipes per page (optional) (default to 100)
    running = True # bool | If true, returns only running recipes (optional)
    since_id = 56 # int | Return recipes with IDs lower than this value (optional)
    stopped_after = '2013-10-20T19:20:30+01:00' # datetime | Exclude recipes stopped after this date (ISO 8601 format) (optional)
    stop_cause = 'stop_cause_example' # str | Filter by stop reason (optional)
    updated_after = '2013-10-20T19:20:30+01:00' # datetime | Include recipes updated after this date (ISO 8601 format) (optional)
    includes = ['includes_example'] # List[str] | Additional fields to include (e.g., tags) (optional)
    exclude_code = True # bool | Exclude recipe code from response for better performance (optional)

    try:
        # List recipes
        api_response = await api_instance.list_recipes(adapter_names_all=adapter_names_all, adapter_names_any=adapter_names_any, folder_id=folder_id, order=order, page=page, per_page=per_page, running=running, since_id=since_id, stopped_after=stopped_after, stop_cause=stop_cause, updated_after=updated_after, includes=includes, exclude_code=exclude_code)
        print("The response of RecipesApi->list_recipes:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RecipesApi->list_recipes: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **adapter_names_all** | **str**| Comma-separated adapter names (recipes must use ALL) | [optional] 
 **adapter_names_any** | **str**| Comma-separated adapter names (recipes must use ANY) | [optional] 
 **folder_id** | **int**| Return recipes in specified folder | [optional] 
 **order** | **str**| Set ordering method | [optional] 
 **page** | **int**| Page number | [optional] [default to 1]
 **per_page** | **int**| Number of recipes per page | [optional] [default to 100]
 **running** | **bool**| If true, returns only running recipes | [optional] 
 **since_id** | **int**| Return recipes with IDs lower than this value | [optional] 
 **stopped_after** | **datetime**| Exclude recipes stopped after this date (ISO 8601 format) | [optional] 
 **stop_cause** | **str**| Filter by stop reason | [optional] 
 **updated_after** | **datetime**| Include recipes updated after this date (ISO 8601 format) | [optional] 
 **includes** | [**List[str]**](str.md)| Additional fields to include (e.g., tags) | [optional] 
 **exclude_code** | **bool**| Exclude recipe code from response for better performance | [optional] 

### Return type

[**RecipeListResponse**](RecipeListResponse.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of recipes retrieved successfully |  -  |
**401** | Authentication required |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **start_recipe**
> RecipeStartResponse start_recipe(recipe_id)

Start a recipe

Starts a recipe specified by recipe ID

### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform.client.workato_api
from workato_platform.client.workato_api.models.recipe_start_response import RecipeStartResponse
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
    api_instance = workato_platform.client.workato_api.RecipesApi(api_client)
    recipe_id = 56 # int | Recipe ID

    try:
        # Start a recipe
        api_response = await api_instance.start_recipe(recipe_id)
        print("The response of RecipesApi->start_recipe:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RecipesApi->start_recipe: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **recipe_id** | **int**| Recipe ID | 

### Return type

[**RecipeStartResponse**](RecipeStartResponse.md)

### Authorization

[BearerAuth](../README.md#BearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Recipe start response (success or validation failure) |  -  |
**400** | Bad request (OEM adapter usage limit or state transition error) |  -  |
**401** | Authentication required |  -  |
**422** | Unprocessable entity (webhook registration error) |  -  |
**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **stop_recipe**
> SuccessResponse stop_recipe(recipe_id)

Stop a recipe

Stops a recipe specified by recipe ID

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
    api_instance = workato_platform.client.workato_api.RecipesApi(api_client)
    recipe_id = 56 # int | Recipe ID

    try:
        # Stop a recipe
        api_response = await api_instance.stop_recipe(recipe_id)
        print("The response of RecipesApi->stop_recipe:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RecipesApi->stop_recipe: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **recipe_id** | **int**| Recipe ID | 

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
**200** | Recipe stopped successfully |  -  |
**400** | Bad request (state transition error or recipe cannot be stopped) |  -  |
**401** | Authentication required |  -  |
**404** | Recipe not found |  -  |
**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_recipe_connection**
> SuccessResponse update_recipe_connection(recipe_id, recipe_connection_update_request)

Update a connection for a recipe

Updates the chosen connection for a specific connector in a stopped recipe.


### Example

* Bearer Authentication (BearerAuth):

```python
import workato_platform.client.workato_api
from workato_platform.client.workato_api.models.recipe_connection_update_request import RecipeConnectionUpdateRequest
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
    api_instance = workato_platform.client.workato_api.RecipesApi(api_client)
    recipe_id = 56 # int | ID of the recipe
    recipe_connection_update_request = workato_platform.client.workato_api.RecipeConnectionUpdateRequest() # RecipeConnectionUpdateRequest | 

    try:
        # Update a connection for a recipe
        api_response = await api_instance.update_recipe_connection(recipe_id, recipe_connection_update_request)
        print("The response of RecipesApi->update_recipe_connection:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RecipesApi->update_recipe_connection: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **recipe_id** | **int**| ID of the recipe | 
 **recipe_connection_update_request** | [**RecipeConnectionUpdateRequest**](RecipeConnectionUpdateRequest.md)|  | 

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
**200** | Connection updated successfully |  -  |
**400** | Bad request (recipe is running or invalid parameters) |  -  |
**401** | Authentication required |  -  |
**403** | Forbidden (no permission to update this recipe) |  -  |
**404** | Recipe not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

