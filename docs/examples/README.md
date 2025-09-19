# Recipe Examples

Sample recipe files demonstrating common integration patterns for real-world scenarios.

## Available Examples

All examples are now **CLI-compatible** and ready for deployment. Each recipe follows proper CLI structure with required fields and correct data pill syntax.

### Basic Patterns

### [basic-sync-recipe.json](basic-sync-recipe.json)
**Pattern:** Real-time data synchronization  
**Use Case:** Sync Salesforce contacts to database  
**Key Features:**
- Object trigger (new/updated records)
- Database upsert operation
- Field mapping and transformation

### [webhook-api-recipe.json](webhook-api-recipe.json)
**Pattern:** Webhook processing with API calls  
**Use Case:** Process incoming orders and notify external systems  
**Key Features:**
- Webhook trigger
- HTTP API calls with authentication
- Email notifications

### [batch-processing-recipe.json](batch-processing-recipe.json)
**Pattern:** Scheduled batch processing  
**Use Case:** Daily customer data sync with error handling  
**Key Features:**
- Scheduled trigger
- Batch processing with loops
- Error handling and notifications

### Advanced Patterns

### [advanced-data-transformation-recipe.json](advanced-data-transformation-recipe.json)
**Pattern:** Complex data transformation and cleansing  
**Use Case:** Transform and enrich Salesforce account data with quality scoring  
**Key Features:**
- Advanced field transformations (phone formatting, address parsing)
- Data quality scoring and conditional processing
- Revenue/employee tier categorization
- Dual-path processing (high quality vs issues)

### [multi-application-workflow-recipe.json](multi-application-workflow-recipe.json)
**Pattern:** Multi-system workflow orchestration  
**Use Case:** Support ticket workflow from Salesforce to Slack to Jira  
**Key Features:**
- Cross-platform workflow (Salesforce → Slack → Jira → Email)
- Priority-based conditional routing
- Enterprise account escalation logic
- Automatic ticket creation and linking

### [file-processing-recipe.json](file-processing-recipe.json)
**Pattern:** File processing with validation pipeline  
**Use Case:** Process CSV files from SFTP with comprehensive validation  
**Key Features:**
- SFTP file monitoring and processing
- Row-by-row data validation and cleansing
- File archiving and error reporting
- Size limits and processing controls

### [real-time-bidirectional-sync-recipe.json](real-time-bidirectional-sync-recipe.json)
**Pattern:** Bidirectional synchronization with conflict resolution  
**Use Case:** Real-time sync between Salesforce and HubSpot contacts  
**Key Features:**
- Sync loop prevention and timestamp comparison
- Conflict detection and automatic resolution
- Orphaned record linking and duplicate handling
- Manual intervention workflows for complex conflicts

### [api-first-integration-recipe.json](api-first-integration-recipe.json)
**Pattern:** Enterprise API integration with resilience patterns  
**Use Case:** Paginated API consumption with rate limiting and circuit breakers  
**Key Features:**
- Pagination handling with state management
- Rate limiting compliance and backoff strategies
- Circuit breaker pattern for API failures
- Comprehensive error logging and monitoring

## Using These Examples

### Validate Recipes

All examples are now CLI-compatible and will pass validation:

```bash
# ✅ These will work - all examples are now CLI-compatible
workato recipes validate --path examples/basic-sync-recipe.json
workato recipes validate --path examples/advanced-data-transformation-recipe.json
workato recipes validate --path examples/multi-application-workflow-recipe.json
workato recipes validate --path examples/file-processing-recipe.json
workato recipes validate --path examples/real-time-bidirectional-sync-recipe.json
workato recipes validate --path examples/api-first-integration-recipe.json
workato recipes validate --path examples/webhook-api-recipe.json
workato recipes validate --path examples/batch-processing-recipe.json
```

### Deploy Recipes

1. Copy the recipe file to your project directory
2. Update connection references to match your connections
3. Customize field mappings and business logic
4. Push to Workato:
```bash
workato push
```

### Customize for Your Use Case

#### Basic Customizations
1. **Update identifiers:** Change `name` and `description` fields
2. **Connection providers:** Update connection names in the `config` section
3. **Field mappings:** Adjust data pill references using proper step aliases
4. **Business logic:** Modify conditional statements and transformations

#### Advanced Customizations
1. **Error handling:** Adjust retry counts, timeout values, and notification channels
2. **Data validation:** Modify validation rules and quality scoring logic
3. **Integration patterns:** Adapt workflow routing and escalation rules
4. **Performance tuning:** Adjust batch sizes, rate limits, and processing thresholds

### Recipe Selection Guide

**Choose recipes based on your integration needs:**

| Use Case | Recommended Recipe | Key Benefits |
|----------|-------------------|--------------|
| Simple sync between systems | `basic-sync-recipe.json` | Quick setup, reliable pattern |
| Process incoming webhooks | `webhook-api-recipe.json` | Event-driven, scalable |
| Scheduled data processing | `batch-processing-recipe.json` | Bulk operations, error handling |
| Complex data transformations | `advanced-data-transformation-recipe.json` | Data quality, conditional logic |
| Multi-system workflows | `multi-application-workflow-recipe.json` | Orchestration, escalation |
| File-based integrations | `file-processing-recipe.json` | Validation, error tracking |
| Bidirectional sync | `real-time-bidirectional-sync-recipe.json` | Conflict resolution, loop prevention |
| Enterprise API consumption | `api-first-integration-recipe.json` | Resilience, rate limiting |

## Recipe Structure

All CLI-compatible Workato recipes follow this structure:

```json
{
  "name": "Recipe Name",
  "description": "What this recipe does",
  "version": 3,
  "private": true,
  "concurrency": 1,
  "code": {
    "number": 0,
    "provider": "app_name",
    "name": "trigger_type",
    "as": "trigger_alias",
    "keyword": "trigger",
    "input": { /* trigger configuration */ },
    "block": [
      {
        "number": 1,
        "provider": "app_name",
        "name": "action_type",
        "as": "action_alias",
        "keyword": "action",
        "uuid": "unique-id-here",
        "input": { /* action configuration */ }
      }
    ],
    "uuid": "trigger-uuid-here",
    "unfinished": false
  },
  "config": [
    {
      "keyword": "application",
      "provider": "app_name",
      "skip_validation": false,
      "account_id": {
        "zip_name": "connection.json",
        "name": "connection_name",
        "folder": ""
      }
    }
  ]
}
```

## Data Pills and References

Use proper CLI data pill syntax:

- **=_('data.provider.step_alias.field')** - Reference step output using aliases
- **=_('job.started_at')** - Job metadata like timestamps
- **=_('connections.name.token')** - Reference connection credentials

## Next Steps

- See [COMMAND_REFERENCE.md](../COMMAND_REFERENCE.md) for all CLI commands
- See [USE_CASES.md](../USE_CASES.md) for more complex scenarios
- Visit [Workato Docs](https://docs.workato.com) for complete recipe reference