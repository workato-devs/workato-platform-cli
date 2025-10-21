# API Token Permissions

This document describes the permissions (scopes) available for Workato API tokens and which CLI commands require which permissions.

## Quick Start: Standard Development Permissions

For typical recipe development workflow, grant these permissions when creating your API client:

| Scope Category | Permissions Required |
|----------------|---------------------|
| **Workspace Details** | Get details (`GET /api/users/me`) |
| **Projects & Folders** | List projects (`GET /api/projects`)<br>List folders (`GET /api/folders`)<br>Create project or folder (`POST /api/folders`) |
| **Recipes** | List (`GET /api/recipes`)<br>Get details (`GET /api/recipes/:id`)<br>Create (`POST /api/recipes`)<br>Update (`PUT /api/recipes/:id`)<br>Start (`PUT /api/recipes/:id/start`)<br>Stop (`PUT /api/recipes/:id/stop`)<br>Update connection for recipe (`PUT /api/recipes/:recipe_id/connect`) |
| **Connections** | List (`GET /api/connections`)<br>Create (`POST /api/connections`)<br>Update (`POST /api/connections/:id`)<br>Get picklist values (`POST /api/connections/:id/pick_list`) |
| **Recipe Lifecycle Management** | Get package details (`GET /api/packages/:id`)<br>Download package (`GET /api/packages/:id/download`)<br>Export package (`POST /api/packages/export/:id`)<br>Import package (`POST /api/packages/import/:id`) |
| **Export Manifests** | Create export manifest (`POST /api/export_manifests`)<br>Show export manifest (`GET /api/export_manifests/:id`)<br>Get folder assets (`GET /api/export_manifests/folder_assets`) |

**Use case:** This permission set enables all core CLI workflows including `workato init`, `workato pull`, `workato push`, `workato recipes start/stop`, and `workato connections create`.

---

## Overview

Workato API tokens use a scope-based permission system. When creating an API client in **Workspace Admin → API clients**, you can select which scopes to grant. The Workato CLI inherits these permissions from your API token.

## Permission Scopes

### Project Assets
Define access to core recipe building features within projects.

#### Projects & Folders

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| List projects | `GET` | `/api/projects` | `workato projects list` |
| List folders | `GET` | `/api/folders` | `workato projects list` (recursive) |
| Create project or folder | `POST` | `/api/folders` | `workato init` |
| Delete folder | `DELETE` | `/api/folders/:id` | - |
| Update folder | `PUT` | `/api/folders/:id` | - |
| Delete project | `DELETE` | `/api/projects/:id` | - |
| Update project | `PUT` | `/api/projects/:id` | - |

#### Connections

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| List | `GET` | `/api/connections` | `workato connections list` |
| Create | `POST` | `/api/connections` | `workato connections create` |
| Update | `POST` | `/api/connections/:id` | `workato connections update` |
| Delete Connection | `DELETE` | `/api/connections/:id` | `workato connections delete` |
| Disconnect Connection | `POST` | `/api/connections/:id/disconnect` | - |
| Get picklist values | `POST` | `/api/connections/:id/pick_list` | `workato connections picklist` |

#### Recipes

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| List | `GET` | `/api/recipes` | `workato recipes list` |
| Get job counts for recipes | `GET` | `/api/recipes/job_counts` | - |
| Get details | `GET` | `/api/recipes/:id` | - |
| Create | `POST` | `/api/recipes` | `workato push` |
| Update | `PUT` | `/api/recipes/:id` | `workato push` |
| Copy | `POST` | `/api/recipes/:id/copy` | - |
| Delete | `DELETE` | `/api/recipes/:id` | - |
| Start | `PUT` | `/api/recipes/:id/start` | `workato recipes start` |
| Stop | `PUT` | `/api/recipes/:id/stop` | `workato recipes stop` |
| Forces a running recipe to poll immediately | `POST` | `/api/recipes/:recipe_id/poll_now` | - |
| Reset recipe trigger | `POST` | `/api/recipes/:recipe_id/reset_trigger` | - |
| Update connection for recipe | `PUT` | `/api/recipes/:recipe_id/connect` | `workato recipes update-connection` |

