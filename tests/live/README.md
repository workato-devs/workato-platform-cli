# Live Tests (Sandbox Only)

These tests hit real Workato APIs. Run only against sandbox/trial environments.

## Required Environment Variables
- `WORKATO_HOST`
- `WORKATO_API_TOKEN`
- `WORKATO_LIVE_SANDBOX=1` (explicit confirmation)

## Optional Environment Variables
- `WORKATO_TEST_PROJECT_ID` or `WORKATO_TEST_PROJECT_NAME`
- `WORKATO_TEST_PROFILE` (default: `live-test`)
- `WORKATO_LIVE_ALLOW_PUSH=1` (enable `workato push`)
- `WORKATO_TEST_RECIPE_ID` (enable recipe start/stop)
- `WORKATO_LIVE_ALLOW_RECIPE_CONTROL=1` (enable recipe start/stop)
- `WORKATO_TEST_CONNECTION_ID` (enable OAuth URL and pick-list tests)
- `WORKATO_TEST_PICKLIST_NAME` (enable pick-list test)

## Run
```bash
WORKATO_LIVE_SANDBOX=1 make test-live
```

## Safety Notes
- Destructive actions are opt-in.
- Project creation test skips if the token lacks permissions.
