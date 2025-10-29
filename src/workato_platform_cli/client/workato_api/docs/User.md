# User


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**name** | **str** |  | 
**created_at** | **datetime** |  | 
**plan_id** | **str** |  | 
**current_billing_period_start** | **datetime** |  | 
**current_billing_period_end** | **datetime** |  | 
**expert** | **bool** |  | [optional] 
**avatar_url** | **str** |  | [optional] 
**recipes_count** | **int** |  | 
**interested_applications** | **List[str]** |  | [optional] 
**company_name** | **str** |  | 
**location** | **str** |  | 
**last_seen** | **datetime** |  | 
**contact_phone** | **str** |  | [optional] 
**contact_email** | **str** |  | [optional] 
**about_me** | **str** |  | [optional] 
**email** | **str** |  | 
**phone** | **str** |  | [optional] 
**active_recipes_count** | **int** |  | 
**root_folder_id** | **int** |  | 

## Example

```python
from workato_platform_cli.client.workato_api.models.user import User

# TODO update the JSON string below
json = "{}"
# create an instance of User from a JSON string
user_instance = User.from_json(json)
# print the JSON string representation of the object
print(User.to_json())

# convert the object into a dict
user_dict = user_instance.to_dict()
# create an instance of User from a dict
user_from_dict = User.from_dict(user_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