#### Genies

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| List genies | `GET` | `/api/agentic/genies` | - |
| Get genie | `GET` | `/api/agentic/genies/:id` | - |
| Create genie | `POST` | `/api/agentic/genies` | - |
| Update genie | `PUT` | `/api/agentic/genies/:id` | - |
| Delete genie | `DELETE` | `/api/agentic/genies/:id` | - |
| Start genie | `POST` | `/api/agentic/genies/:id/start` | - |
| Stop genie | `POST` | `/api/agentic/genies/:id/stop` | - |
| Assign skills to genie | `POST` | `/api/agentic/genies/:id/assign_skills` | - |
| Remove skills from genie | `POST` | `/api/agentic/genies/:id/remove_skills` | - |
| Assign knowledge bases to genie | `POST` | `/api/agentic/genies/:id/assign_knowledge_bases` | - |
| Remove knowledge bases from genie | `POST` | `/api/agentic/genies/:id/remove_knowledge_bases` | - |
| Assign user groups to genie | `POST` | `/api/agentic/genies/:id/assign_user_groups` | - |
| Remove user groups from genie | `POST` | `/api/agentic/genies/:id/remove_user_groups` | - |

#### Knowledge Bases

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| List knowledge bases | `GET` | `/api/agentic/knowledge_bases` | - |
| Get knowledge base | `GET` | `/api/agentic/knowledge_bases/:id` | - |
| Create knowledge base | `POST` | `/api/agentic/knowledge_bases` | - |
| Update knowledge base | `PUT` | `/api/agentic/knowledge_bases/:id` | - |
| Delete knowledge base | `DELETE` | `/api/agentic/knowledge_bases/:id` | - |
| Get knowledge base data sources | `GET` | `/api/agentic/knowledge_bases/:id/data_sources` | - |
| Get knowledge base recipes | `GET` | `/api/agentic/knowledge_bases/:id/recipes` | - |

#### Skills

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| List skills | `GET` | `/api/agentic/skills` | - |
| Get skill | `GET` | `/api/agentic/skills/:id` | - |
| Create skill | `POST` | `/api/agentic/skills` | - |

#### Recipe Versions

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| List | `GET` | `/api/recipes/:recipe_id/versions` | - |
| Get details | `GET` | `/api/recipes/:recipe_id/versions/:id` | - |
| Update | `PUT` | `/api/recipes/:recipe_id/versions/:id` | - |

#### Jobs

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| List | `GET` | `/api/recipes/:recipe_id/jobs` | - |
| Get job | `GET` | `/api/recipes/:recipe_id/jobs/:job_id` | - |
| Resume suspended job | `POST` | `/api/job/resume` | - |

#### Tag Assignments

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| Manage tag assignments | `POST` | `/api/tags_assignments` | - |

#### Test Cases

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| List test cases for recipe | `GET` | `/api/recipes/:recipe_id/test_cases` | - |
| Run test cases | `POST` | `/api/test_cases/run_requests` | - |
| Get run details | `GET` | `/api/test_cases/run_requests/:id` | - |

---

### Recipe Lifecycle Management
Define access to assets transfer across workspaces.

#### Recipe Lifecycle Management

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| Get package details | `GET` | `/api/packages/:id` | `workato pull`, `workato push` |
| Download package | `GET` | `/api/packages/:id/download` | `workato pull` |
| Export package | `POST` | `/api/packages/export/:id` | `workato pull` |
| Import package | `POST` | `/api/packages/import/:id` | `workato push` |

#### Export Manifests

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| Create export manifest | `POST` | `/api/export_manifests` | `workato pull` |
| Show export manifest | `GET` | `/api/export_manifests/:id` | `workato pull` |
| Update export manifest | `PUT` | `/api/export_manifests/:id` | - |
| Delete export manifest | `DELETE` | `/api/export_manifests/:id` | - |
| Get folder assets for export manifest | `GET` | `/api/export_manifests/folder_assets` | `workato pull` |

---

### Workspace Data
Define access to data configured at the workspace-level.

#### Lookup Tables

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| List tables | `GET` | `/api/lookup_tables` | - |
| Create table | `POST` | `/api/lookup_tables` | - |
| List rows | `GET` | `/api/lookup_tables/:lookup_table_id/rows` | - |
| Get row | `GET` | `/api/lookup_tables/:lookup_table_id/rows/:row_id` | - |
| Lookup row | `GET` | `/api/lookup_tables/:lookup_table_id/lookup` | - |
| Update row | `PUT` | `/api/lookup_tables/:lookup_table_id/rows/:row_id` | - |
| Add row | `POST` | `/api/lookup_tables/:lookup_table_id/rows` | - |
| Delete row | `DELETE` | `/api/lookup_tables/:lookup_table_id/rows/:row_id` | - |
| Batch delete tables | `POST` | `/api/lookup_tables/batch_delete` | - |

