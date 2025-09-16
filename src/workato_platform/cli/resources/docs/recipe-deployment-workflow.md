# Recipe Deployment Workflow

This guide covers the complete end-to-end process of deploying a Workato recipe, from initial validation through successful execution.

## 🚀 Complete Workflow Overview

The recipe deployment process follows this sequence:

1. **Validate Recipe** → 2. **Check Connections** → 3. **Create Missing Connections** → 4. **Push Project** → 5. **Start Recipe** → 6. **Monitor Execution**

## 1. Recipe Validation

Always validate your recipe before attempting deployment:

```bash
# Validate a single recipe file
workato recipes validate --path project/API/Box/upload_document_to_box.recipe.json

# Validate all recipes in project
workato recipes validate --project
```

**Validation Checks:**
- ✅ Recipe structure and syntax
- ✅ Provider/connector validity
- ✅ Data pill references
- ✅ Required schemas
- ✅ Block numbering and flow

**Fix any validation errors before proceeding.**

## 2. Connection Status Check

Before pushing, verify all required connections exist and are authorized:

```bash
# List all connections in current project
workato connections list

# Check specific connection details
workato connections get --id <connection_id>
```

**Required Connections for Our Box Recipe:**
- `workato_api_platform` (for webhook trigger)
- `box` (for file upload action)

## 3. Connection Creation Workflow

### 3.1 Regular Connections (Non-OAuth)

For providers like `workato_api_platform` that don't require OAuth:

```bash
# Create connection with inline parameters
workato connections create \
  --provider workato_api_platform \
  --name "Workato API Platform" \
  --input '{"api_token": "your_api_token"}'

# Or use a config file
workato connections create \
  --provider workato_api_platform \
  --name "Workato API Platform" \
  --input-file connection-config.json
```

**Connection Config File Example (connection-config.json):**
```json
{
  "api_token": "your_workato_api_token_here"
}
```

### 3.2 OAuth Connections (Box, Google Drive, etc.)

OAuth connections require a two-step process:

#### Step 1: Create Parent OAuth Connection

```bash
# Create OAuth parent connection
workato connections create \
  --provider box \
  --name "Box OAuth Base" \
  --input '{"client_id": "your_oauth_client_id", "client_secret": "your_oauth_client_secret"}'
```

**What Happens:**
1. CLI detects OAuth provider automatically
2. Creates a shell connection (not yet authorized)
3. Provides OAuth authorization URL
4. Opens browser for user authorization

#### Step 2: Complete OAuth Authorization

The CLI will:
1. **Display OAuth URL** for you to visit
2. **Open browser automatically** (if possible)
3. **Wait for authorization** completion
4. **Confirm successful connection** creation

**Example OAuth Flow Output:**
```
🔐 OAuth provider detected - initiating OAuth authorization flow

✅ OAuth shell connection created successfully (1.2s)
  📄 Name: Box OAuth Base
  🆔 Connection ID: 12345
  🔌 Provider: box
  🏷️  External ID: oauth-shell-a1b2c3d4

🔐 OAuth Authorization Required:
  📋 OAuth URL: https://app.workato.com/connections/12345/oauth

🌐 Opening OAuth URL in browser...

💡 Next steps:
  1. Complete OAuth authorization in your browser
  2. The connection will be automatically authorized
  3. Use connection ID 12345 in your recipes
```

### 3.3 Connection Selection Strategy

When multiple connections exist for the same provider:

```bash
# List connections by provider
workato connections list --provider box

# Get connection details to choose the right one
workato connections get --id <connection_id>
```

**Choose Based On:**
- **Environment**: Production vs Development
- **Permissions**: User access levels
- **Scope**: Organization-wide vs user-specific

## 4. Recipe Configuration Updates

After creating connections, update your recipe's `config` section:

```json
{
  "config": [
    {
      "keyword": "application",
      "provider": "workato_api_platform",
      "skip_validation": false,
      "personalization": false,
      "account_id": {
        "zip_name": "Base Connections/workato_api_platform.connection.json",
        "name": "Workato API Platform",
        "folder": "Base Connections"
      }
    },
    {
      "keyword": "application",
      "provider": "box",
      "skip_validation": false,
      "personalization": true,
      "account_id": {
        "zip_name": "Base Connections/box_connection.connection.json",
        "name": "Box Connection",
        "folder": "Base Connections"
      }
    }
  ]
}
```

