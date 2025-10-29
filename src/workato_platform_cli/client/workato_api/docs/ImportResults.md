# ImportResults


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | 
**total_endpoints** | **int** |  | 
**failed_endpoints** | **int** |  | 
**failed_actions** | **List[str]** |  | 

## Example

```python
from workato_platform_cli.client.workato_api.models.import_results import ImportResults

# TODO update the JSON string below
json = "{}"
# create an instance of ImportResults from a JSON string
import_results_instance = ImportResults.from_json(json)
# print the JSON string representation of the object
print(ImportResults.to_json())

# convert the object into a dict
import_results_dict = import_results_instance.to_dict()
# create an instance of ImportResults from a dict
import_results_from_dict = ImportResults.from_dict(import_results_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


