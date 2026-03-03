# E2E Test Development Status

## Current Status: 81.5% Pass Rate

### Latest Test Results (March 2026)

| Category | Count | Percentage |
|----------|-------|------------|
| Passing | 22 | 81.5% |
| Failed | 5 | 18.5% |
| Critical Failures | 0 | 0% |

### ✅ Passing Commands (22)
- `workato --version`
- `workato --help`
- `workato pull`
- `workato push`
- `workato push --restart-recipes`
- `workato workspace`
- `workato assets`
- `workato profiles list`
- `workato profiles show default`
- `workato profiles status`
- `workato project list`
- `workato properties list --prefix test`
- `workato data-tables list`
- `workato connections list`
- `workato connections list --provider salesforce`
- `workato recipes list`
- `workato recipes list --since-id 1`
- `workato recipes list --running`
- `workato connectors list`
- `workato connectors list --custom`
- `workato guide topics`
- `workato guide index`

### ❌ Failing Commands (5)

| Command | Issue | Priority |
|---------|-------|----------|
| `workato init` (interactive) | Expected - requires user input | Low |
| `workato init --non-interactive` | Test config mismatch (preview vs trial) | Medium |
| `workato assets --folder-id 86384` | Invalid folder ID for test workspace | Low |
| `workato api-collections list` | Bug: Pydantic validation - `project_id` is None | High |
| `workato api-clients list` | Bug: Pydantic validation - `api_policies` is None | High |

## Known Bugs Found

### 1. api-collections list - ValidationError
```
ValidationError: 1 validation error for ApiCollection
project_id
  Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]
```
The API returns `null` for `project_id` but the model expects a string.

### 2. api-clients list - ValidationError
```
ValidationError: 1 validation error for ApiClient
api_policies
  Input should be a valid list [type=list_type, input_value=None, input_type=NoneType]
```
The API returns `null` for `api_policies` but the model expects a list.

## Next Steps

1. **Fix Pydantic Models** - Make `project_id` and `api_policies` optional
2. **Update Test Commands** - Remove invalid folder ID, fix init test config
3. **Add More Coverage** - Expand test matrix for edge cases

## Running Tests

```bash
# Set environment variables
export $(cat .env | xargs)

# Run e2e tests
uv run python tests/e2e/test_e2e.py
```

Required environment variables:
- `WORKATO_API_TOKEN` - API token for authentication
- `WORKATO_API_HOST` (optional) - API host URL