**Key Points:**
- `zip_name` should match your connection file path
- `name` should match your connection name
- `personalization: true` for OAuth connections
- `personalization: false` for regular connections

## 5. Project Push

Deploy your validated recipe to Workato:

```bash
# Push entire project
workato push

# Push specific recipe
workato push --recipe project/API/Box/upload_document_to_box.recipe.json
```

**Push Process:**
1. **Validates** all recipes locally
2. **Uploads** recipe files to Workato
3. **Creates/updates** remote recipe assets
4. **Synchronizes** connection references
5. **Reports** success/failure for each recipe

## 6. Recipe Startup

Start your deployed recipe:

```bash
# Start recipe by ID (from push output)
workato recipes start --id <recipe_id>

# Start recipe by name
workato recipes start --name "Upload Document to Box"
```

**Startup Process:**
1. **Validates** remote recipe configuration
2. **Checks** all connections are authorized
3. **Activates** trigger monitoring
4. **Reports** startup status

## 7. Monitoring and Troubleshooting

### 7.1 Check Recipe Status

```bash
# List recipes and check status
workato recipes list --running

# List recipes in specific folder
workato recipes list --folder-id <folder_id>
```

### 7.2 Common Startup Issues

#### Connection Authorization Failed
```
❌ Recipe startup failed: Connection authorization failed
💡 Check connection status: workato connections get --id <connection_id>
💡 Re-authorize OAuth: workato connections get-oauth-url --id <connection_id>
```

**Solution:**
1. Check connection status
2. Re-authorize if needed
3. Restart recipe

#### Missing Required Fields
```
❌ Recipe startup failed: Missing required input field 'folder_id'
💡 Verify recipe configuration and connection parameters
```

**Solution:**
1. Check recipe input schemas
2. Verify connection provides required fields
3. Update recipe configuration

#### Invalid Provider Reference
```
❌ Recipe startup failed: Provider 'box' not found in workspace
💡 Check available connectors: workato connectors list --platform
💡 Verify connection provider matches connector name
```

**Solution:**
1. Verify connector exists in workspace
2. Check connection provider name
3. Update recipe if needed

## 8. Complete Example: Box Upload Recipe

Let's walk through the complete deployment of our Box upload recipe:

### 8.1 Initial Validation
```bash
workato recipes validate --path project/API/Box/upload_document_to_box.recipe.json
```

### 8.2 Check Existing Connections
```bash
workato connections list
```

### 8.3 Create Missing Connections
```bash
# Create Box OAuth connection
workato connections create \
  --provider box \
  --name "Box Production" \
  --input '{"client_id": "your_client_id", "client_secret": "your_client_secret"}'

# Complete OAuth authorization in browser
# Connection will be created automatically
```

### 8.4 Update Recipe Config
Ensure recipe references the correct connection files.

### 8.5 Push Project
```bash
workato push
```

### 8.6 Start Recipe
```bash
workato recipes start --name "Upload Document to Box"
```

### 8.7 Monitor Execution
```bash
# Check recipe status
workato recipes list --running

# List all recipes to see status
workato recipes list
```

## 9. Best Practices

### 9.1 Connection Management
- **Use descriptive names** for connections
- **Group by environment** (Dev/Staging/Prod)
- **Document OAuth credentials** securely
- **Test connections** before recipe deployment

### 9.2 Recipe Deployment
- **Always validate** before pushing
- **Test in development** environment first
- **Use version control** for recipe changes
- **Monitor startup** and first few executions

### 9.3 Troubleshooting
- **Check logs** for detailed error messages
- **Verify connections** are authorized
- **Test connections** independently
- **Use CLI commands** for debugging

## 10. Quick Reference Commands

```bash
# Complete workflow commands
workato recipes validate --path <recipe>          # 1. Validate
workato connections list                          # 2. Check connections
workato connections create --provider <name>      # 3. Create connections
workato push                                      # 4. Push project
workato recipes start --id <id>                  # 5. Start recipe
workato recipes list --running                   # 6. Monitor execution

# Troubleshooting commands
workato connections get --id <id>                 # Check connection status
workato recipes list --running                   # Check recipe status
workato connectors list --platform               # List available connectors
workato connectors parameters --provider <name>  # Get connection parameters
```

This workflow ensures successful recipe deployment by systematically addressing each requirement: validation, connections, configuration, deployment, and monitoring.