#### Data Tables

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| List data tables | `GET` | `/api/data_tables` | `workato data-tables list` |
| Create a data table | `POST` | `/api/data_tables` | `workato data-tables create` |
| Get data table by id | `GET` | `/api/data_tables/:data_table_id` | - |
| Delete a data table | `DELETE` | `/api/data_tables/:data_table_id` | `workato data-tables delete` |
| Update a data table | `PUT` | `/api/data_tables/:data_table_id` | - |
| Truncate a data table | `POST` | `/api/data_tables/:data_table_id/truncate` | `workato data-tables truncate` |

#### Data Table Records

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| Create record | `POST` | `/api/v1/tables/:data_table_id/records` | - |
| Update record | `PUT` | `/api/v1/tables/:data_table_id/records/:record_id` | - |
| Delete record | `DELETE` | `/api/v1/tables/:data_table_id/records/:record_id` | - |
| Query records | `POST` | `/api/v1/tables/:data_table_id/records/query` | - |

#### Event Streams

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| Publish message to event topic | `POST` | `/api/v1/topics/:topic_id/publish` | - |
| Read messages from event topic | `POST` | `/api/v1/topics/:topic_id/consume` | - |

#### Event Streams Topics

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| List topics | `GET` | `/api/event_streams/topics` | - |
| Create a topic | `POST` | `/api/event_streams/topics` | - |
| Get topic by id | `GET` | `/api/event_streams/topics/:topic_id` | - |
| Delete a topic | `DELETE` | `/api/event_streams/topics/:topic_id` | - |
| Update a topic | `PUT` | `/api/event_streams/topics/:topic_id` | - |
| Purge a topic | `PUT` | `/api/event_streams/topics/:topic_id/purge` | - |

#### Environment Properties

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| List | `GET` | `/api/properties` | `workato properties list` |
| Upsert | `POST` | `/api/properties` | `workato properties set` |

---

### API Platform
Define access to manage and monitor API recipe endpoints and collections.

#### Certificate Bundles

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| List certificate bundles | `GET` | `/api/cert_bundles` | - |
| Create certificate bundle | `POST` | `/api/cert_bundles` | - |
| Update certificate bundle | `PUT` | `/api/cert_bundles/:cert_bundle_id` | - |
| Delete certificate bundle | `DELETE` | `/api/cert_bundles/:cert_bundle_id` | - |
| Download certificate bundle | `GET` | `/api/cert_bundles/:cert_bundle_id` | - |

#### API Portal

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| List API Portals | `GET` | `/api/v2/api_portals` | - |

#### Collections & Endpoints

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| List collections | `GET` | `/api/api_collections` | `workato api-collections list` |
| Create collection | `POST` | `/api/api_collections` | `workato api-collections create` |
| List endpoints in a collection | `GET` | `/api/api_endpoints` | `workato api-collections endpoints` |
| Enable endpoint | `PUT` | `/api/api_endpoints/:api_endpoint_id/enable` | - |
| Disable endpoint | `PUT` | `/api/api_endpoints/:api_endpoint_id/disable` | - |

#### Clients & Access Profiles

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| List clients | `GET` | `/api/api_clients`, `/api/v2/api_clients` | `workato api-clients list` |
| Get client by ID | `GET` | `/api/v2/api_clients/:api_client_id` | - |
| Create client | `POST` | `/api/api_clients`, `/api/v2/api_clients` | `workato api-clients create` |
| Update client | `PUT` | `/api/v2/api_clients/:api_client_id` | - |
| Delete client | `DELETE` | `/api/v2/api_clients/:api_client_id` | `workato api-clients delete` |
| List access profiles | `GET` | `/api/api_access_profiles`, `/api/v2/api_clients/:api_client_id/api_keys` | - |
| Update access profile | `PUT` | `/api/api_access_profiles/:api_access_profile_id`, `/api/v2/api_clients/:api_client_id/api_keys/:api_key_id` | - |
| Create access profile | `POST` | `/api/api_access_profiles`, `/api/v2/api_clients/:api_client_id/api_keys` | - |
| Enable access profile | `PUT` | `/api/api_access_profiles/:api_access_profile_id/enable`, `/api/v2/api_clients/:api_client_id/api_keys/:api_key_id/enable` | - |
| Disable access profile | `PUT` | `/api/api_access_profiles/:api_access_profile_id/disable`, `/api/v2/api_clients/:api_client_id/api_keys/:api_key_id/disable` | - |
| Refresh token/secret | `PUT` | `/api/api_access_profiles/:access_profile_id/refresh_secret`, `/api/v2/api_clients/:api_client_id/api_keys/:api_key_id/refresh_secret` | - |
| Delete access profile | `DELETE` | `/api/v2/api_clients/:api_client_id/api_keys/:api_key_id` | - |

---

### Connector SDKs
Define access to managing custom connectors and their versions.

#### Connector SDKs

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| List | `GET` | `/api/custom_connectors` | `workato connectors list` |
| Release latest version | `POST` | `/api/custom_connectors/:id/release` | - |
| Share latest version | `POST` | `/api/custom_connectors/:id/share` | - |
| Update custom connector | `PUT` | `/api/custom_connectors/:id` | `workato connectors update` |
| Create custom connector | `POST` | `/api/custom_connectors` | `workato connectors create` |
| Search custom connectors | `GET` | `/api/custom_connectors/search` | - |
| Get custom connector code | `GET` | `/api/custom_connectors/:id/code` | `workato connectors get-code` |

#### SDK CLI

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| Generate Schema from CSV | `POST` | `/api/sdk/generate_schema/csv` | - |
| Generate Schema from JSON | `POST` | `/api/sdk/generate_schema/json` | - |

---

### Custom OAuth Profiles
Define access to manage custom OAuth profiles.

#### Custom OAuth Profiles

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| List custom OAuth profiles | `GET` | `/api/custom_oauth_profiles` | - |
| Create custom OAuth profiles | `POST` | `/api/custom_oauth_profiles` | - |
| Get custom OAuth profile | `GET` | `/api/custom_oauth_profiles/:id` | - |
| Update custom OAuth profile | `PUT` | `/api/custom_oauth_profiles/:id` | - |
| Delete custom OAuth profile | `DELETE` | `/api/custom_oauth_profiles/:id` | - |

---

### On-Prem Groups and Agents
Define access to manage connectivity to authorized on-prem applications through groups and agents.

#### On-Prem Groups

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| List | `GET` | `/api/on_prem_groups` | - |
| Get status | `GET` | `/api/on_prem_groups/:id/status` | - |
| Get details | `GET` | `/api/on_prem_groups/:id` | - |
| Update | `PUT` | `/api/on_prem_groups/:id` | - |
| Create | `POST` | `/api/on_prem_groups` | - |
| Delete | `DELETE` | `/api/on_prem_groups/:id` | - |
| Get agents in group | `GET` | `/api/on_prem_groups/:id/agents` | - |

#### On-Prem Agents

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| List | `GET` | `/api/on_prem_agents` | - |
| Search | `GET` | `/api/on_prem_agents/search` | - |
| Get status | `GET` | `/api/on_prem_agents/:id/status` | - |
| Get details | `GET` | `/api/on_prem_agents/:id` | - |
| Update | `PUT` | `/api/on_prem_agents/:id` | - |
| Create | `POST` | `/api/on_prem_agents` | - |
| Delete | `DELETE` | `/api/on_prem_agents/:id` | - |
| Get activation code | `GET` | `/api/on_prem_agents/:id/activation_code` | - |

---

### Partner Marketplace
Define access to endpoints that help in the creation of a connector marketplace for your customers.

#### Connectors

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| Search connectors | `GET` | `/api/integrations` | - |
| List connectors | `GET` | `/api/integrations/all` | - |

---

### Workspace Collaborators
Define access to manage collaborators and their roles in your workspace.

#### Collaborators

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| Invite | `POST` | `/api/member_invitations` | - |
| Get collaborators | `GET` | `/api/members` | - |
| Get collaborator | `GET` | `/api/members/:id` | - |
| Update collaborator's roles | `PUT` | `/api/members/:id` | - |
| Get collaborator privileges | `GET` | `/api/members/:id/privileges` | - |
| Delete collaborator | `DELETE` | `/api/members/:id` | - |

#### Collaborator Roles

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| List non-system roles | `GET` | `/api/roles` | - |
| Copy non-system role | `POST` | `/api/roles/:id/copy` | - |
| Update non-system role | `PUT` | `/api/roles/:id` | - |

---

### Workspace Details
Define access to retrieval of workspace details.

#### Workspace Details

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| Get details | `GET` | `/api/users/me` | `workato workspace`, `workato init` |

---

### Environment Management
Define access to environment management operations.

#### Secrets Management

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| Clear secrets cache | `POST` | `/api/secrets_management/clear_cache` | - |

#### Audit Log

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| Get audit log | `GET` | `/api/activity_logs` | - |

#### Tags

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| List tags | `GET` | `/api/tags` | - |
| Create tag | `POST` | `/api/tags` | - |
| Update tag | `PUT` | `/api/tags/:handle` | - |
| Delete tag | `DELETE` | `/api/tags/:handle` | - |

---

### Developer API Clients
Define access to manage API clients.

#### API Clients

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| List API clients | `GET` | `/api/developer_api_clients` | - |
| Create API clients | `POST` | `/api/developer_api_clients` | - |
| Get API client by ID | `GET` | `/api/developer_api_clients/:id` | - |
| Update API client | `PUT` | `/api/developer_api_clients/:id` | - |
| Delete API client | `DELETE` | `/api/developer_api_clients/:id` | - |
| Regenerate API client token | `POST` | `/api/developer_api_clients/:id/regenerate` | - |

#### API Client Roles

| Permission | HTTP Method | Endpoint | CLI Commands |
|------------|-------------|----------|--------------|
| List API client roles | `GET` | `/api/developer_api_client_roles` | - |
| Copy API client role | `POST` | `/api/developer_api_client_roles/:id/copy` | - |

---

## Recommended Permission Sets

### Basic CLI Usage (Read-Only)
For users who only need to view and list resources:
- **Workspace Details**: Get details
- **Projects & Folders**: List projects, List folders
- **Recipes**: List, Get details
- **Connections**: List
- **Data Tables**: List data tables

### Standard Development
For typical recipe development workflow:
- All permissions from **Basic CLI Usage**
- **Projects & Folders**: Create project or folder
- **Recipes**: Create, Update, Start, Stop, Update connection for recipe
- **Connections**: Create, Update, Get picklist values
- **Recipe Lifecycle Management**: All permissions
- **Export Manifests**: All permissions

### Full CLI Access
For complete control over all CLI features:
- **All permissions** across all scopes

---

## Common CLI Workflows

### `workato init` - Initialize Project
**Required permissions:**
- Workspace Details → Get details
- Projects & Folders → List projects, Create project or folder

### `workato pull` - Pull Project Assets
**Required permissions:**
- Projects & Folders → List folders
- Recipe Lifecycle Management → Create export manifest, Export package, Download package
- Export Manifests → Create export manifest, Show export manifest, Get folder assets

### `workato push` - Push Project Assets
**Required permissions:**
- Recipe Lifecycle Management → Import package, Get package details
- Recipes → Create, Update

### `workato recipes start/stop` - Manage Recipes
**Required permissions:**
- Recipes → List, Start, Stop

### `workato connections create` - Create Connection
**Required permissions:**
- Connections → Create, Get picklist values

---

## Troubleshooting

### 403 Forbidden Errors
If you receive a `403 Forbidden` error, your API token lacks the required permissions:

```
❌ Access forbidden
   You don't have permission to perform this action
💡 Please check:
   • Your account has the required permissions
   • You're working in the correct workspace/folder
   • The resource exists and is accessible to you
```

**Solution:** Check your API client's scopes in **Workspace Admin → API clients** and grant the necessary permissions.

### 401 Unauthorized Errors
If you receive a `401 Unauthorized` error, your API token is invalid or expired:

```
❌ Authentication failed
   Your API token may be invalid
💡 Please check your authentication:
   • Verify your API token is correct
   • Run 'workato profiles list' to check your profile
   • Run 'workato profiles use' to update your credentials
```

**Solution:** Regenerate your API token or verify it's correctly stored in your profile.

---

## Related Documentation

- [Quick Start Guide](QUICK_START.md)
- [Command Reference](COMMAND_REFERENCE.md)
- [Developer Guide](DEVELOPER_GUIDE.md)
