---
title: Workato API - Connection parameters reference
date: 2024-05-15 00:00:00
translated: false
page_nav_depth: 3

attributes:
  - name: 'oauth'
    type: 'boolean'
    description: 'If <code>true</code>, the connector requires OAuth.'

  - name: 'personalization'
    type: 'boolean'
    description: 'If <code>true</code>, the connection can be used as a personalized connection in Workbot use cases.'

  - name: 'secure_tunnel'
    type: 'boolean'
    description: 'If <code>true</code>, the connection can be used to connect to on-premise systems.'

  - name: 'input'
    type: 'array'
    description: 'An array of objects describing the connection parameters for the connector. When empty, no configuration is required.'
---

# Connection parameters reference

This reference contains the connection parameters required to configure connectors using Workato's APIs.

## Provider values

Every connector has a `provider` value which uniquely identifies the type of connector. For example, the Salesforce connector has a `provider: salesforce` value.

Provider values should be supplied when:

- [**Creating a connection**](/oem/oem-api/connections.md#create-a-connection) using the Platform API:

  ```shell
  curl  -X POST https://www.workato.com/api/managed_users/98178/connections \
        -H 'Authorization: Bearer <api_token>' \
        -H 'Content-Type: application/json' \
        -d  '{
               "name": "Salesforce",
               "provider": "salesforce"
             }'
  ```

- **Defining [App Access](/oem/oem-api/managed-users.md) for customers**. A connector's `provider` value can be included in the `whitelisted_apps` parameter to define the list of connectors the customer can access.

  For example, the following request creates an account that only has access to Salesforce and NetSuite:

  ```shell
  curl  -X POST https://www.workato.com/api/managed_users \
        -H 'Authorization: Bearer <api_token>' \
        -H 'Content-Type: application/json' \
        -d '{
              "name": "Kevin Leary",
              "notification_email": "kevinl@acme.com",
              "external_id": "UU0239093498",
              "whitelisted_apps": ["salesforce", "netsuite"],
              "time_zone": "Central Time (US & Canada)"
            }'
  ```

## Connection parameters

The following parameters describe the configuration for a given connector:

<table width="100%">
  <thead>
    <tr>
        <th>Field</th>
        <th>Type</th>
        <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr v-for="field in $frontmatter.attributes">
      <td>
        <strong>{{ field.name }}</strong>
      </td>
      <td>
        {{ field.type }}
      </td>
      <td v-html="field.description">
      </td>
    </tr>
  </tbody>
</table>

---
### Example: No configuration required

The following is an example of a connector that doesn't require any configuration:

```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          []
      }
```

---
### Example: Configuration required

The following is an example of the configuration for the Airtable connector, which requires connection parameter configuration:

```json
{
    "oauth": true,
    "personalization": false,
    "input": [
        {
            "name": "authentication_type",
            "type": "select",
            "options": [
                "OAuth 2.0",
                "Personal access token",
                "API key (Deprecated)"
            ],
            "optional": false,
            "label": "Authentication type",
            "hint": "Select 'OAuth 2.0' or 'Personal access token' for current methods, 'API key' is unsupported."
        },
        {
            "name": "personal_access_token",
            "type": "string",
            "optional": true,
            "label": "Personal access token",
            "hint": "Enter your personal access token here if 'Personal access token' is the selected authentication type.",
            "conditional": {
                "field": "authentication_type",
                "value": "Personal access token"
            }
        }
    ]
}
```

---

## Configuration parameters and provider values by connector

The following list contains the configuration parameters and provider values for each connector.

**Note**: Only connectors that require connections are listed.

### 2Checkout

**Provider value:**
```json
"provider": "two_checkout"
```

---
### Active Directory


###

**Provider value:**
```json
"provider": "active_directory"
```

::: details View connection parameters JSON
```json
      {
         "oauth":false,
         "personalization":false,
         "input":[
            {
               "name":"company_identifier",
               "type":"string",
               "label":"Company identifier"
            },
            {
               "name":"ftp_host",
               "type":"string",
               "label":"FTP host"
            },
            {
               "name":"ftp_user",
               "type":"string",
               "label":"FTP user"
            },
            {
               "name":"ftp_password",
               "type":"string",
               "label":"FTP password"
            },
            {
               "name":"pgp_key",
               "type":"string",
               "label":"PGP public key"
            }
         ]
      }
```
:::

---
### Adobe Experience Manager

**Provider value:**
```json
"provider": "adobe_experience_manager"
```

---
### ADP 2

**Provider value:**
```json
"provider": "adp"
```

::: details View connection parameters JSON
```JSON
      {
         "oauth":false,
         "personalization":false,
         "input":[
            {
               "name":"company_identifier",
               "type":"string",
               "label":"Company identifier"
            },
            {
               "name":"ftp_host",
               "type":"string",
               "label":"FTP host"
            },
            {
               "name":"ftp_user",
               "type":"string",
               "label":"FTP user"
            },
            {
               "name":"ftp_password",
               "type":"string",
               "label":"FTP password"
            },
            {
               "name":"pgp_key",
               "type":"string",
               "label":"PGP public key"
            }
         ]
      }
```
:::

---
### ADP Workforce Now

**Provider value:**
```json
"provider": "adp7"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "sandbox",
                  "type": "boolean",
                  "optional": true,
                  "label": "Sandbox",
                  "default": "false"
              },
              {
                  "name": "client_id",
                  "type": "string",
                  "label": "Client ID"
              },
              {
                  "name": "client_secret",
                  "type": "string",
                  "label": "Client secret"
              },
              {
                  "name": "ssl_client_cert",
                  "type": "string",
                  "label": "SSL client certificate"
              },
              {
                  "name": "ssl_client_key",
                  "type": "string",
                  "label": "SSL client key"
              },
              {
                  "name": "ssl_key_passphrase",
                  "type": "string",
                  "optional": true,
                  "label": "Custom CA certificate"
              },
              {
                  "name": "unmask",
                  "type": "boolean",
                  "optional": true,
                  "label": "Unmask sensitive information?",
                  "hint": "If <b>Yes</b>, sensitive information will be returned in the response. If <b>No</b>, it will not be returned.",
                  "default": "false"
              }
          ]
      }
```
:::

---
### Airbrake

**Provider value:**
```
"provider": "airbrake"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "api_key",
                  "type": "string",
                  "optional": true,
                  "label": "Api key"
              }
          ]
      }
```
:::

---
### AirREGI

**Provider value:**
```json
"provider": "air_regi"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          []
      }
```
:::

---
### Airtable

**Provider value:**
```json
"provider": "airtable"
```

::: details View connection parameters JSON
```json
      {
    "oauth": true,
    "personalization": false,
    "input": [
        {
            "name": "authentication_type",
            "type": "select",
            "options": [
                "OAuth 2.0",
                "Personal access token",
                "API key (Deprecated)"
            ],
            "optional": false,
            "label": "Authentication type",
            "hint": "Select 'OAuth 2.0' or 'Personal access token' for current methods, 'API key' is unsupported."
        },
        {
            "name": "personal_access_token",
            "type": "string",
            "optional": true,
            "label": "Personal access token",
            "hint": "Enter your personal access token here if 'Personal access token' is the selected authentication type.",
            "conditional": {
                "field": "authentication_type",
                "value": "Personal access token"
            }
        }
    ]
}
```
:::

---
### Amazon Cognito

**Provider value:**
```json
"provider": "aws_cognito"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "api_key",
                  "type": "string",
                  "optional": false,
                  "label": "API key",
                  "hint": "You can find the API Key on the <a target='_blank' href='https://airtable.com/account'>account</a> page."
              }
          ]
      }
```
:::

---
### Amazon Lex

**Provider value:**
```json
"provider": "amazon_lex_nlu"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "bot_name",
                  "type": "string",
                  "label": "Bot name",
                  "hint": "Amazon Lex Bot Name"
              },
              {
                  "name": "bot_alias",
                  "type": "string",
                  "label": "Bot alias",
                  "hint": "Amazon Lex Bot Alias"
              },
              {
                  "name": "region",
                  "type": "string",
                  "label": "Region",
                  "hint": "Region"
              },
              {
                  "name": "access_key_id",
                  "type": "string",
                  "label": "Access key ID",
                  "hint": "IAM User: Access Key Id (AWS managed policy \"AmazonLexRunBotsOnly\" should be attached to the user)"
              },
              {
                  "name": "secret_access_key",
                  "type": "string",
                  "label": "Secret access key",
                  "hint": "IAM User: Secret Access Key"
              }
          ]
      }
```
:::

---
### Amazon S3

**Provider value:**
```json
"provider": "amazon_s3"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "auth_type",
                  "type": "string",
                  "optional": false,
                  "label": "Authorization type",
                  "hint": "            Learn more about Amazon S3 authorization support <a href=\"http://docs.workato.com/connectors/s3.html#connection-setup\" target=\"_blank\">here</a>.\n",
                  "pick_list":
                  [
                      [
                          "Access key",
                          "key_secret"
                      ],
                      [
                          "IAM role",
                          "role_based"
                      ]
                  ],
                  "default": "key_secret"
              },
              {
                  "name": "assume_role",
                  "type": "string",
                  "optional": false,
                  "label": "IAM role ARN",
                  "hint": "Follow <a href=\"http://docs.workato.com/connectors/s3.html#connection-setup\" target=\"_blank\">this guide</a> to create an IAM role in your S3, then input the IAM ARN here.\nWorkato S3 account (ID: <b>484634596152</b>) will assume this IAM role to access your instance.\n<a href=\"https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-user.html\" target=\"_blank\">Learn more</a>.\n"
              },
              {
                  "name": "api_key",
                  "type": "string",
                  "optional": false,
                  "label": "Access key ID",
                  "hint": "Go to <b>AWS account name</b> > <b>My Security Credentials</b> > <b>Users</b>. Get API key from existing user or create new user."
              },
              {
                  "name": "secret_key",
                  "type": "string",
                  "optional": false,
                  "label": "Secret access key",
                  "hint": "Go to <b>AWS account name</b> > <b>My Security Credentials</b> > <b>Users</b>. Get secret key from existing user or create new user."
              },
              {
                  "name": "external_id",
                  "type": "string",
                  "optional": true,
                  "label": "External ID",
                  "hint": "External ID was created when you first created the IAM role in S3.\n<a href=\"https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-user_externalid.html\" target=\"_blank\">Learn more</a>\n"
              },
              {
                  "name": "restrict_to_bucket",
                  "type": "string",
                  "optional": true,
                  "label": "Restrict to bucket",
                  "hint": "Use to restrict connection to specified bucket. Needed when this user has only limited\n<a href=\"http://docs.aws.amazon.com/AmazonS3/latest/dev/using-with-s3-actions.html#using-with-s3-actions-related-to-buckets\" target=\"_blank\">s3:ListBucket</a> access.\n"
              },
              {
                  "name": "restrict_to_path",
                  "type": "string",
                  "optional": true,
                  "label": "Restrict to path",
                  "hint": "Use to restrict connection to specified bucket and object or path. Needed when this user has only limited\n<a href=\"http://docs.aws.amazon.com/AmazonS3/latest/dev/using-with-s3-actions.html#using-with-s3-actions-related-to-buckets\" target=\"_blank\">s3:ListBucket</a> access.'\n"
              },
              {
                  "name": "region",
                  "type": "string",
                  "optional": false,
                  "label": "Region",
                  "hint": "Region is typically provided in the S3 account URL. If your account URL is <b>https://eu-west-1.console.s3.amazon.com</b>, use <b>eu-west-1</b> as the region."
              },
              {
                  "name": "download_threads",
                  "type": "string",
                  "optional": true,
                  "label": "Download threads",
                  "hint": "Use to boost download speed. One thread is used by default."
              }
          ]
      }
```
:::

---
### Amazon S3 (Secondary)

**Provider value:**
```json
"provider": "amazon_s3_secondary"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "auth_type",
                  "type": "string",
                  "optional": false,
                  "label": "Authorization type",
                  "hint": "            Learn more about Amazon S3 authorization support <a href=\"http://docs.workato.com/connectors/s3.html#connection-setup\" target=\"_blank\">here</a>.\n",
                  "pick_list":
                  [
                      [
                          "Access key",
                          "key_secret"
                      ],
                      [
                          "IAM role",
                          "role_based"
                      ]
                  ],
                  "default": "key_secret"
              },
              {
                  "name": "assume_role",
                  "type": "string",
                  "optional": false,
                  "label": "IAM role ARN",
                  "hint": "Follow <a href=\"http://docs.workato.com/connectors/s3.html#connection-setup\" target=\"_blank\">this guide</a> to create an IAM role in your S3, then input the IAM ARN here.\nWorkato S3 account (ID: <b>484634596152</b>) will assume this IAM role to access your instance.\n<a href=\"https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-user.html\" target=\"_blank\">Learn more</a>.\n"
              },
              {
                  "name": "api_key",
                  "type": "string",
                  "optional": false,
                  "label": "Access key ID",
                  "hint": "Go to <b>AWS account name</b> > <b>My Security Credentials</b> > <b>Users</b>. Get API key from existing user or create new user."
              },
              {
                  "name": "secret_key",
                  "type": "string",
                  "optional": false,
                  "label": "Secret access key",
                  "hint": "Go to <b>AWS account name</b> > <b>My Security Credentials</b> > <b>Users</b>. Get secret key from existing user or create new user."
              },
              {
                  "name": "external_id",
                  "type": "string",
                  "optional": true,
                  "label": "External ID",
                  "hint": "External ID was created when you first created the IAM role in S3.\n<a href=\"https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-user_externalid.html\" target=\"_blank\">Learn more</a>\n"
              },
              {
                  "name": "restrict_to_bucket",
                  "type": "string",
                  "optional": true,
                  "label": "Restrict to bucket",
                  "hint": "Use to restrict connection to specified bucket. Needed when this user has only limited\n<a href=\"http://docs.aws.amazon.com/AmazonS3/latest/dev/using-with-s3-actions.html#using-with-s3-actions-related-to-buckets\" target=\"_blank\">s3:ListBucket</a> access.\n"
              },
              {
                  "name": "restrict_to_path",
                  "type": "string",
                  "optional": true,
                  "label": "Restrict to path",
                  "hint": "Use to restrict connection to specified bucket and object or path. Needed when this user has only limited\n<a href=\"http://docs.aws.amazon.com/AmazonS3/latest/dev/using-with-s3-actions.html#using-with-s3-actions-related-to-buckets\" target=\"_blank\">s3:ListBucket</a> access.'\n"
              },
              {
                  "name": "region",
                  "type": "string",
                  "optional": false,
                  "label": "Region",
                  "hint": "Region is typically provided in the S3 account URL. If your account URL is <b>https://eu-west-1.console.s3.amazon.com</b>, use <b>eu-west-1</b> as the region."
              },
              {
                  "name": "download_threads",
                  "type": "string",
                  "optional": true,
                  "label": "Download threads",
                  "hint": "Use to boost download speed. One thread is used by default."
              }
          ]
      }
```
:::

---
### Amazon SNS

**Provider value:**
```json
"provider": "aws_sns"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "access_key_id",
                  "type": "string",
                  "optional": false,
                  "label": "Access Key ID",
                  "hint": "Select your AWS account name > Security Credentials > Users. Get API key from existing user or create user"
              },
              {
                  "name": "secret_access_key",
                  "type": "string",
                  "optional": false,
                  "label": "Secret Access Key",
                  "hint": "Select your AWS account name > Security Credentials > Users. Get secret key from existing user or create user"
              },
              {
                  "name": "region",
                  "type": "string",
                  "optional": false,
                  "label": "Region",
                  "hint": "If your account url is https://eu-west-1.console.aws.amazon.com then use eu-west-1 as the region"
              }
          ]
      }
```
:::

---
### Amazon SQS

**Provider value:**
```json
"provider": "aws_sqs"
```

---
### AMcards

**Provider value:**
```json
"provider": "amcards"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "access_token",
                  "type": "string",
                  "optional": false,
                  "label": "Access token",
                  "hint": "Click <a target='_blank' href=https://amcards.com/profile/generate-access-token>here</a> to get access token"
              }
          ]
      }
```
:::

---
### Anaplan

**Provider value:**
```json
"provider": "anaplan"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "authentication_type",
                  "type": "string",
                  "label": "Authentication type",
                  "pick_list":
                  [
                      [
                          "Certificate authentication",
                          "certificate_auth"
                      ],
                      [
                          "Username/password",
                          "basic_auth"
                      ]
                  ],
                  "default": "basic_auth"
              },
              {
                  "name": "username",
                  "type": "string",
                  "optional": false,
                  "label": "Username"
              },
              {
                  "name": "certificate",
                  "type": "string",
                  "optional": false,
                  "label": "Certificate",
                  "hint": "             Enter a PEM-format certificate string. Learn how to obtain a CA certificate and convert to a PEM string\n             <a href=\"https://help.anaplan.com/anapedia/Content/Administration_and_Security/Tenant_Administration/Security/ProcuringCACertificates.htm\" target=\"_blank\">here</a>.\n"
              },
              {
                  "name": "private_key",
                  "type": "string",
                  "optional": false,
                  "label": "Private key",
                  "hint": "Enter a PEM-format private key string."
              },
              {
                  "name": "password",
                  "type": "string",
                  "optional": false,
                  "label": "Password"
              }
          ]
      }
```
:::

---
### Apache Kafka

**Provider value:**
```json
"provider": "kafka"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "profile",
                  "type": "string",
                  "label": "On-prem Kafka connection profile"
              }
          ]
      }
```
:::

---
### Apttus

**Provider value:**
```json
"provider": "apttus"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "sandbox",
                  "type": "boolean",
                  "optional": true,
                  "label": "Sandbox",
                  "hint": "Is this connecting to a sandbox account?",
                  "default": "false"
              }
          ]
      }
```
:::

---
### Apttus Intelligent Cloud

**Provider value:**
```json
"provider": "apttus_intelligent_cloud"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "subdomain",
                  "type": "string",
                  "optional": false,
                  "label": "Subdomain",
                  "hint": "Your AIC cloud name as found in your apttus AIC URL"
              },
              {
                  "name": "client_id",
                  "type": "string",
                  "optional": false,
                  "label": "Client ID"
              },
              {
                  "name": "client_secret",
                  "type": "string",
                  "optional": false,
                  "label": "Client secret"
              },
              {
                  "name": "directory_id",
                  "type": "string",
                  "optional": false,
                  "label": "Directory ID",
                  "hint": "Your directory ID can be found <a target=\"_blank\" href=\"https://portal.azure.com/#blade/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/Properties\">here</a>."
              }
          ]
      }
```
:::

---
### Ariba

**Provider value:**
```json
"provider": "ariba"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "network_user_id",
                  "type": "string",
                  "label": "Network user ID"
              },
              {
                  "name": "shared_secret",
                  "type": "string",
                  "label": "Shared secret"
              },
              {
                  "name": "buyer_network_user_id",
                  "type": "string",
                  "label": "Buyer network user ID"
              },
              {
                  "name": "purchase_order_url",
                  "type": "string",
                  "label": "Purchase order URL",
                  "hint": "URL for submitting the purchase order cXML",
                  "default": "http://www.workato.com/ariba/purchase_order/1/78"
              }
          ]
      }
```
:::

---
### Asana

**Provider value:**
```json
"provider": "asana"
```

Connection parameter configuration **_is not required_** for this connector.

---
### AscentERP

**Provider value:**
```json
"provider": "ascent_erp"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "sandbox",
                  "type": "boolean",
                  "optional": true,
                  "label": "Sandbox",
                  "hint": "Is this connecting to a sandbox account?",
                  "default": "false"
              }
          ]
      }
```
:::

---
### AWS Cognito

**Provider value:**
```json
"provider": "aws_cognito"
```

---
### AWS Lambda

**Provider value:**
```json
"provider": "aws_lambda"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "api_key",
                  "type": "string",
                  "optional": false,
                  "label": "Access Key ID",
                  "hint": "Select your AWS account name > Security Credentials > Users. Get API key from existing user or create user (with AWSLambdaFullAccess permission) "
              },
              {
                  "name": "secret_key",
                  "type": "string",
                  "optional": false,
                  "label": "Secret Access Key",
                  "hint": "Select your AWS account name > Security Credentials > Users. Get secret key from existing user or create user (with AWSLambdaFullAccess permission) "
              },
              {
                  "name": "region",
                  "type": "string",
                  "optional": false,
                  "label": "Region",
                  "hint": "If your account url is https://eu-west-1.console.aws.amazon.com then use eu-west-1 as the region"
              }
          ]
      }
```
:::

---
### AWS SNS

**Provider value:**
```json
"provider": "aws_sns"
```

---
### Azure Blob Storage

**Provider value:**
```json
"provider": "azure_blob_storage"
```

---
### Azure Monitor

**Provider value:**
```json
"provider": "azure_monitor"
```

---
### BambooHR

**Provider value:**
```json
"provider": "bamboohr"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "api_token",
                  "type": "string",
                  "label": "API token",
                  "hint": "Can be found at https://[sub domain].bamboohr.com/settings/permissions/api.php"
              },
              {
                  "name": "subdomain",
                  "type": "string",
                  "label": "Sub-domain",
                  "hint": "Your Bamboo HR subdomain is most often your company name"
              }
          ]
      }
```
:::

---
### Basecamp 2

**Provider value:**
```json
"provider": "basecamp"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "account_id",
                  "type": "integer",
                  "label": "Account ID",
                  "hint": "Your account ID is the numeric portion of the browser URL shown when you're logged in. <br>For example, If URL is https://basecamp.com/2551808/, your account ID is 2551808."
              }
          ]
      }
```
:::

---
### Bigtincan

**Provider value:**
```json
"provider": "bigtincan"
```

Connection parameter configuration **_is not required_** for this connector.

---
<h3> Bill.com</h3>

**Provider value:**
```json
"provider": "bill"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "userName",
                  "type": "string",
                  "label": "User name",
                  "hint": "Email ID of the user"
              },
              {
                  "name": "password",
                  "type": "string",
                  "label": "Password",
                  "hint": "Password for login"
              },
              {
                  "name": "orgId",
                  "type": "string",
                  "label": "Organization ID",
                  "hint": "Log in to your Bill.com account, select gear icon, select settings then select profiles under your company.<br>The Organization ID is at the end of the URL, after 'https://www.bill.com/Organization?Id='"
              }
          ]
      }
```
:::

---
### BIM 360

**Provider value:**
```json
"provider": "bim360"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Bitbucket

**Provider value:**
```json
"provider": "bitbucket"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "hostname",
                  "type": "string",
                  "optional": true,
                  "label": "Bitbucket hostname",
                  "hint": "Host (and optional port) of your server. Eg. http://localhost:7990/rest/api"
              }
          ]
      }
```
:::

---
### Box

**Provider value:**
```json
"provider": "box"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "advanced_settings",
                  "type": "object",
                  "optional": true,
                  "label": "Advanced settings",
                  "properties":
                  [
                      {
                          "name": "api_scope",
                          "type": "string",
                          "optional": true,
                          "label": "Requested permissions (Oauth scopes)",
                          "hint": "                     Select <a href=\"https://developer.box.com/docs/scopes\" target=\"_blank\">permissions</a>\n                      to request for this connection. Minimum permissions that will always be requested are: Manage files and folders, groups, and webhooks.\n"
                      }
                  ]
              }
          ]
      }
```
:::

---
### BrickFTP

**Provider value:**
```json
"provider": "brick_ftp"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "api_key",
                  "type": "string",
                  "label": "API Key",
                  "hint": "Enable REST and get key at https://<b>yoursite</b>.brickftp.com/sites/edit?group=api"
              }
          ]
      }
```
:::

---
### Bynder

**Provider value:**
```json
"provider": "bynder"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Callable recipes by Workato

**Provider value:**
```json
"provider": "workato_service"
```

---
### CandidateZip

**Provider value:**
```json
"provider": "candidate_zip"
```

---
### Capsule CRM

**Provider value:**
```json
"provider": "capsulecrm"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "api_token",
                  "type": "string",
                  "label": "API token",
                  "hint": "Can be found at https://(your subdomain).capsulecrm.com/users/api"
              },
              {
                  "name": "subdomain",
                  "type": "string",
                  "label": "Sub-domain",
                  "hint": "Your Capsule CRM subdomain is most often your company name"
              }
          ]
      }
```
:::

---
### Celonis

**Provider value:**
```json
"provider": "celonis"
```

---
### Chargify

**Provider value:**
```json
"provider": "chargify"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "api_key",
                  "type": "string",
                  "label": "API Key",
                  "hint": "Can be generated from the “API Access” tab of your seller dashboard"
              },
              {
                  "name": "subdomain",
                  "type": "string",
                  "label": "Sub-domain",
                  "hint": "Your Chargify subdomain is most often your company name"
              }
          ]
      }
```
:::

---
### Chatter

**Provider value:**
```json
"provider": "chatter"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Cisco Webex Teams

**Provider value:**
```json
"provider": "cisco_spark"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Clearbit

**Provider value:**
```json
"provider": "clearbit"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "api_key",
                  "type": "string",
                  "optional": true,
                  "label": "Api key",
                  "hint": "Can be found here: https://dashboard.clearbit.com/keys"
              }
          ]
      }
```
:::

---
### Cloud Watch

**Provider value:**
```json
"provider": "cloud_watch"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "api_key",
                  "type": "string",
                  "optional": false,
                  "label": "Access Key ID",
                  "hint": "Select your AWS account name-> My Security Credentials-> Users. Get API key from existing user or create user (with Amazon CloudWatch permission) "
              },
              {
                  "name": "secret_key",
                  "type": "string",
                  "optional": false,
                  "label": "Secret Access Key",
                  "hint": "Select your AWS account name-> My Security Credentials-> Users. Get secret key from existing user or create user (with Amazon CloudWatch permission) "
              },
              {
                  "name": "region",
                  "type": "string",
                  "optional": false,
                  "label": "Region",
                  "hint": "If your account url is https://eu-west-1.console.aws.amazon.com then use eu-west-1 as the region"
              }
          ]
      }
```
:::

---
### Codeship

**Provider value:**
```json
"provider": "codeship"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "api_key",
                  "type": "string",
                  "optional": false,
                  "label": "API key",
                  "hint": "Go to My Account->Account settings and get API key"
              }
          ]
      }
```
:::

---
### Collection by Workato

**Provider value:**
```json
"provider": "workato_smart_list"
```

---
### Concur

**Provider value:**
```json
"provider": "concur"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "sandbox",
                  "type": "boolean",
                  "optional": true,
                  "label": "Implementation instance",
                  "hint": "Is this connecting to an implementation instance? <a href=\"https://docs.workato.com/connectors/concur.html\">Learn more</a>.",
                  "default": "false"
              },
              {
                  "name": "user_name",
                  "type": "string",
                  "label": "Username",
                  "hint": "Specify the username or user ID."
              },
              {
                  "name": "password",
                  "type": "string",
                  "label": "Password",
                  "hint": "Password for login."
              },
              {
                  "name": "location",
                  "type": "string",
                  "label": "Location",
                  "hint": "Select the location of your implementation server.",
                  "pick_list":
                  [
                      [
                          "US Implementation",
                          "us-impl"
                      ],
                      [
                          "EU Implementation",
                          "emea-impl"
                      ]
                  ]
              },
              {
                  "name": "client_id",
                  "type": "string",
                  "label": "Client ID",
                  "hint": "Client ID of your implementation application."
              },
              {
                  "name": "client_secret",
                  "type": "string",
                  "label": "Client secret",
                  "hint": "Client secret of your implementation application."
              }
          ]
      }
```
:::

---
### Confluence

**Provider value:**
```json
"provider": "confluence"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "subdomain",
                  "type": "string",
                  "optional": false,
                  "label": "Confluence subdomain",
                  "hint": "Your Jira Service Desk name as found in your URL. For on-premise instances, select an on-prem agent below."
              },
              {
                  "name": "root_uri",
                  "type": "string",
                  "optional": false,
                  "label": "Confluence root URI",
                  "hint": "Root URI (protocol, optional port, hostname) of your Confluence host, for example, http://confluence.intranet.acme.com:7654"
              },
              {
                  "name": "api_token_auth",
                  "type": "number",
                  "optional": true,
                  "label": "API token authentication?",
                  "hint": "Is authentication based on API tokens? If Yes, provide <b>Email</b> & <b>API token</b>. If No, provide <b>Username</b> & <b>Password</b>.",
                  "default": "false"
              },
              {
                  "name": "email",
                  "type": "string",
                  "optional": false,
                  "label": "Email"
              },
              {
                  "name": "apitoken",
                  "type": "string",
                  "optional": false,
                  "label": "API token",
                  "hint": "            Get/create API tokens by going to <a href='https://id.atlassian.com/manage/api-tokens' target='_blank' ><b>id.atlassian.com</b></a> > <b>API tokens</b> > <b>Create API token</b>.\n"
              },
              {
                  "name": "username",
                  "type": "string",
                  "optional": false,
                  "label": "Username",
                  "hint": "Your user name (not email)"
              },
              {
                  "name": "password",
                  "type": "string",
                  "optional": false,
                  "label": "Password"
              }
          ]
      }
```
:::

---
### Confluence (Secondary)

**Provider value:**
```
"provider": "confluence_secondary"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "subdomain",
                  "type": "string",
                  "optional": false,
                  "label": "Confluence subdomain",
                  "hint": "Your Jira Service Desk name as found in your URL. For on-premise instances, select an on-prem agent below."
              },
              {
                  "name": "root_uri",
                  "type": "string",
                  "optional": false,
                  "label": "Confluence root URI",
                  "hint": "Root URI (protocol, optional port, hostname) of your Confluence host, for example, http://confluence.intranet.acme.com:7654"
              },
              {
                  "name": "api_token_auth",
                  "type": "number",
                  "optional": true,
                  "label": "API token authentication?",
                  "hint": "Is authentication based on API tokens? If Yes, provide <b>Email</b> & <b>API token</b>. If No, provide <b>Username</b> & <b>Password</b>.",
                  "default": "false"
              },
              {
                  "name": "email",
                  "type": "string",
                  "optional": false,
                  "label": "Email"
              },
              {
                  "name": "apitoken",
                  "type": "string",
                  "optional": false,
                  "label": "API token",
                  "hint": "            Get/create API tokens by going to <a href='https://id.atlassian.com/manage/api-tokens' target='_blank' ><b>id.atlassian.com</b></a> > <b>API tokens</b> > <b>Create API token</b>.\n"
              },
              {
                  "name": "username",
                  "type": "string",
                  "optional": false,
                  "label": "Username",
                  "hint": "Your user name (not email)"
              },
              {
                  "name": "password",
                  "type": "string",
                  "optional": false,
                  "label": "Password"
              }
          ]
      }
```
:::

---
### Confluent Cloud

**Provider value:**
```json
"provider": "confluent_cloud"
```

---
### Coupa

**Provider value:**
```json
"provider": "coupa"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "host",
                  "type": "string",
                  "optional": false,
                  "label": "Host",
                  "hint": "Enter your Coupa URL.<br>Eg: https://<b>your-instance-name.coupacloud</b>.com"
              },
              {
                  "name": "api_key",
                  "type": "string",
                  "optional": false,
                  "label": "API key",
                  "hint": "Select the <b>Setup</b> tab and select <b>API Keys</b> under <b>Integrations</b> to generate API key.<br>Or go to <b>https://your-instance-name.coupacloud.com/api_keys</b> to generate API key."
              }
          ]
      }
```
:::

---
### CSV by Workato

**Provider value:**

```json
"provider": "csv_parser"
```

---
### cXML

**Provider value:**
```json
"provider": "cxml"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "network_user_id",
                  "type": "string",
                  "label": "Network user ID"
              },
              {
                  "name": "shared_secret",
                  "type": "string",
                  "label": "Shared secret"
              },
              {
                  "name": "buyer_network_user_id",
                  "type": "string",
                  "label": "Buyer network user ID"
              },
              {
                  "name": "purchase_order_url",
                  "type": "string",
                  "label": "Purchase order URL",
                  "hint": "URL for submitting the purchase order cXML",
                  "default": "http://www.workato.com/ariba/purchase_order/1/78"
              }
          ]
      }
```
:::

---
### Deputy

**Provider value:**
```json
"provider": "deputy"
```

Connection parameter configuration **_is not required_** for this connector.

---
### docparser

**Provider value:**
```json
"provider": "docparser"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "api_key",
                  "type": "string",
                  "optional": false,
                  "label": "API Key",
                  "hint": "Go to Account -> API Access to get the API key"
              }
          ]
      }
```
:::

---
### DocuSign

**Provider value:**
```json
"provider": "docusign"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "demo",
                  "type": "boolean",
                  "optional": true,
                  "label": "Demo",
                  "hint": "Is this connecting to a demo account?",
                  "default": "false"
              }
          ]
      }
```
:::


---
### DocuSign (Secondary)

**Provider value:**
```json
"provider": "docusign_secondary"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "demo",
                  "type": "boolean",
                  "optional": true,
                  "label": "Demo",
                  "hint": "Is this connecting to a demo account?",
                  "default": "false"
              }
          ]
      }
```
:::

---
### Dropbox

**Provider value:**
```json
"provider": "dropbox"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Egnyte

**Provider value:**
```json
"provider": "egnyte"
```

---
### Eloqua

**Provider value:**
```json
"provider": "eloqua"
```

---
### Email by Workato

**Provider value:**
```json
"provider": "email"
```

---
### eTapestry

**Provider value:**
```json
"provider": "etapestry"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "loginId",
                  "type": "string",
                  "label": "Login ID"
              },
              {
                  "name": "password",
                  "type": "string",
                  "label": "Password",
                  "hint": "Password for login"
              }
          ]
      }
```
:::

---
### Eventbrite

**Provider value:**
```json
"provider": "event_brite"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Evernote

**Provider value:**
```json
"provider": "evernote"
```

Connection parameter configuration **_is not required_** for this connector.

---
### everydayhero

**Provider value:**
```json
"provider": "everydayhero"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Expensify

**Provider value:**
```json
"provider": "expensify"
```

::: details View connection parameter JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "partner_user_id",
                  "type": "string",
                  "label": "Partner user ID",
                  "hint": "Generate user ID and secret in Expensify <a href=\"https://www.expensify.com/tools/integrations/\">integration settings</a>"
              },
              {
                  "name": "partner_user_secret",
                  "type": "string",
                  "label": "Partner user secret"
              }
          ]
      }
```
:::

---
### Facebook

**Provider value:**
```json
"provider": "facebook"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Fairsail

**Provider value:**
```json
"provider": "fairsail"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "sandbox",
                  "type": "boolean",
                  "optional": true,
                  "label": "Sandbox",
                  "hint": "Is this connecting to a sandbox account?",
                  "default": "false"
              }
          ]
      }
```
:::

---
### Feedly

**Provider value:**
```json
"provider": "feedly"
```

Connection parameter configuration **_is not required_** for this connector.

---
### File tools by Workato

**Provider value:**
```json
"provider": "file_connector"
```

---
### FinancialForce

**Provider value:**
```json
"provider": "financialforce"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "sandbox",
                  "type": "boolean",
                  "optional": true,
                  "label": "Sandbox",
                  "hint": "Is this connecting to a sandbox account?",
                  "default": "false"
              }
          ]
      }
```
:::

<h3> Force.com </h3>

**Provider value:**
```json
"provider": "forcecom"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "sandbox",
                  "type": "boolean",
                  "optional": true,
                  "label": "Sandbox",
                  "hint": "Is this connecting to a sandbox account?",
                  "default": "false"
              }
          ]
      }
```
:::

---
### FreshBooks

**Provider value:**
```json
"provider": "fresh_books"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "auth_token",
                  "type": "string",
                  "label": "Authentication Token",
                  "hint": "From your FreshBooks page, My Account - FreshBooks API"
              },
              {
                  "name": "subdomain",
                  "type": "string",
                  "label": "Subdomain",
                  "hint": "Your account name as it appears in your FreshBooks web address, usually your company name"
              }
          ]
      }
```
:::

---
### Freshdesk

**Provider value:**
```json
"provider": "fresh_desk"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "api_key",
                  "type": "string",
                  "label": "API key",
                  "hint": "You can find the API key under, \"User Profile\" drop-down (top right corner of your helpdesk) > Profile Settings > Your API Key"
              },
              {
                  "name": "help_desk_name",
                  "type": "string",
                  "label": "Helpdesk name",
                  "hint": "yourcompany.freshdesk.com"
              }
          ]
      }
```
:::

---
### FTP/FTPS

**Provider value:**
```json
"provider": "ftps"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "servertype",
                  "type": "string",
                  "label": "Server type",
                  "hint": "Select secure/non-secure FTP as per your FTP server. Make sure you have whitelisted Workato IP addresses. <a href=\"http://docs.workato.com/security.html\" target=\"_blank\">Learn more</a>",
                  "pick_list":
                  [
                      [
                          "FTP-S",
                          "FTP-S"
                      ],
                      [
                          "FTP",
                          "FTP"
                      ]
                  ],
                  "default": "ftp-s"
              },
              {
                  "name": "verify_cert",
                  "type": "boolean",
                  "optional": true,
                  "label": "Verify cert",
                  "hint": "Verify FTPS server certificate"
              },
              {
                  "name": "ftps_conn",
                  "type": "string",
                  "optional": true,
                  "label": "Ftps conn",
                  "hint": "should be defined only for FTP-S",
                  "pick_list":
                  [
                      [
                          "Explicit",
                          "Explicit"
                      ],
                      [
                          "Implicit",
                          "Implicit"
                      ]
                  ]
              },
              {
                  "name": "hostname",
                  "type": "string",
                  "label": "Host name",
                  "hint": "For example, companyname.sampleftp.com"
              },
              {
                  "name": "username",
                  "type": "string",
                  "label": "Username"
              },
              {
                  "name": "password",
                  "type": "string",
                  "label": "Password"
              }
          ]
      }
```
:::

---
### FTP/FTPS (Secondary)

**Provider value:**
```json
"provider": "ftps_secondary"
```

---
### FullContact

**Provider value:**
```json
"provider": "fullcontact"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "apiKey",
                  "type": "string",
                  "label": "API key",
                  "hint": "<a href=\"https://portal.fullcontact.com/admin\" target=\"_blank\" rel=\"noopener\">How do I find my Fullcontact API key?</a>"
              }
          ]
      }
```
:::

---
### Funraise

**Provider value:**
```json
"provider": "funraise"
```

---
### G2

**Provider value:**
```json
"provider": "g2_crowd"
```

---
### GitHub

**Provider value:**
```json
"provider": "github"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Gmail

**Provider value:**
```json
"provider": "gmail"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "read_email_permission",
                  "type": "boolean",
                  "optional": true,
                  "label": "Read email permission",
                  "hint": "Based on Google's updated security policies, Gmail triggers or download attachment\nactions can only be used by paid G Suite account. To use them, enable this setting\nand request your G Suite admin to whitelist the Workato Gmail Connector app and\ngrant it read email permission before linking your GMail account here.\n<a href=\"https://docs.workato.com/connectors/gmail.html\" target=\"_blank\">Learn more</a>\n"
              }
          ]
      }
```
:::

---
<h3> Gong.io </h3>

**Provider value:**
```json
"provider": "gong"
```

---
### Google BigQuery

**Provider value:**
```json
"provider": "google_big_query"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Google Calendar

**Provider value:**
```json
"provider": "google_calendar"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Google Contacts

**Provider value:**
```json
"provider": "google_contacts"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Google Dialogflow

**Provider value:**
```json
"provider": "api_ai_nlu"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "project_name",
                  "type": "string",
                  "optional": true,
                  "label": "Project name",
                  "hint": "Can be found at the generated json file."
              },
              {
                  "name": "client_access_token",
                  "type": "string",
                  "label": "Client access token",
                  "hint": "Create a client access token using this <a target='_blank' href='https://docs.workato.com/connectors/dialogflow.html'>link</a>."
              }
          ]
      }
```
:::

---
### Google Drive

**Provider value:**
```json
"provider": "google_drive"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Google People

**Provider value:**
```json
"provider": "google_people"
```

---
### Google Sheets

**Provider value:**
```json
"provider": "google_sheets"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Google Speech to Text

**Provider value:**
```json
"provider": "google_speech_to_text"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Google Text to Speech

**Provider value:**
```json
"provider": "google_text_to_speech"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Google Translate

**Provider value:**
```json
"provider": "google_translate"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Google Vision

**Provider value:**
```json
"provider": "google_vision"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Google Workspace

**Provider value:**
```json
"provider": "google_workspace"
```

---
### Goombal

**Provider value:**
```json
"provider": "goombal"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "Email",
                  "type": "string",
                  "label": "Email"
              },
              {
                  "name": "Password",
                  "type": "string",
                  "label": "Password"
              },
              {
                  "name": "instance",
                  "type": "string",
                  "optional": true,
                  "label": "Instance",
                  "hint": "Leave empty to default to <b>app</b>"
              }
          ]
      }
```
:::

---
### GotoWebinar

**Provider value:**
```json
"provider": "goto_webinar"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Greenhouse

**Provider value:**
```json
"provider": "greenhouse"
```

---
### HipChat

**Provider value:**
```json
"provider": "hipchat"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "subdomain",
                  "type": "string",
                  "optional": false,
                  "label": "Subdomain",
                  "hint": "If your HipChat url is https://abc.hipchat.com, then subdomain is 'abc'"
              },
              {
                  "name": "auth_token",
                  "type": "string",
                  "optional": false,
                  "label": "Access token",
                  "hint": "Go to yourdomain.hipchat.com/account/api and create new token. Select \"View Group\" or \"View Room\" as one of the scopes"
              }
          ]
      }
```
:::

---
### HTTP (OAuth2)

**Provider value:**
```json
"provider": "rest_oauth"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "oauth2_auth_url",
                  "type": "string",
                  "label": "OAuth2 auth URL",
                  "hint": "Use <b>https://www.workato.com/oauth/callback</b> as callback url. <a href='https://docs.workato.com/developing-connectors/http/connection-setup.html#authentication-type-oauth2-authorization-code-grant'\n                                    target='_blank'>Learn how to authenticate</a>"
              },
              {
                  "name": "oauth2_token_url",
                  "type": "string",
                  "label": "OAuth2 token URL"
              },
              {
                  "name": "oauth2_client_id",
                  "type": "string",
                  "label": "OAuth2 client ID"
              },
              {
                  "name": "oauth2_client_secret",
                  "type": "string",
                  "label": "OAuth2 client secret"
              }
          ]
      }
```
:::

---
### HTTP

**Provider value:**
```json
"provider": "rest"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "auth_type",
                  "type": "string",
                  "label": "Authentication type",
                  "hint": "Select an authentication method. <a href=\"https://docs.workato.com/developing-connectors/http/connection-setup.html\" target=\"_blank\">Learn how to authenticate</a>",
                  "pick_list":
                  [
                      [
                          "None",
                          "no_auth"
                      ],
                      [
                          "Basic",
                          "basic"
                      ],
                      [
                          "Header auth",
                          "headers"
                      ],
                      [
                          "Query params",
                          "query"
                      ],
                      [
                          "On-prem NTLM",
                          "ntlm"
                      ],
                      [
                          "OAuth 2 (authorization code grant)",
                          "oauth2_auth_code_grant"
                      ],
                      [
                          "OAuth 2 (client credentials grant)",
                          "oauth2_client_credentials_grant"
                      ],
                      [
                          "Custom",
                          "custom"
                      ]
                  ]
              },
              {
                  "name": "profile",
                  "type": "string",
                  "label": "On-prem NTLM profile",
                  "hint": "NTLM Profile name given in the on-prem agent's <b>config.yml</b> file."
              },
              {
                  "name": "basic_user",
                  "type": "string",
                  "optional": true,
                  "label": "Basic auth user"
              },
              {
                  "name": "basic_password",
                  "type": "string",
                  "optional": true,
                  "label": "Basic auth password"
              },
              {
                  "name": "header_pair",
                  "type": "string",
                  "optional": true,
                  "label": "Header authorization",
                  "hint": "Add custom auth headers, one per line, for example, <b>X-API-Token: secret42</b>"
              },
              {
                  "name": "url_param",
                  "type": "string",
                  "optional": true,
                  "label": "GET-params authorization",
                  "hint": "Add custom GET parameters, one per line, for example, <b>token=secret42</b>"
              },
              {
                  "name": "oauth2_auth_url",
                  "type": "string",
                  "label": "OAuth2 authorization URL",
                  "hint": "Use <b>https://www.workato.com/oauth/callback</b> as callback url. Use <b>response_type=code</b> as param, if needed. <a href='https://docs.workato.com/developing-connectors/http/connection-setup.html#authentication-type-oauth2-authorization-code-grant'\n                 target='_blank'>Learn how to authenticate</a>"
              },
              {
                  "name": "oauth2_token_url",
                  "type": "string",
                  "label": "OAuth2 token URL"
              },
              {
                  "name": "oauth2_client_id",
                  "type": "string",
                  "label": "OAuth2 client ID"
              },
              {
                  "name": "oauth2_client_secret",
                  "type": "string",
                  "label": "OAuth2 client secret"
              },
              {
                  "name": "param_type",
                  "type": "string",
                  "optional": true,
                  "label": "How does the API require credentials to be sent to request a token?",
                  "hint": "Send client ID and secret in token request body or as a base64 encoded string in the header?",
                  "pick_list":
                  [
                      [
                          "Header",
                          "basic"
                      ],
                      [
                          "Body",
                          "payload"
                      ]
                  ]
              },
              {
                  "name": "ssl_params",
                  "type": "boolean",
                  "optional": true,
                  "label": "Use client SSL certificate",
                  "default": "false"
              },
              {
                  "name": "ssl_client_cert",
                  "type": "string",
                  "optional": true,
                  "label": "SSL client certificate"
              },
              {
                  "name": "ssl_client_key",
                  "type": "string",
                  "optional": true,
                  "label": "SSL client key"
              },
              {
                  "name": "ssl_ca_cert",
                  "type": "string",
                  "optional": true,
                  "label": "Custom CA certificate"
              }
          ]
      }
```
:::

---
### HTTP (Secondary)

**Provider value:**
```json
"provider": "rest_secondary"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "auth_type",
                  "type": "string",
                  "label": "Authentication type",
                  "hint": "Select an authentication method. <a href=\"https://docs.workato.com/developing-connectors/http/connection-setup.html\" target=\"_blank\">Learn how to authenticate</a>",
                  "pick_list":
                  [
                      [
                          "None",
                          "no_auth"
                      ],
                      [
                          "Basic",
                          "basic"
                      ],
                      [
                          "Header auth",
                          "headers"
                      ],
                      [
                          "Query params",
                          "query"
                      ],
                      [
                          "On-prem NTLM",
                          "ntlm"
                      ],
                      [
                          "OAuth 2 (authorization code grant)",
                          "oauth2_auth_code_grant"
                      ],
                      [
                          "OAuth 2 (client credentials grant)",
                          "oauth2_client_credentials_grant"
                      ],
                      [
                          "Custom",
                          "custom"
                      ]
                  ]
              },
              {
                  "name": "profile",
                  "type": "string",
                  "label": "On-prem NTLM profile",
                  "hint": "NTLM Profile name given in the on-prem agent's <b>config.yml</b> file."
              },
              {
                  "name": "basic_user",
                  "type": "string",
                  "optional": true,
                  "label": "Basic auth user"
              },
              {
                  "name": "basic_password",
                  "type": "string",
                  "optional": true,
                  "label": "Basic auth password"
              },
              {
                  "name": "header_pair",
                  "type": "string",
                  "optional": true,
                  "label": "Header authorization",
                  "hint": "Add custom auth headers, one per line, for example, <b>X-API-Token: secret42</b>"
              },
              {
                  "name": "url_param",
                  "type": "string",
                  "optional": true,
                  "label": "GET-params authorization",
                  "hint": "Add custom GET parameters, one per line, for example, <b>token=secret42</b>"
              },
              {
                  "name": "oauth2_auth_url",
                  "type": "string",
                  "label": "OAuth2 authorization URL",
                  "hint": "Use <b>https://www.workato.com/oauth/callback</b> as callback url. Use <b>response_type=code</b> as param, if needed. <a href='https://docs.workato.com/developing-connectors/http/connection-setup.html#authentication-type-oauth2-authorization-code-grant'\n                 target='_blank'>Learn how to authenticate</a>"
              },
              {
                  "name": "oauth2_token_url",
                  "type": "string",
                  "label": "OAuth2 token URL"
              },
              {
                  "name": "oauth2_client_id",
                  "type": "string",
                  "label": "OAuth2 client ID"
              },
              {
                  "name": "oauth2_client_secret",
                  "type": "string",
                  "label": "OAuth2 client secret"
              },
              {
                  "name": "param_type",
                  "type": "string",
                  "optional": true,
                  "label": "How does the API require credentials to be sent to request a token?",
                  "hint": "Send client ID and secret in token request body or as a base64 encoded string in the header?",
                  "pick_list":
                  [
                      [
                          "Header",
                          "basic"
                      ],
                      [
                          "Body",
                          "payload"
                      ]
                  ]
              },
              {
                  "name": "ssl_params",
                  "type": "boolean",
                  "optional": true,
                  "label": "Use client SSL certificate",
                  "default": "false"
              },
              {
                  "name": "ssl_client_cert",
                  "type": "string",
                  "optional": true,
                  "label": "SSL client certificate"
              },
              {
                  "name": "ssl_client_key",
                  "type": "string",
                  "optional": true,
                  "label": "SSL client key"
              },
              {
                  "name": "ssl_ca_cert",
                  "type": "string",
                  "optional": true,
                  "label": "Custom CA certificate"
              }
          ]
      }
```
:::

---
### HubSpot

**Provider value:**
```json
"provider": "hubspot"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "advanced_settings",
                  "type": "object",
                  "optional": true,
                  "label": "Advanced settings",
                  "properties":
                  [
                      {
                          "name": "scopes",
                          "type": "string",
                          "optional": true,
                          "label": "Scopes",
                          "hint": "               Select the areas of HubSpot this connection will have access to. Selecting scopes which your HubSpot account does not have access to will result in an error. Our default selection should be enough when working with contacts, companies, and deals.\n",
                          "default": "contacts"
                      }
                  ]
              }
          ]
      }
```
:::

---
### IBM Watson Workspace

**Provider value:**
```json
"provider": "ibm_workspace"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Infusionsoft

**Provider value:**
```json
"provider": "infusionsoft"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Insightly

**Provider value:**
```json
"provider": "insightly"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "api_key",
                  "type": "string",
                  "label": "Api key",
                  "hint": "Click the drop-down at the top right corner of the home page. API KEY found under the 'User settings'"
              }
          ]
      }
```
:::

---
### Instagram

**Provider value:**
```json
"provider": "instagram"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Intercom

**Provider value:**
```json
"provider": "intercom"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "user_ids",
                  "type": "string",
                  "optional": true,
                  "label": "Example user IDs",
                  "hint": "                   Provide comma separated Intercom user IDs, for example, <b>54253</b>, for Workato to retrieve the custom fields set up for these users.\n                   Maximum of <b>3</b> user IDs can be provided.\n"
              }
          ]
      }
```
:::

---
### JavaScript

**Provider value:**
```json
"provider": "js_eval"
```

---
### JDBC

**Provider value:**
```json
"provider": "jdbc"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "profile",
                  "type": "string",
                  "label": "On-prem connection profile"
              },
              {
                  "name": "schema_name",
                  "type": "string",
                  "optional": true,
                  "label": "Schema"
              }
          ]
      }
```
:::

---
### JDBC (Secondary)

**Provider value:**
```json
"provider": "jdbc_secondary"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "profile",
                  "type": "string",
                  "label": "On-prem connection profile"
              },
              {
                  "name": "schema_name",
                  "type": "string",
                  "optional": true,
                  "label": "Schema"
              }
          ]
      }
```
:::

---
### Jenkins

**Provider value:**
```json
"provider": "jenkins"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "root_uri",
                  "type": "string",
                  "optional": false,
                  "label": "Jenkins root URI",
                  "hint": "                  Host (and optional port) of your Jenkins server. Eg. http://workato-jenkins.<br>\n                  Go to Manage Jenkins-> Configure Global Security. Uncheck <b>Prevent Cross Site Request Forgery exploits</b>.\n"
              },
              {
                  "name": "username",
                  "type": "string",
                  "optional": false,
                  "label": "Username"
              },
              {
                  "name": "password",
                  "type": "string",
                  "optional": false,
                  "label": "Password"
              }
          ]
      }
```
:::

---
### Jira
**Provider value:**
```json
"provider": "jira"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "host_name",
                  "type": "string",
                  "label": "Host name",
                  "hint": "Refer to the URL of your Jira account and complete the above URL. For example, <b>workato.atlassian.net</b>"
              },
              {
                  "name": "host_url",
                  "type": "string",
                  "label": "Host name with protocol",
                  "hint": "Refer to the URL of your Jira account and specify the above URL.<br>for example, <b>http://workato.atlassian.net</b>"
              },
              {
                  "name": "auth_type",
                  "type": "string",
                  "label": "Authentication Type",
                  "hint": "Select an authentication method",
                  "pick_list":
                  [
                    [
                      "API Token",
                      "api_token"
                    ],
                    [
                      "OAuth 2.0",
                      "oauth"
                    ]
                  ]
              },
              {
                  "name": "email",
                  "type": "string",
                  "optional": true,
                  "label": "Email"
              },
              {
                  "name": "apitoken",
                  "type": "string",
                  "optional": true,
                  "label": "API token",
                  "hint": "             Get/create API tokens by going to <a href='https://id.atlassian.com' target='_blank' ><b>id.atlassian.com</b></a> > <b>API tokens</b> > <b>Create API token</b>.\n"
              }
          ]
      }
```
:::

---
### Jira (Secondary)

**Provider value:**
```json
"provider": "jira_secondary"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "host_name",
                  "type": "string",
                  "label": "Host name",
                  "hint": "Refer to the URL of your Jira account and complete the above URL. For example, <b>workato.atlassian.net</b>"
              },
              {
                  "name": "host_url",
                  "type": "string",
                  "label": "Host name with protocol",
                  "hint": "Refer to the URL of your Jira account and specify the above URL.<br>for example, <b>http://workato.atlassian.net</b>"
              },
              {
                  "name": "auth_type",
                  "type": "string",
                  "label": "Authentication Type",
                  "hint": "Select an authentication method",
                  "pick_list":
                  [
                    [
                      "API Token",
                      "api_token"
                    ]
                  ]
              },
              {
                  "name": "email",
                  "type": "string",
                  "optional": true,
                  "label": "Email"
              },
              {
                  "name": "apitoken",
                  "type": "string",
                  "optional": true,
                  "label": "API token",
                  "hint": "             Get/create API tokens by going to <a href='https://id.atlassian.com' target='_blank' ><b>id.atlassian.com</b></a> > <b>API tokens</b> > <b>Create API token</b>.\n"
              }
          ]
      }
```
:::


---
### JIRA Service Desk

**Provider value:**
```json
"provider": "jira_service_desk"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "host_name",
                  "type": "string",
                  "label": "Host name",
                  "hint": "Refer to the URL of your Jira account and complete the above URL. For example, <b>workato.atlassian.net</b>"
              },
              {
                  "name": "host_url",
                  "type": "string",
                  "label": "Host name with protocol",
                  "hint": "Refer to the URL of your Jira account and specify the above URL.<br>for example, <b>http://workato.atlassian.net</b>"
              },
              {
                  "name": "api_token_auth",
                  "type": "boolean",
                  "label": "API token authentication?",
                  "hint": "Is authentication based on API tokens? If Yes, provide <b>Email</b> & <b>API token</b>. If No, provide <b>Username</b> & <b>Password</b>.",
                  "default": "false"
              },
              {
                  "name": "email",
                  "type": "string",
                  "optional": true,
                  "label": "Email"
              },
              {
                  "name": "apitoken",
                  "type": "string",
                  "optional": true,
                  "label": "API token",
                  "hint": "             Get/create API tokens by going to <a href='https://id.atlassian.com' target='_blank' ><b>id.atlassian.com</b></a> > <b>API tokens</b> > <b>Create API token</b>.\n"
              }
          ]
      }
```
:::


---
### JMS

**Provider value:**
```json
"provider": "jms"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "profile",
                  "type": "string",
                  "label": "On-prem JMS connection profile"
              }
          ]
      }
```
:::

---
### JobScience

**Provider value:**
```json
"provider": "jobscience"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "sandbox",
                  "type": "boolean",
                  "optional": true,
                  "label": "Sandbox",
                  "hint": "Is this connecting to a sandbox account?",
                  "default": "false"
              }
          ]
      }
```
:::

---
### Jobvite

**Provider value:**
```json
"provider": "jobvite"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "api_key",
                  "type": "string",
                  "label": "API Key",
                  "hint": "Enter the <b>Api Key</b> from jobvite."
              },
              {
                  "name": "secret",
                  "type": "string",
                  "label": "Secret",
                  "hint": "Enter the <b>Secret</b> from jobvite."
              },
              {
                  "name": "use_staging",
                  "type": "boolean",
                  "label": "Use Staging",
                  "hint": "If selected, staging jobvite instance will be used",
                  "default": "false"
              },
              {
                  "name": "use_v2",
                  "type": "boolean",
                  "optional": true,
                  "label": "Use V2 API",
                  "hint": "If selected, V2 version will be used",
                  "default": "false"
              }
          ]
      }
```
:::

---
### JSON parser by Workato

**Provider value:**
```json
"provider": "json_parser"
```

---
### JSON Web Token (JWT)

**Provider value:**
```json
"provider": "jwt"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "alg",
                  "type": "string",
                  "label": "Signing algorithm",
                  "hint": "Select the JWT signing algorithm",
                  "pick_list":
                  [
                      [
                          "HMAC using SHA-256",
                          "HS256"
                      ],
                      [
                          "HMAC using SHA-384",
                          "HS384"
                      ],
                      [
                          "HMAC using SHA-512",
                          "HS512"
                      ],
                      [
                          "RSA using SHA-256",
                          "RS256"
                      ],
                      [
                          "RSA using SHA-384",
                          "RS384"
                      ],
                      [
                          "RSA using SHA-512",
                          "RS512"
                      ]
                  ],
                  "default": "HS256"
              },
              {
                  "name": "hmac_secret",
                  "type": "string",
                  "optional": true,
                  "label": "HMAC shared secret",
                  "hint": "Enter the shared HMAC secret(min 32 characters)"
              },
              {
                  "name": "public_key",
                  "type": "string",
                  "optional": true,
                  "label": "Public key",
                  "hint": "                                Learn how to generate a pair of Public key and Private key\n                                <a href=\"https://docs.workato.com/features/pgp-encryption.html\" target=\"_blank\">here</a>.\n"
              },
              {
                  "name": "private_key",
                  "type": "string",
                  "optional": true,
                  "label": "Private key",
                  "hint": "                                 Learn how to generate a pair of Public key and Private key\n                                 <a href=\"https://docs.workato.com/features/pgp-encryption.html\" target=\"_blank\">here</a>.\n"
              },
              {
                  "name": "passphrase",
                  "type": "string",
                  "optional": true,
                  "label": "Passphrase",
                  "hint": "Passphrase for encrypted private key"
              }
          ]
      }
```
:::

---
### JumpCloud

**Provider value:**
```json
"provider": "jump_cloud"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "api_key",
                  "type": "string",
                  "optional": false,
                  "label": "API key",
                  "hint": "Click <a href='https://docs.jumpcloud.com/2.0/authentication-and-authorization/authentication-and-authorization-overview#access-your-api-key' target='_blank'>here</a> to get API key."
              },
              {
                  "name": "org_id",
                  "type": "string",
                  "optional": true,
                  "label": "Organization ID",
                  "hint": "<span class='provider'>Organization ID </span> is required for all multi-tenant admins. Click <a href='https://docs.jumpcloud.com/2.0/authentication-and-authorization/multi-tenant-organization-api-headers#to-obtain-an-individual-organization-id-via-the-ui' target='_blank'>here</a> to get Organization ID."
              }
          ]
      }
```
:::

---
### Kenandy

**Provider value:**
```json
"provider": "kenandy"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "sandbox",
                  "type": "boolean",
                  "optional": true,
                  "label": "Sandbox",
                  "hint": "Is this connecting to a sandbox account?",
                  "default": "false"
              }
          ]
      }
```
:::

---
### Kizen

**Provider value:**
```json
"provider": "kizen"
```

---
### Knack
**Provider value:**
```json
"provider": "knack"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "app_id",
                  "type": "string",
                  "optional": false,
                  "label": "Application ID",
                  "hint": "Hover over gear icon, Select API & Code -> get Application ID"
              },
              {
                  "name": "api_key",
                  "type": "string",
                  "optional": false,
                  "label": "API Key",
                  "hint": "Hover over gear icon, Select API & Code -> get API Key"
              }
          ]
      }
```
:::

---
### Librato

**Provider value:**
```json
"provider": "librato"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "username",
                  "type": "string",
                  "optional": false,
                  "label": "Username",
                  "hint": "Go to Account Settings->API Token. GET token. eg: abc@efg.com"
              },
              {
                  "name": "password",
                  "type": "string",
                  "optional": false,
                  "label": "Password or personal API key",
                  "hint": "If its API key, Go to Account Settings->API Token. GET API Key"
              }
          ]
      }
```
:::

---
### LinkedIn

**Provider value:**
```json
"provider": "linkedin"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Linked objects by Workato

**Provider value:**
```json
"provider": "linked_objects"
```

---
### Lists by Workato

**Provider value:**
```json
"provider": "workato_list"
```

---
### Logger by Workato

**Provider value:**
```json
"provider": "logger"
```

---
### Lookup tables by Workato

**Provider value:**
```json
"provider": "lookup_table"
```

---
### Magento 2

**Provider value:**
```json
"provider": "magento"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "server",
                  "type": "string",
                  "optional": false,
                  "label": "Server domain",
                  "hint": "Enter your full URL, for example, <b>http://mymagentostore.com</b>"
              },
              {
                  "name": "username",
                  "type": "string",
                  "optional": false,
                  "label": "Username",
                  "hint": "If account type is admin, enter username. Otherwise, enter email address"
              },
              {
                  "name": "account_type",
                  "type": "string",
                  "optional": false,
                  "label": "Account type",
                  "hint": "Select if your connected account is an admin or non-admin account",
                  "pick_list":
                  [
                      [
                          "admin",
                          "admin"
                      ],
                      [
                          "customer",
                          "customer"
                      ]
                  ]
              },
              {
                  "name": "password",
                  "type": "string",
                  "optional": false,
                  "label": "Password"
              }
          ]
      }
```
:::

---
### MailChimp

**Provider value:**
```json
"provider": "mailchimp"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Mapper by Workato

**Provider value:**
```json
"provider": "workato_mapper"
```

---
### Marketo

**Provider value:**
```json
"provider": "marketo"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "endpoint",
                  "type": "string",
                  "label": "REST Endpoint",
                  "hint": "Admin/Web Services/REST API - more <a href=\"http://developers.marketo.com/documentation/rest/endpoint-url/\">here</a>."
              },
              {
                  "name": "client_id",
                  "type": "string",
                  "label": "Custom Service client ID",
                  "hint": "To create a Marketo custom service see <a href=\"http://developers.marketo.com/documentation/rest/custom-service/\">this</a>."
              },
              {
                  "name": "client_secret",
                  "type": "string",
                  "label": "Custom Service client secret"
              }
          ]
      }
```
:::

---
### Marketo (Secondary)

**Provider value:**
```json
"provider": "marketo_secondary"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "endpoint",
                  "type": "string",
                  "label": "REST Endpoint",
                  "hint": "Admin/Web Services/REST API - more <a href=\"http://developers.marketo.com/documentation/rest/endpoint-url/\">here</a>."
              },
              {
                  "name": "client_id",
                  "type": "string",
                  "label": "Custom Service client ID",
                  "hint": "To create a Marketo custom service see <a href=\"http://developers.marketo.com/documentation/rest/custom-service/\">this</a>."
              },
              {
                  "name": "client_secret",
                  "type": "string",
                  "label": "Custom Service client secret"
              }
          ]
      }
```
:::

---
### Message template by Workato

**Provider value:**
```json
"provider": "workato_template"
```

---
### Microsoft Dynamics 365

**Provider value:**
```json
"provider": "microsoft_dynamics_crm"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "subdomain",
                  "type": "string",
                  "label": "Subdomain",
                  "hint": "             If your Microsoft Dynamics 365 URL is <b>https://abc.crm.dynamics.com</b>,\n             subdomain will be <b>abc.crm.dynamics.com</b>\n"
              },
              {
                  "name": "account_type",
                  "type": "string",
                  "label": "Account type",
                  "pick_list":
                  [
                      [
                          "On premise",
                          "onpremises"
                      ],
                      [
                          "Cloud",
                          "online"
                      ]
                  ]
              },
              {
                  "name": "adfs_name",
                  "type": "string",
                  "optional": true,
                  "label": "AD domain name",
                  "hint": "             Requires, if the account type is 'On premise'.\n             If your AD server is <b>https://abc.adfs.dynamics.com/adfs</b>, AD domain name will be <b>abc.adfs.dynamics.com</b>\n"
              },
              {
                  "name": "client_id",
                  "type": "string",
                  "label": "Client ID",
                  "hint": "Click <a target='_blank' href=http://docs.workato.com/connectors/dynamics-crm.html>here</a> to know how to get client ID"
              },
              {
                  "name": "client_secret",
                  "type": "string",
                  "optional": true,
                  "label": "Client secret"
              }
          ]
      }
```
:::

---
### Microsoft Sharepoint

**Provider value:**
```json
"provider": "microsoft_sharepoint"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "subdomain",
                  "type": "string",
                  "optional": false,
                  "label": "Subdomain",
                  "hint": "Enter your SharePoint subdomain as found in your SharePoint URL. If your SharePoint URL is <b>https://abc.sharepoint.com</b>, then subdomain is <b>abc</b>"
              },
              {
                  "name": "domain",
                  "type": "string",
                  "label": "Domain",
                  "hint": "Enter full URL of your SharePoint domain. <b>for example, https://company-name.sharepoint.com</b>."
              },
              {
                  "name": "client_id",
                  "type": "string",
                  "optional": true,
                  "label": "Client ID",
                  "hint": "<a href='https://docs.workato.com/connectors/sharepoint.html' target='_blank'>Click here</a> to learn how to generate Client ID and Client secret."
              },
              {
                  "name": "client_secret",
                  "type": "string",
                  "optional": true,
                  "label": "Client secret",
                  "hint": "<a href='https://docs.workato.com/connectors/sharepoint.html' target='_blank'>Click here</a> to learn how to generate Client ID and Client secret."
              },
              {
                  "name": "connection_siteurl",
                  "type": "string",
                  "optional": true,
                  "label": "Site name",
                  "hint": "                  The name of the SharePoint site you want to connect to. Use this field if you only have access to that specific site, but not the home site.\n                  If left blank, Workato will connect to your default home site.\n                  Use the site name as found in the URL of site page. eg. If the URL is <b>https://company-name.sharepoint.com/sites/product</b>, then use <b>product</b>.\n"
              }
          ]
      }
```
:::

---
### Miro

**Provider value:**
```json
"provider": "miro_board"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "client_id",
                  "type": "string",
                  "optional": false,
                  "label": "Client ID"
              },
              {
                  "name": "client_secret",
                  "type": "string",
                  "optional": false,
                  "label": "Client secret"
              }
          ]
      }
```
:::

---
### Mixpanel

**Provider value:**
```json
"provider": "mixpanel"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "api_key",
                  "type": "string",
                  "label": "Api key",
                  "hint": "Can be found in your account menu within the projects tab"
              },
              {
                  "name": "api_secret",
                  "type": "string",
                  "label": "Api secret",
                  "hint": "Can be found in your account menu within the projects tab"
              }
          ]
      }
```
:::

---
### MySQL

**Provider value:**
```json
"provider": "mysql"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "profile",
                  "type": "string",
                  "label": "On-prem connection profile"
              },
              {
                  "name": "username",
                  "type": "string",
                  "label": "Username"
              },
              {
                  "name": "password",
                  "type": "string",
                  "label": "Password"
              },
              {
                  "name": "host",
                  "type": "string",
                  "label": "Host"
              },
              {
                  "name": "port",
                  "type": "string",
                  "label": "Port"
              },
              {
                  "name": "database",
                  "type": "string",
                  "label": "Database"
              }
          ]
      }
```
:::

---
### MySQL (Secondary)

**Provider value:**
```json
"provider": "mysql_secondary"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "profile",
                  "type": "string",
                  "label": "On-prem connection profile"
              },
              {
                  "name": "username",
                  "type": "string",
                  "label": "Username"
              },
              {
                  "name": "password",
                  "type": "string",
                  "label": "Password"
              },
              {
                  "name": "host",
                  "type": "string",
                  "label": "Host"
              },
              {
                  "name": "port",
                  "type": "string",
                  "label": "Port"
              },
              {
                  "name": "database",
                  "type": "string",
                  "label": "Database"
              }
          ]
      }
```
:::

---
### Namely

**Provider value:**
```json
"provider": "namely"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "company",
                  "type": "string",
                  "label": "Company",
                  "hint": "If your Namely url is https://acme.namely.com then use <b>acme</b> as value."
              }
          ]
      }
```
:::

---
### NationBuilder

**Provider value:**
```json
"provider": "nationbuilder"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "slug",
                  "type": "string",
                  "label": "Nation",
                  "hint": "Your NationBuilder \"nation\", for example, <b>voteforpedro</b>.nationbuilder.com"
              }
          ]
      }
```
:::

---
### NetSuite

**Provider value:**
```json
"provider": "netsuite"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "account",
                  "type": "string",
                  "label": "Account ID",
                  "hint": "Login as Administrator, then in <b>Setup Menu</b>, find in <b>Integration</b> > <b>Web Services Preferences</b>"
              },
              {
                  "name": "tokenId",
                  "type": "string",
                  "label": "Token ID"
              },
              {
                  "name": "tokenSecret",
                  "type": "string",
                  "label": "Token secret"
              },
              {
                  "name": "timezone",
                  "type": "string",
                  "optional": true,
                  "label": "Account timezone",
                  "hint": "Needed for consistency with NetSuite - pick same as your NetSuite profile",
                  "pick_list":
                  [
                      [
                          "American Samoa (-11:00)",
                          "American Samoa"
                      ],
                      [
                          "International Date Line West (-11:00)",
                          "International Date Line West"
                      ],
                      [
                          "Midway Island (-11:00)",
                          "Midway Island"
                      ],
                      [
                          "Hawaii (-10:00)",
                          "Hawaii"
                      ],
                      [
                          "Alaska (-9:00)",
                          "Alaska"
                      ],
                      [
                          "Pacific Time (US & Canada) (-8:00)",
                          "Pacific Time (US & Canada)"
                      ],
                      [
                          "Tijuana (-8:00)",
                          "Tijuana"
                      ],
                      [
                          "Arizona (-7:00)",
                          "Arizona"
                      ],
                      [
                          "Chihuahua (-7:00)",
                          "Chihuahua"
                      ],
                      [
                          "Mazatlan (-7:00)",
                          "Mazatlan"
                      ],
                      [
                          "Mountain Time (US & Canada) (-7:00)",
                          "Mountain Time (US & Canada)"
                      ],
                      [
                          "Central America (-6:00)",
                          "Central America"
                      ],
                      [
                          "Central Time (US & Canada) (-6:00)",
                          "Central Time (US & Canada)"
                      ],
                      [
                          "Guadalajara (-6:00)",
                          "Guadalajara"
                      ],
                      [
                          "Mexico City (-6:00)",
                          "Mexico City"
                      ],
                      [
                          "Monterrey (-6:00)",
                          "Monterrey"
                      ],
                      [
                          "Saskatchewan (-6:00)",
                          "Saskatchewan"
                      ],
                      [
                          "Bogota (-5:00)",
                          "Bogota"
                      ],
                      [
                          "Eastern Time (US & Canada) (-5:00)",
                          "Eastern Time (US & Canada)"
                      ],
                      [
                          "Indiana (East) (-5:00)",
                          "Indiana (East)"
                      ],
                      [
                          "Lima (-5:00)",
                          "Lima"
                      ],
                      [
                          "Quito (-5:00)",
                          "Quito"
                      ],
                      [
                          "Atlantic Time (Canada) (-4:00)",
                          "Atlantic Time (Canada)"
                      ],
                      [
                          "Caracas (-4:00)",
                          "Caracas"
                      ],
                      [
                          "Georgetown (-4:00)",
                          "Georgetown"
                      ],
                      [
                          "La Paz (-4:00)",
                          "La Paz"
                      ],
                      [
                          "Santiago (-4:00)",
                          "Santiago"
                      ],
                      [
                          "Newfoundland (-4:30)",
                          "Newfoundland"
                      ],
                      [
                          "Brasilia (-3:00)",
                          "Brasilia"
                      ],
                      [
                          "Buenos Aires (-3:00)",
                          "Buenos Aires"
                      ],
                      [
                          "Greenland (-3:00)",
                          "Greenland"
                      ],
                      [
                          "Montevideo (-3:00)",
                          "Montevideo"
                      ],
                      [
                          "Mid-Atlantic (-2:00)",
                          "Mid-Atlantic"
                      ],
                      [
                          "Azores (-1:00)",
                          "Azores"
                      ],
                      [
                          "Cape Verde Is. (-1:00)",
                          "Cape Verde Is."
                      ],
                      [
                          "Casablanca (+0:00)",
                          "Casablanca"
                      ],
                      [
                          "Dublin (+0:00)",
                          "Dublin"
                      ],
                      [
                          "Edinburgh (+0:00)",
                          "Edinburgh"
                      ],
                      [
                          "Lisbon (+0:00)",
                          "Lisbon"
                      ],
                      [
                          "London (+0:00)",
                          "London"
                      ],
                      [
                          "Monrovia (+0:00)",
                          "Monrovia"
                      ],
                      [
                          "UTC (+0:00)",
                          "UTC"
                      ],
                      [
                          "Amsterdam (+1:00)",
                          "Amsterdam"
                      ],
                      [
                          "Belgrade (+1:00)",
                          "Belgrade"
                      ],
                      [
                          "Berlin (+1:00)",
                          "Berlin"
                      ],
                      [
                          "Bern (+1:00)",
                          "Bern"
                      ],
                      [
                          "Bratislava (+1:00)",
                          "Bratislava"
                      ],
                      [
                          "Brussels (+1:00)",
                          "Brussels"
                      ],
                      [
                          "Budapest (+1:00)",
                          "Budapest"
                      ],
                      [
                          "Copenhagen (+1:00)",
                          "Copenhagen"
                      ],
                      [
                          "Ljubljana (+1:00)",
                          "Ljubljana"
                      ],
                      [
                          "Madrid (+1:00)",
                          "Madrid"
                      ],
                      [
                          "Paris (+1:00)",
                          "Paris"
                      ],
                      [
                          "Prague (+1:00)",
                          "Prague"
                      ],
                      [
                          "Rome (+1:00)",
                          "Rome"
                      ],
                      [
                          "Sarajevo (+1:00)",
                          "Sarajevo"
                      ],
                      [
                          "Skopje (+1:00)",
                          "Skopje"
                      ],
                      [
                          "Stockholm (+1:00)",
                          "Stockholm"
                      ],
                      [
                          "Vienna (+1:00)",
                          "Vienna"
                      ],
                      [
                          "Warsaw (+1:00)",
                          "Warsaw"
                      ],
                      [
                          "West Central Africa (+1:00)",
                          "West Central Africa"
                      ],
                      [
                          "Zagreb (+1:00)",
                          "Zagreb"
                      ],
                      [
                          "Athens (+2:00)",
                          "Athens"
                      ],
                      [
                          "Bucharest (+2:00)",
                          "Bucharest"
                      ],
                      [
                          "Cairo (+2:00)",
                          "Cairo"
                      ],
                      [
                          "Harare (+2:00)",
                          "Harare"
                      ],
                      [
                          "Helsinki (+2:00)",
                          "Helsinki"
                      ],
                      [
                          "Jerusalem (+2:00)",
                          "Jerusalem"
                      ],
                      [
                          "Kaliningrad (+2:00)",
                          "Kaliningrad"
                      ],
                      [
                          "Kyiv (+2:00)",
                          "Kyiv"
                      ],
                      [
                          "Pretoria (+2:00)",
                          "Pretoria"
                      ],
                      [
                          "Riga (+2:00)",
                          "Riga"
                      ],
                      [
                          "Sofia (+2:00)",
                          "Sofia"
                      ],
                      [
                          "Tallinn (+2:00)",
                          "Tallinn"
                      ],
                      [
                          "Vilnius (+2:00)",
                          "Vilnius"
                      ],
                      [
                          "Baghdad (+3:00)",
                          "Baghdad"
                      ],
                      [
                          "Istanbul (+3:00)",
                          "Istanbul"
                      ],
                      [
                          "Kuwait (+3:00)",
                          "Kuwait"
                      ],
                      [
                          "Minsk (+3:00)",
                          "Minsk"
                      ],
                      [
                          "Moscow (+3:00)",
                          "Moscow"
                      ],
                      [
                          "Nairobi (+3:00)",
                          "Nairobi"
                      ],
                      [
                          "Riyadh (+3:00)",
                          "Riyadh"
                      ],
                      [
                          "St. Petersburg (+3:00)",
                          "St. Petersburg"
                      ],
                      [
                          "Tehran (+3:30)",
                          "Tehran"
                      ],
                      [
                          "Abu Dhabi (+4:00)",
                          "Abu Dhabi"
                      ],
                      [
                          "Baku (+4:00)",
                          "Baku"
                      ],
                      [
                          "Muscat (+4:00)",
                          "Muscat"
                      ],
                      [
                          "Samara (+4:00)",
                          "Samara"
                      ],
                      [
                          "Tbilisi (+4:00)",
                          "Tbilisi"
                      ],
                      [
                          "Volgograd (+4:00)",
                          "Volgograd"
                      ],
                      [
                          "Yerevan (+4:00)",
                          "Yerevan"
                      ],
                      [
                          "Kabul (+4:30)",
                          "Kabul"
                      ],
                      [
                          "Ekaterinburg (+5:00)",
                          "Ekaterinburg"
                      ],
                      [
                          "Islamabad (+5:00)",
                          "Islamabad"
                      ],
                      [
                          "Karachi (+5:00)",
                          "Karachi"
                      ],
                      [
                          "Tashkent (+5:00)",
                          "Tashkent"
                      ],
                      [
                          "Chennai (+5:30)",
                          "Chennai"
                      ],
                      [
                          "Kolkata (+5:30)",
                          "Kolkata"
                      ],
                      [
                          "Mumbai (+5:30)",
                          "Mumbai"
                      ],
                      [
                          "New Delhi (+5:30)",
                          "New Delhi"
                      ],
                      [
                          "Sri Jayawardenepura (+5:30)",
                          "Sri Jayawardenepura"
                      ],
                      [
                          "Kathmandu (+5:45)",
                          "Kathmandu"
                      ],
                      [
                          "Almaty (+6:00)",
                          "Almaty"
                      ],
                      [
                          "Astana (+6:00)",
                          "Astana"
                      ],
                      [
                          "Dhaka (+6:00)",
                          "Dhaka"
                      ],
                      [
                          "Urumqi (+6:00)",
                          "Urumqi"
                      ],
                      [
                          "Rangoon (+6:30)",
                          "Rangoon"
                      ],
                      [
                          "Bangkok (+7:00)",
                          "Bangkok"
                      ],
                      [
                          "Hanoi (+7:00)",
                          "Hanoi"
                      ],
                      [
                          "Jakarta (+7:00)",
                          "Jakarta"
                      ],
                      [
                          "Krasnoyarsk (+7:00)",
                          "Krasnoyarsk"
                      ],
                      [
                          "Novosibirsk (+7:00)",
                          "Novosibirsk"
                      ],
                      [
                          "Beijing (+8:00)",
                          "Beijing"
                      ],
                      [
                          "Chongqing (+8:00)",
                          "Chongqing"
                      ],
                      [
                          "Hong Kong (+8:00)",
                          "Hong Kong"
                      ],
                      [
                          "Irkutsk (+8:00)",
                          "Irkutsk"
                      ],
                      [
                          "Kuala Lumpur (+8:00)",
                          "Kuala Lumpur"
                      ],
                      [
                          "Perth (+8:00)",
                          "Perth"
                      ],
                      [
                          "Singapore (+8:00)",
                          "Singapore"
                      ],
                      [
                          "Taipei (+8:00)",
                          "Taipei"
                      ],
                      [
                          "Ulaanbaatar (+8:00)",
                          "Ulaanbaatar"
                      ],
                      [
                          "Osaka (+9:00)",
                          "Osaka"
                      ],
                      [
                          "Sapporo (+9:00)",
                          "Sapporo"
                      ],
                      [
                          "Seoul (+9:00)",
                          "Seoul"
                      ],
                      [
                          "Tokyo (+9:00)",
                          "Tokyo"
                      ],
                      [
                          "Yakutsk (+9:00)",
                          "Yakutsk"
                      ],
                      [
                          "Adelaide (+9:30)",
                          "Adelaide"
                      ],
                      [
                          "Darwin (+9:30)",
                          "Darwin"
                      ],
                      [
                          "Brisbane (+10:00)",
                          "Brisbane"
                      ],
                      [
                          "Canberra (+10:00)",
                          "Canberra"
                      ],
                      [
                          "Guam (+10:00)",
                          "Guam"
                      ],
                      [
                          "Hobart (+10:00)",
                          "Hobart"
                      ],
                      [
                          "Melbourne (+10:00)",
                          "Melbourne"
                      ],
                      [
                          "Port Moresby (+10:00)",
                          "Port Moresby"
                      ],
                      [
                          "Sydney (+10:00)",
                          "Sydney"
                      ],
                      [
                          "Vladivostok (+10:00)",
                          "Vladivostok"
                      ],
                      [
                          "Magadan (+11:00)",
                          "Magadan"
                      ],
                      [
                          "New Caledonia (+11:00)",
                          "New Caledonia"
                      ],
                      [
                          "Solomon Is. (+11:00)",
                          "Solomon Is."
                      ],
                      [
                          "Srednekolymsk (+11:00)",
                          "Srednekolymsk"
                      ],
                      [
                          "Auckland (+12:00)",
                          "Auckland"
                      ],
                      [
                          "Fiji (+12:00)",
                          "Fiji"
                      ],
                      [
                          "Kamchatka (+12:00)",
                          "Kamchatka"
                      ],
                      [
                          "Marshall Is. (+12:00)",
                          "Marshall Is."
                      ],
                      [
                          "Wellington (+12:00)",
                          "Wellington"
                      ],
                      [
                          "Chatham Is. (+12:45)",
                          "Chatham Is."
                      ],
                      [
                          "Nuku'alofa (+13:00)",
                          "Nuku'alofa"
                      ],
                      [
                          "Samoa (+13:00)",
                          "Samoa"
                      ],
                      [
                          "Tokelau Is. (+13:00)",
                          "Tokelau Is."
                      ]
                  ]
              },
              {
                  "name": "ignoreReadOnlyFields",
                  "type": "boolean",
                  "optional": true,
                  "label": "Ignore read-only fields",
                  "hint": "Ignore read-only fields in add and update operation? If set to <b>No</b>, the action will throw error on trying to write to read-only fields.",
                  "default": "false"
              },
              {
                  "name": "advanced_settings",
                  "type": "object",
                  "properties": [
                    {
                        "name": "consumerKey",
                        "type": "string",
                        "label": "Consumer key"
                    },
                    {
                        "name": "consumerSecret",
                        "type": "string",
                        "label": "Consumer secret"
                    },
                  ]
              }
          ]
      }
```
:::

---
### NetSuite (Secondary)

**Provider values:**
```json
"provider": "netsuite_secondary"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "account",
                  "type": "string",
                  "label": "Account ID",
                  "hint": "Login as Administrator, then in <b>Setup Menu</b>, find in <b>Integration</b> > <b>Web Services Preferences</b>"
              },
              {
                  "name": "tokenId",
                  "type": "string",
                  "label": "Token ID"
              },
              {
                  "name": "tokenSecret",
                  "type": "string",
                  "label": "Token secret"
              },
              {
                  "name": "timezone",
                  "type": "string",
                  "optional": true,
                  "label": "Account timezone",
                  "hint": "Needed for consistency with NetSuite - pick same as your NetSuite profile",
                  "pick_list":
                  [
                      [
                          "American Samoa (-11:00)",
                          "American Samoa"
                      ],
                      [
                          "International Date Line West (-11:00)",
                          "International Date Line West"
                      ],
                      [
                          "Midway Island (-11:00)",
                          "Midway Island"
                      ],
                      [
                          "Hawaii (-10:00)",
                          "Hawaii"
                      ],
                      [
                          "Alaska (-9:00)",
                          "Alaska"
                      ],
                      [
                          "Pacific Time (US & Canada) (-8:00)",
                          "Pacific Time (US & Canada)"
                      ],
                      [
                          "Tijuana (-8:00)",
                          "Tijuana"
                      ],
                      [
                          "Arizona (-7:00)",
                          "Arizona"
                      ],
                      [
                          "Chihuahua (-7:00)",
                          "Chihuahua"
                      ],
                      [
                          "Mazatlan (-7:00)",
                          "Mazatlan"
                      ],
                      [
                          "Mountain Time (US & Canada) (-7:00)",
                          "Mountain Time (US & Canada)"
                      ],
                      [
                          "Central America (-6:00)",
                          "Central America"
                      ],
                      [
                          "Central Time (US & Canada) (-6:00)",
                          "Central Time (US & Canada)"
                      ],
                      [
                          "Guadalajara (-6:00)",
                          "Guadalajara"
                      ],
                      [
                          "Mexico City (-6:00)",
                          "Mexico City"
                      ],
                      [
                          "Monterrey (-6:00)",
                          "Monterrey"
                      ],
                      [
                          "Saskatchewan (-6:00)",
                          "Saskatchewan"
                      ],
                      [
                          "Bogota (-5:00)",
                          "Bogota"
                      ],
                      [
                          "Eastern Time (US & Canada) (-5:00)",
                          "Eastern Time (US & Canada)"
                      ],
                      [
                          "Indiana (East) (-5:00)",
                          "Indiana (East)"
                      ],
                      [
                          "Lima (-5:00)",
                          "Lima"
                      ],
                      [
                          "Quito (-5:00)",
                          "Quito"
                      ],
                      [
                          "Atlantic Time (Canada) (-4:00)",
                          "Atlantic Time (Canada)"
                      ],
                      [
                          "Caracas (-4:00)",
                          "Caracas"
                      ],
                      [
                          "Georgetown (-4:00)",
                          "Georgetown"
                      ],
                      [
                          "La Paz (-4:00)",
                          "La Paz"
                      ],
                      [
                          "Santiago (-4:00)",
                          "Santiago"
                      ],
                      [
                          "Newfoundland (-4:30)",
                          "Newfoundland"
                      ],
                      [
                          "Brasilia (-3:00)",
                          "Brasilia"
                      ],
                      [
                          "Buenos Aires (-3:00)",
                          "Buenos Aires"
                      ],
                      [
                          "Greenland (-3:00)",
                          "Greenland"
                      ],
                      [
                          "Montevideo (-3:00)",
                          "Montevideo"
                      ],
                      [
                          "Mid-Atlantic (-2:00)",
                          "Mid-Atlantic"
                      ],
                      [
                          "Azores (-1:00)",
                          "Azores"
                      ],
                      [
                          "Cape Verde Is. (-1:00)",
                          "Cape Verde Is."
                      ],
                      [
                          "Casablanca (+0:00)",
                          "Casablanca"
                      ],
                      [
                          "Dublin (+0:00)",
                          "Dublin"
                      ],
                      [
                          "Edinburgh (+0:00)",
                          "Edinburgh"
                      ],
                      [
                          "Lisbon (+0:00)",
                          "Lisbon"
                      ],
                      [
                          "London (+0:00)",
                          "London"
                      ],
                      [
                          "Monrovia (+0:00)",
                          "Monrovia"
                      ],
                      [
                          "UTC (+0:00)",
                          "UTC"
                      ],
                      [
                          "Amsterdam (+1:00)",
                          "Amsterdam"
                      ],
                      [
                          "Belgrade (+1:00)",
                          "Belgrade"
                      ],
                      [
                          "Berlin (+1:00)",
                          "Berlin"
                      ],
                      [
                          "Bern (+1:00)",
                          "Bern"
                      ],
                      [
                          "Bratislava (+1:00)",
                          "Bratislava"
                      ],
                      [
                          "Brussels (+1:00)",
                          "Brussels"
                      ],
                      [
                          "Budapest (+1:00)",
                          "Budapest"
                      ],
                      [
                          "Copenhagen (+1:00)",
                          "Copenhagen"
                      ],
                      [
                          "Ljubljana (+1:00)",
                          "Ljubljana"
                      ],
                      [
                          "Madrid (+1:00)",
                          "Madrid"
                      ],
                      [
                          "Paris (+1:00)",
                          "Paris"
                      ],
                      [
                          "Prague (+1:00)",
                          "Prague"
                      ],
                      [
                          "Rome (+1:00)",
                          "Rome"
                      ],
                      [
                          "Sarajevo (+1:00)",
                          "Sarajevo"
                      ],
                      [
                          "Skopje (+1:00)",
                          "Skopje"
                      ],
                      [
                          "Stockholm (+1:00)",
                          "Stockholm"
                      ],
                      [
                          "Vienna (+1:00)",
                          "Vienna"
                      ],
                      [
                          "Warsaw (+1:00)",
                          "Warsaw"
                      ],
                      [
                          "West Central Africa (+1:00)",
                          "West Central Africa"
                      ],
                      [
                          "Zagreb (+1:00)",
                          "Zagreb"
                      ],
                      [
                          "Athens (+2:00)",
                          "Athens"
                      ],
                      [
                          "Bucharest (+2:00)",
                          "Bucharest"
                      ],
                      [
                          "Cairo (+2:00)",
                          "Cairo"
                      ],
                      [
                          "Harare (+2:00)",
                          "Harare"
                      ],
                      [
                          "Helsinki (+2:00)",
                          "Helsinki"
                      ],
                      [
                          "Jerusalem (+2:00)",
                          "Jerusalem"
                      ],
                      [
                          "Kaliningrad (+2:00)",
                          "Kaliningrad"
                      ],
                      [
                          "Kyiv (+2:00)",
                          "Kyiv"
                      ],
                      [
                          "Pretoria (+2:00)",
                          "Pretoria"
                      ],
                      [
                          "Riga (+2:00)",
                          "Riga"
                      ],
                      [
                          "Sofia (+2:00)",
                          "Sofia"
                      ],
                      [
                          "Tallinn (+2:00)",
                          "Tallinn"
                      ],
                      [
                          "Vilnius (+2:00)",
                          "Vilnius"
                      ],
                      [
                          "Baghdad (+3:00)",
                          "Baghdad"
                      ],
                      [
                          "Istanbul (+3:00)",
                          "Istanbul"
                      ],
                      [
                          "Kuwait (+3:00)",
                          "Kuwait"
                      ],
                      [
                          "Minsk (+3:00)",
                          "Minsk"
                      ],
                      [
                          "Moscow (+3:00)",
                          "Moscow"
                      ],
                      [
                          "Nairobi (+3:00)",
                          "Nairobi"
                      ],
                      [
                          "Riyadh (+3:00)",
                          "Riyadh"
                      ],
                      [
                          "St. Petersburg (+3:00)",
                          "St. Petersburg"
                      ],
                      [
                          "Tehran (+3:30)",
                          "Tehran"
                      ],
                      [
                          "Abu Dhabi (+4:00)",
                          "Abu Dhabi"
                      ],
                      [
                          "Baku (+4:00)",
                          "Baku"
                      ],
                      [
                          "Muscat (+4:00)",
                          "Muscat"
                      ],
                      [
                          "Samara (+4:00)",
                          "Samara"
                      ],
                      [
                          "Tbilisi (+4:00)",
                          "Tbilisi"
                      ],
                      [
                          "Volgograd (+4:00)",
                          "Volgograd"
                      ],
                      [
                          "Yerevan (+4:00)",
                          "Yerevan"
                      ],
                      [
                          "Kabul (+4:30)",
                          "Kabul"
                      ],
                      [
                          "Ekaterinburg (+5:00)",
                          "Ekaterinburg"
                      ],
                      [
                          "Islamabad (+5:00)",
                          "Islamabad"
                      ],
                      [
                          "Karachi (+5:00)",
                          "Karachi"
                      ],
                      [
                          "Tashkent (+5:00)",
                          "Tashkent"
                      ],
                      [
                          "Chennai (+5:30)",
                          "Chennai"
                      ],
                      [
                          "Kolkata (+5:30)",
                          "Kolkata"
                      ],
                      [
                          "Mumbai (+5:30)",
                          "Mumbai"
                      ],
                      [
                          "New Delhi (+5:30)",
                          "New Delhi"
                      ],
                      [
                          "Sri Jayawardenepura (+5:30)",
                          "Sri Jayawardenepura"
                      ],
                      [
                          "Kathmandu (+5:45)",
                          "Kathmandu"
                      ],
                      [
                          "Almaty (+6:00)",
                          "Almaty"
                      ],
                      [
                          "Astana (+6:00)",
                          "Astana"
                      ],
                      [
                          "Dhaka (+6:00)",
                          "Dhaka"
                      ],
                      [
                          "Urumqi (+6:00)",
                          "Urumqi"
                      ],
                      [
                          "Rangoon (+6:30)",
                          "Rangoon"
                      ],
                      [
                          "Bangkok (+7:00)",
                          "Bangkok"
                      ],
                      [
                          "Hanoi (+7:00)",
                          "Hanoi"
                      ],
                      [
                          "Jakarta (+7:00)",
                          "Jakarta"
                      ],
                      [
                          "Krasnoyarsk (+7:00)",
                          "Krasnoyarsk"
                      ],
                      [
                          "Novosibirsk (+7:00)",
                          "Novosibirsk"
                      ],
                      [
                          "Beijing (+8:00)",
                          "Beijing"
                      ],
                      [
                          "Chongqing (+8:00)",
                          "Chongqing"
                      ],
                      [
                          "Hong Kong (+8:00)",
                          "Hong Kong"
                      ],
                      [
                          "Irkutsk (+8:00)",
                          "Irkutsk"
                      ],
                      [
                          "Kuala Lumpur (+8:00)",
                          "Kuala Lumpur"
                      ],
                      [
                          "Perth (+8:00)",
                          "Perth"
                      ],
                      [
                          "Singapore (+8:00)",
                          "Singapore"
                      ],
                      [
                          "Taipei (+8:00)",
                          "Taipei"
                      ],
                      [
                          "Ulaanbaatar (+8:00)",
                          "Ulaanbaatar"
                      ],
                      [
                          "Osaka (+9:00)",
                          "Osaka"
                      ],
                      [
                          "Sapporo (+9:00)",
                          "Sapporo"
                      ],
                      [
                          "Seoul (+9:00)",
                          "Seoul"
                      ],
                      [
                          "Tokyo (+9:00)",
                          "Tokyo"
                      ],
                      [
                          "Yakutsk (+9:00)",
                          "Yakutsk"
                      ],
                      [
                          "Adelaide (+9:30)",
                          "Adelaide"
                      ],
                      [
                          "Darwin (+9:30)",
                          "Darwin"
                      ],
                      [
                          "Brisbane (+10:00)",
                          "Brisbane"
                      ],
                      [
                          "Canberra (+10:00)",
                          "Canberra"
                      ],
                      [
                          "Guam (+10:00)",
                          "Guam"
                      ],
                      [
                          "Hobart (+10:00)",
                          "Hobart"
                      ],
                      [
                          "Melbourne (+10:00)",
                          "Melbourne"
                      ],
                      [
                          "Port Moresby (+10:00)",
                          "Port Moresby"
                      ],
                      [
                          "Sydney (+10:00)",
                          "Sydney"
                      ],
                      [
                          "Vladivostok (+10:00)",
                          "Vladivostok"
                      ],
                      [
                          "Magadan (+11:00)",
                          "Magadan"
                      ],
                      [
                          "New Caledonia (+11:00)",
                          "New Caledonia"
                      ],
                      [
                          "Solomon Is. (+11:00)",
                          "Solomon Is."
                      ],
                      [
                          "Srednekolymsk (+11:00)",
                          "Srednekolymsk"
                      ],
                      [
                          "Auckland (+12:00)",
                          "Auckland"
                      ],
                      [
                          "Fiji (+12:00)",
                          "Fiji"
                      ],
                      [
                          "Kamchatka (+12:00)",
                          "Kamchatka"
                      ],
                      [
                          "Marshall Is. (+12:00)",
                          "Marshall Is."
                      ],
                      [
                          "Wellington (+12:00)",
                          "Wellington"
                      ],
                      [
                          "Chatham Is. (+12:45)",
                          "Chatham Is."
                      ],
                      [
                          "Nuku'alofa (+13:00)",
                          "Nuku'alofa"
                      ],
                      [
                          "Samoa (+13:00)",
                          "Samoa"
                      ],
                      [
                          "Tokelau Is. (+13:00)",
                          "Tokelau Is."
                      ]
                  ]
              },
              {
                  "name": "ignoreReadOnlyFields",
                  "type": "boolean",
                  "optional": true,
                  "label": "Ignore read-only fields",
                  "hint": "Ignore read-only fields in add and update operation? If set to <b>No</b>, the action will throw error on trying to write to read-only fields.",
                  "default": "false"
              },
              {
                  "name": "advanced_settings",
                  "type": "object",
                  "properties": [
                    {
                        "name": "consumerKey",
                        "type": "string",
                        "label": "Consumer key"
                    },
                    {
                        "name": "consumerSecret",
                        "type": "string",
                        "label": "Consumer secret"
                    },
                  ]
              }
          ]
      }
```
:::

---
### New Relic

**Provider values:**
```json
"provider": "new_relic"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "api_key",
                  "type": "string",
                  "optional": false,
                  "label": "API Key",
                  "hint": "Go to Account settings->API Keys and get API key"
              }
          ]
      }
```
:::

---
### Nimble CRM

**Provider values:**
```json
"provider": "nimblecrm"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Okta

**Provider values:**
```json
"provider": "okta"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "subdomain",
                  "type": "string",
                  "optional": false,
                  "label": "Okta domain",
                  "hint": "Your Okta domain name as found in your Okta URL for example, mycompany.okta.com, mytest.oktapreview.com"
              },
              {
                  "name": "api_key",
                  "type": "string",
                  "optional": false,
                  "label": "API Key",
                  "hint": "Logon to the Okta admin console as an administrator and go to Security -> API -> Create Token"
              }
          ]
      }
```
:::

---
### Okta (Secondary)

**Provider values:**
```json
"provider": "okta_secondary"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "subdomain",
                  "type": "string",
                  "optional": false,
                  "label": "Okta domain",
                  "hint": "Your Okta domain name as found in your Okta URL for example, mycompany.okta.com, mytest.oktapreview.com"
              },
              {
                  "name": "api_key",
                  "type": "string",
                  "optional": false,
                  "label": "API Key",
                  "hint": "Logon to the Okta admin console as an administrator and go to Security -> API -> Create Token"
              }
          ]
      }
```
:::

---
### On-prem command-line scripts

**Provider values:**
```json
"provider": "onprem_command_line_scripts"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "profile",
                  "type": "string",
                  "label": "On-prem command-line scripts profile",
                  "hint": "Profile name given in the <b>config.yml</b> file"
              }
          ]
      }
```
:::

---
### On-prem files

**Provider values:**
```json
"provider": "onprem_files"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "profile",
                  "type": "string",
                  "label": "On-prem connection profile",
                  "hint": "Profile name given in the <b>config.yml</b> file"
              }
          ]
      }
```
:::

---
### On-prem files (Secondary)

**Provider values:**
```json
"provider": "onprem_files_secondary"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "profile",
                  "type": "string",
                  "label": "On-prem connection profile",
                  "hint": "Profile name given in the <b>config.yml</b> file"
              }
          ]
      }
```
:::

---
### OneDrive

**Provider values:**
```json
"provider": "onedrive"
```

::: details View connection parameters reference
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "account_type",
                  "type": "string",
                  "optional": false,
                  "label": "Account type",
                  "hint": "Select your Onedrive account type",
                  "pick_list":
                  [
                      [
                          "Personal",
                          "personal"
                      ],
                      [
                          "Business",
                          "business"
                      ]
                  ],
                  "default": "personal"
              }
          ]
      }
```
:::

---
### Oracle

**Provider values:**
```json
"provider": "oracle"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "profile",
                  "type": "string",
                  "label": "On-prem connection profile"
              },
              {
                  "name": "host",
                  "type": "string",
                  "label": "Database host"
              },
              {
                  "name": "port",
                  "type": "string",
                  "optional": true,
                  "label": "Database port",
                  "hint": "Port number, default is 1521",
                  "default": 1521
              },
              {
                  "name": "user",
                  "type": "string",
                  "label": "User name"
              },
              {
                  "name": "password",
                  "type": "string",
                  "optional": true,
                  "label": "Password"
              },
              {
                  "name": "dbname",
                  "type": "string",
                  "label": "Database name"
              }
          ]
      }
```
:::

---
### Oracle (Secondary)

**Provider values:**
```json
"provider": "oracle_secondary"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "profile",
                  "type": "string",
                  "label": "On-prem connection profile"
              },
              {
                  "name": "host",
                  "type": "string",
                  "label": "Database host"
              },
              {
                  "name": "port",
                  "type": "string",
                  "optional": true,
                  "label": "Database port",
                  "hint": "Port number, default is 1521",
                  "default": 1521
              },
              {
                  "name": "user",
                  "type": "string",
                  "label": "User name"
              },
              {
                  "name": "password",
                  "type": "string",
                  "optional": true,
                  "label": "Password"
              },
              {
                  "name": "dbname",
                  "type": "string",
                  "label": "Database name"
              }
          ]
      }
```
:::

---
### Oracle E-Business Suite

**Provider values:**
```json
"provider": "oracle_ebs"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "instance_url",
                  "type": "string",
                  "label": "Instance URL",
                  "hint": "URL of the instance. Eg: 'https://oracleebs.mycompany.com:8000/'. <br>\nDeploy User PL/SQL service (internal name: FND_USER_PKG) with service name as 'user'\n"
              },
              {
                  "name": "username",
                  "type": "string",
                  "label": "Username"
              },
              {
                  "name": "password",
                  "type": "string",
                  "label": "Password"
              },
              {
                  "name": "user_service_name",
                  "type": "string",
                  "label": "User service name",
                  "hint": "Name of the PL/SQL REST service name used while deployment"
              }
          ]
      }
```
:::

---
### Oracle Fusion

**Provider values:**
```json
"provider": "oracle_fusion"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "user",
                  "type": "string",
                  "label": "User"
              },
              {
                  "name": "password",
                  "type": "string",
                  "label": "Password"
              }
          ]
      }
```
:::

---
### Outlook

**Provider values:**
```json
"provider": "outlook"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "advanced_settings",
                  "type": "object",
                  "optional": true,
                  "label": "Advanced settings",
                  "properties":
                  [
                      {
                          "name": "api_scope",
                          "type": "string",
                          "optional": true,
                          "label": "Requested permissions (Oauth scopes)",
                          "hint": "                     Select <a href=\"https://docs.microsoft.com/en-us/graph/permissions-reference#mail-permissions\" target=\"_blank\">permissions</a>\n                     to request for this connection. Defaults to minimum permissions if left blank.\n                     Minimum permissions required are <b>mail.read</b>, <b>mail.send</b>, <b>calendars.readwrite</b>, <b>offline_access</b>, <b>mail.Read.Shared</b>;\n                     these are always requested in addition to selected permissions.\n"
                      }
                  ]
              }
          ]
      }
```
:::

---
### Outreach

**Provider values:**
```json
"provider": "outreach"
```

---
### OutSystems

**Provider values:**
```json
"provider": "out_systems"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "API_key",
                  "type": "string",
                  "optional": false,
                  "label": "API key",
                  "hint": "Type in an API key generated using the security configuration page, on the <b>OutSystems Workato Connector</b>. If you don't have the <b>OutSystems Workato Connector</b> installed on your server, please get it from the <a href='https://www.outsystems.com/forge/' target='_blank'>OutSystems Forge</a>."
              },
              {
                  "name": "EnvironmentURL",
                  "type": "string",
                  "optional": false,
                  "label": "Environment URL",
                  "hint": "Your OutSystems environment URL (eg: YOUR_PERSONAL.outsystemscloud.com)."
              }
          ]
      }
```
:::

---
### Pagerduty

**Provider values:**
```json
"provider": "pagerduty"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "api_key",
                  "type": "string",
                  "optional": false,
                  "label": "API key",
                  "hint": "Go to Configuration -> API Access and get API Key"
              }
          ]
      }
```
:::

---
### ParseHub

**Provider values:**
```json
"provider": "parsehub"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "api_key",
                  "type": "string",
                  "optional": false,
                  "label": "Api key",
                  "hint": "Select your ParseHub account name-> Select Account-> Get your api key"
              }
          ]
      }
```
:::

---
### People Task by Workato

**Provider values:**
```json
"provider": "workflow"
```

---
### Percolate

**Provider values:**
```json
"provider": "percolate"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "client_id",
                  "type": "string",
                  "optional": false,
                  "label": "Client ID",
                  "hint": "To create client ID, the system admin or manager can click <a href='https://percolate.com/app/settings/developer/apps/new' target='_blank'>here</a> to register a new client application."
              },
              {
                  "name": "client_secret",
                  "type": "string",
                  "optional": false,
                  "label": "Client secret",
                  "hint": "To create client secret, the system admin or manager can click <a href='https://percolate.com/app/settings/developer/apps/new' target='_blank'>here</a> to register a new client application."
              },
              {
                  "name": "environment",
                  "type": "string",
                  "optional": false,
                  "label": "Environment",
                  "pick_list":
                  [
                      [
                          "Production",
                          "production"
                      ],
                      [
                          "Sandbox",
                          "sandbox"
                      ],
                      [
                          "Internal",
                          "internal"
                      ]
                  ]
              }
          ]
      }
```
:::

---
### PGP

**Provider values:**
```json
"provider": "pgp"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "public_key",
                  "type": "string",
                  "optional": true,
                  "label": "Public key (deprecated)",
                  "hint": "Provide the public key in Encrypt and Verify action input."
              },
              {
                  "name": "private_key",
                  "type": "string",
                  "optional": true,
                  "label": "Private key",
                  "hint": "Private is required for decrypt and sign actions. Learn how to generate a pair of Public key and Private key\n<a href=\"https://docs.workato.com/features/pgp-encryption.html\" target=\"_blank\">here</a>.\n"
              },
              {
                  "name": "passphrase",
                  "type": "string",
                  "optional": true,
                  "label": "Passphrase",
                  "hint": "Passphrase of the keys you have generated."
              }
          ]
      }
```
:::

---
### Pingdom

**Provider value:**
```json
"provider": "pingdom"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "app_key",
                  "type": "string",
                  "optional": false,
                  "label": "Application key"
              },
              {
                  "name": "username",
                  "type": "string",
                  "optional": false,
                  "label": "Username",
                  "hint": "Your username"
              },
              {
                  "name": "password",
                  "type": "string",
                  "optional": false,
                  "label": "Password"
              }
          ]
      }
```
:::

---
### Pipedrive

**Provider value:**
```json
"provider": "pipedrive"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "api_token",
                  "type": "string",
                  "label": "Api token",
                  "hint": "API token is found in the API tab under Personal settings (Settings > Personal > API)"
              }
          ]
      }
```
:::

---
### Pivotal Tracker

**Provider value:**
```json
"provider": "pivotal_tracker"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "api_key",
                  "type": "string",
                  "optional": true,
                  "label": "API key",
                  "hint": "Select your account name -> Profile. Scroll down to end of the page to get API token"
              }
          ]
      }
```
:::

---
### PlanGrid

**Provider value:**
```json
"provider": "plan_grid"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Podio

**Provider value:**
```json
"provider": "podio"
```

Connection parameter configuration **_is not required_** for this connector.

---
### PostgreSQL

**Provider value:**
```json
"provider": "postgresql"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "profile",
                  "type": "string",
                  "label": "On-prem connection profile"
              },
              {
                  "name": "host",
                  "type": "string",
                  "label": "Database host"
              },
              {
                  "name": "port",
                  "type": "string",
                  "label": "Database port"
              },
              {
                  "name": "user",
                  "type": "string",
                  "label": "User name"
              },
              {
                  "name": "password",
                  "type": "string",
                  "optional": true,
                  "label": "Password"
              },
              {
                  "name": "dbname",
                  "type": "string",
                  "label": "Database name"
              },
              {
                  "name": "schema_name",
                  "type": "string",
                  "optional": true,
                  "label": "Schema",
                  "hint": "\"public\" schema by default"
              }
          ]
      }
```
:::

### PostgreSQL (Secondary)

**Provider value:**
```json
"provider": "postgresql_secondary"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "profile",
                  "type": "string",
                  "label": "On-prem connection profile"
              },
              {
                  "name": "host",
                  "type": "string",
                  "label": "Database host"
              },
              {
                  "name": "port",
                  "type": "string",
                  "label": "Database port"
              },
              {
                  "name": "user",
                  "type": "string",
                  "label": "User name"
              },
              {
                  "name": "password",
                  "type": "string",
                  "optional": true,
                  "label": "Password"
              },
              {
                  "name": "dbname",
                  "type": "string",
                  "label": "Database name"
              },
              {
                  "name": "schema_name",
                  "type": "string",
                  "optional": true,
                  "label": "Schema",
                  "hint": "\"public\" schema by default"
              }
          ]
      }
```
:::

---
### Product Hunt

**Provider value:**
```json
"provider": "product_hunt"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "username",
                  "type": "string",
                  "optional": false,
                  "label": "Username",
                  "hint": "Your Product Hunt Username. Remove \"@\" prefix."
              }
          ]
      }
```
:::

---
### Prontoforms

**Provider value:**
```json
"provider": "prontoforms"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "api_key",
                  "type": "string",
                  "label": "Api key"
              },
              {
                  "name": "api_secret",
                  "type": "string",
                  "label": "Api secret"
              }
          ]
      }
```
:::

---
### Propel

**Provider value:**
```json
"provider": "propel"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "sandbox",
                  "type": "boolean",
                  "optional": true,
                  "label": "Sandbox",
                  "hint": "Is this connecting to a sandbox account?",
                  "default": "false"
              }
          ]
      }
```
:::

---
### PubSub by Workato

**Provider value:**
```json
"provider": "workato_pub_sub"
```

---
### Quick Base

**Provider value:**
```json
"provider": "quickbase"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "subdomain",
                  "type": "string",
                  "label": "Sub-domain",
                  "hint": "Your Quick Base subdomain is most often your company name"
              },
              {
                  "name": "user_token_auth",
                  "type": "boolean",
                  "label": "User-token authentication?",
                  "hint": "Is authentication based on user tokens? If yes, provide <b>User token</b>. If no, provide <b>Username</b> & <b>Password</b>.",
                  "default": "false"
              },
              {
                  "name": "usertoken",
                  "type": "string",
                  "optional": true,
                  "label": "User token",
                  "hint": "Get/create user token by clicking on <b>Your profile > My preferences > Manage User Tokens</b>. <a href='https://help.quickbase.com/api-guide/manage_user_tokens.html' target='_blank' >Learn more</a>"
              },
              {
                  "name": "username",
                  "type": "string",
                  "optional": true,
                  "label": "Username"
              },
              {
                  "name": "password",
                  "type": "string",
                  "optional": true,
                  "label": "Password"
              }
          ]
      }
```
:::

---
### Quick Base (Secondary)

**Provider value:**
```json
"provider": "quickbase_secondary"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "subdomain",
                  "type": "string",
                  "label": "Sub-domain",
                  "hint": "Your Quick Base subdomain is most often your company name"
              },
              {
                  "name": "user_token_auth",
                  "type": "boolean",
                  "label": "User-token authentication?",
                  "hint": "Is authentication based on user tokens? If yes, provide <b>User token</b>. If no, provide <b>Username</b> & <b>Password</b>.",
                  "default": "false"
              },
              {
                  "name": "usertoken",
                  "type": "string",
                  "optional": true,
                  "label": "User token",
                  "hint": "Get/create user token by clicking on <b>Your profile > My preferences > Manage User Tokens</b>. <a href='https://help.quickbase.com/api-guide/manage_user_tokens.html' target='_blank' >Learn more</a>"
              },
              {
                  "name": "username",
                  "type": "string",
                  "optional": true,
                  "label": "Username"
              },
              {
                  "name": "password",
                  "type": "string",
                  "optional": true,
                  "label": "Password"
              }
          ]
      }
```
:::

---
### QuickBooks Online

**Provider value:**
```json
"provider": "quickbooks"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Quip

**Provider value:**
```json
"provider": "quip"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "api_key",
                  "type": "string",
                  "label": "Personal API token",
                  "hint": "Personal API token. Click <a href=\"https://quip.com/api/personal-token\">here</a> to generate API token"
              }
          ]
      }
```
:::

---
### Raiser's Edge NXT

**Provider value:**
```json
"provider": "raisers_edge"
```

Connection parameter configuration **_is not required_** for this connector.

---
### RecipeOps by Workato

**Provider value:**
```json
"provider": "workato_app"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "connecting_to_account",
                  "type": "boolean",
                  "label": "Whose account are you managing?",
                  "pick_list":
                  [
                      [
                          "My account",
                          "current"
                      ],
                      [
                          "Someone else's account",
                          "other"
                      ]
                  ],
                  "default": "nil"
              },
              {
                  "name": "email",
                  "type": "string",
                  "label": "Email",
                  "hint": "Managed account’s email"
              },
              {
                  "name": "api_key",
                  "type": "string",
                  "label": "API key",
                  "hint": "Ask the account holder to provide the API key found here: <a href=\"http://localhost:3000/users/current/edit#api_key\" target=\"_blank\">http://localhost:3000/users/current/edit#api_key</a>"
              }
          ]
      }
```
:::

---
### Redshift

**Provider value:**
```json
"provider": "redshift"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "url",
                  "type": "string",
                  "label": "URL",
                  "hint": "Redshift JDBC URL."
              },
              {
                  "name": "username",
                  "type": "string",
                  "label": "Username"
              },
              {
                  "name": "password",
                  "type": "string",
                  "label": "Password"
              },
              {
                  "name": "schema_name",
                  "type": "string",
                  "optional": true,
                  "label": "Schema",
                  "hint": "\"public\" schema by default"
              }
          ]
      }
```
:::

---
### Redshift (Secondary)

**Provider value:**
```json
"provider": "redshift_secondary"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "url",
                  "type": "string",
                  "label": "URL",
                  "hint": "Redshift JDBC URL."
              },
              {
                  "name": "username",
                  "type": "string",
                  "label": "Username"
              },
              {
                  "name": "password",
                  "type": "string",
                  "label": "Password"
              },
              {
                  "name": "schema_name",
                  "type": "string",
                  "optional": true,
                  "label": "Schema",
                  "hint": "\"public\" schema by default"
              }
          ]
      }
```
:::

---
### RegOnline® by Lanyon

**Provider value:**
```json
"provider": "active_reg_online"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "api_token",
                  "type": "string",
                  "label": "API Token",
                  "hint": "API token is found at the bottom of the RegOnline 'Edit User' screen."
              }
          ]
      }
```
:::

---
### Replicon

**Provider value:**
```json
"provider": "replicon"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "company",
                  "type": "string",
                  "label": "Company",
                  "hint": "The company name associated with your login"
              },
              {
                  "name": "user_token_auth",
                  "type": "boolean",
                  "label": "User-token authentication?",
                  "hint": "Is authentication based on user tokens? If <b>Yes</b>, provide <b>User token</b>. Is <b>No</b>, provide <b>Username</b> & <b>Password</b>.",
                  "default": "false"
              },
              {
                  "name": "usertoken",
                  "type": "string",
                  "optional": true,
                  "label": "User token",
                  "hint": "Use this API https://<b>region</b>.replicon.com/<b>Company name</b>/services/AuthenticationService1.svc/help/test/CreateAccessToken to get user token"
              },
              {
                  "name": "username",
                  "type": "string",
                  "label": "Login name"
              },
              {
                  "name": "password",
                  "type": "string",
                  "optional": true,
                  "label": "Password"
              },
              {
                  "name": "subdomain",
                  "type": "string",
                  "optional": true,
                  "label": "Subdomain",
                  "hint": "Leave to default (global) for production instances",
                  "default": "global"
              }
          ]
      }
```
:::

---
### Revel Systems

**Provider value:**
```json
"provider": "revel_systems"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "subdomain",
                  "type": "string",
                  "label": "Subdomain",
                  "hint": "Your revel systems subdomain, usually a company name; for example, the <b>api-playground</b> part in https://api-playground.revelup.com"
              },
              {
                  "name": "api_key",
                  "type": "string",
                  "label": "Api key"
              },
              {
                  "name": "api_secret",
                  "type": "string",
                  "label": "Api secret"
              }
          ]
      }
```
:::

---
### RingCentral

**Provider value:**
```json
"provider": "ringcentral"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "development",
                  "type": "number",
                  "optional": true,
                  "label": "Development",
                  "hint": "Leave empty to connect production account. Provide <b>true</b> for development account <b>false</b> for production account."
              }
          ]
      }
```
:::

---
### Rollbar

**Provider value:**
```json
"provider": "rollbar"
```

---
### Ruby

**Provider value:**
```json
"provider": "workato_custom_code"
```

---
### Sage Intacct

**Provider value:**
```json
"provider": "intacct"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "login_username",
                  "type": "string",
                  "label": "Login username"
              },
              {
                  "name": "login_password",
                  "type": "string",
                  "label": "Login password"
              },
              {
                  "name": "company_id",
                  "type": "string",
                  "label": "Company ID"
              },
              {
                  "name": "location_id",
                  "type": "string",
                  "optional": true,
                  "label": "Location ID",
                  "hint": "If not specified, it takes the top level(all entities)"
              }
          ]
      }
```
:::

---
### Sage Live

**Provider value:**
```json
"provider": "sagelive"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "sandbox",
                  "type": "boolean",
                  "optional": true,
                  "label": "Sandbox",
                  "hint": "Is this connecting to a sandbox account?",
                  "default": "false"
              }
          ]
      }
```
:::

---
### Salesforce

**Provider value:**
```json
"provider": "salesforce"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "sandbox",
                  "type": "boolean",
                  "optional": true,
                  "label": "Sandbox",
                  "hint": "Is this connecting to a sandbox account?",
                  "default": "false"
              },
              {
                  "name": "advanced_settings",
                  "type": "object",
                  "optional": true,
                  "label": "Advanced settings",
                  "properties":
                  [
                      {
                          "name": "custom_login_url",
                          "type": "string",
                          "optional": true,
                          "label": "Salesforce community custom domain URL",
                          "hint": "                   Enter your Salesforce community's custom domain URL, eg. <b>acme-domain.force.com</b>.\n                   <a target='_blank' href='https://docs.workato.com/connectors/salesforce.html#connecting-to-custom-domains'>Learn more</a>\n"
                      },
                      {
                          "name": "api_scope",
                          "type": "string",
                          "optional": true,
                          "label": "Requested permissions (Oauth scopes)",
                          "hint": "                     Select <a href=\"https://help.salesforce.com/articleView?id=remoteaccess_oauth_scopes.htm&type=5\" target=\"_blank\">permissions</a>\n                      to request for this connection. Defaults to <b>full</b> (all permissions) if left blank.\n                     <br/>Minimum permissions required are <b>basic info</b>, <b>manage data</b> and <b>make\n                      requests at any time</b>;\n                     those are always requested in addition to selected permissions.\n"
                      }
                  ]
              }
          ]
      }
```
:::

---
### Salesforce (Secondary)

**Provider value:**
```json
"provider": "salesforce_secondary"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "sandbox",
                  "type": "boolean",
                  "optional": true,
                  "label": "Sandbox",
                  "hint": "Is this connecting to a sandbox account?",
                  "default": "false"
              },
              {
                  "name": "advanced_settings",
                  "type": "object",
                  "optional": true,
                  "label": "Advanced settings",
                  "properties":
                  [
                      {
                          "name": "custom_login_url",
                          "type": "string",
                          "optional": true,
                          "label": "Salesforce community custom domain URL",
                          "hint": "                   Enter your Salesforce community's custom domain URL, eg. <b>acme-domain.force.com</b>.\n                   <a target='_blank' href='https://docs.workato.com/connectors/salesforce.html#connecting-to-custom-domains'>Learn more</a>\n"
                      },
                      {
                          "name": "api_scope",
                          "type": "string",
                          "optional": true,
                          "label": "Requested permissions (Oauth scopes)",
                          "hint": "                     Select <a href=\"https://help.salesforce.com/articleView?id=remoteaccess_oauth_scopes.htm&type=5\" target=\"_blank\">permissions</a>\n                      to request for this connection. Defaults to <b>full</b> (all permissions) if left blank.\n                     <br/>Minimum permissions required are <b>basic info</b>, <b>manage data</b> and <b>make\n                      requests at any time</b>;\n                     those are always requested in addition to selected permissions.\n"
                      }
                  ]
              }
          ]
      }
```
:::

---
### Salesforce CPQ

**Provider value:**
```json
"provider": "steelbrick"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "sandbox",
                  "type": "boolean",
                  "optional": true,
                  "label": "Sandbox",
                  "hint": "Is this connecting to a sandbox account?",
                  "default": "false"
              }
          ]
      }
```
:::

---
### SalesforceIQ

**Provider value:**
```json
"provider": "relateiq"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "api_key",
                  "type": "string",
                  "label": "API Key",
                  "hint": "Create in your SalesforceIQ account: Organization > settings > integrations"
              },
              {
                  "name": "api_secret",
                  "type": "string",
                  "label": "API Secret"
              }
          ]
      }
```
:::

---
### Salesforce Marketing Cloud

**Provider value:**
```json
"provider": "salesforce_marketing_cloud"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "flag",
                  "type": "boolean",
                  "label": "Are you using a new installed package?",
                  "hint": "Legacy packages (created before 1st August 2019) uses a different set of fields to connect.",
                  "default": "false"
              },
              {
                  "name": "instance",
                  "type": "string",
                  "label": "Instance",
                  "hint": "Select the instance of your account. Eg: Select <b>s7</b>, if the instance URL is <b>https://mc.s7.exacttarget.com</b>.",
                  "pick_list":
                  [
                      [
                          "s1",
                          "s1"
                      ],
                      [
                          "s4",
                          "s4"
                      ],
                      [
                          "s6",
                          "s6"
                      ],
                      [
                          "s7",
                          "s7"
                      ],
                      [
                          "s10",
                          "s10"
                      ],
                      [
                          "test",
                          "test"
                      ]
                  ]
              },
              {
                  "name": "instance_name",
                  "type": "string",
                  "label": "Instance name",
                  "hint": "Enter the instance of your account. Eg: Enter <b>s7</b>, if the instance URL is <b>https://mc.s7.exacttarget.com</b>."
              },
              {
                  "name": "subdomain",
                  "type": "string",
                  "label": "Subdomain",
                  "hint": "Enter the sub-domain of your account."
              },
              {
                  "name": "client_id",
                  "type": "string",
                  "label": "Client ID",
                  "hint": "                   Create client credentials with read and write access for <b>channels</b>, <b>assets</b>, <b>contacts</b>, <b>data</b>. To access shared content, use\n                   credentials of business unit where content belongs.\n                   To create client credentials refer\n                   <a href=\"https://developer.salesforce.com/docs/atlas.en-us.mc-getting-started.meta/mc-getting-started/app-center-types.htm\" target=\"_blank\">here</a>.\n"
              },
              {
                  "name": "client_secret",
                  "type": "string",
                  "label": "Client secret"
              }
          ]
      }
```
:::

---
### SAP D4C

**Provider value:**
```json
"provider": "sap_d4c"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "username",
                  "type": "string",
                  "label": "Username"
              },
              {
                  "name": "password",
                  "type": "string",
                  "label": "Password"
              },
              {
                  "name": "endpoint",
                  "type": "string",
                  "label": "Endpoint",
                  "hint": "Eg. 'my123456.vlab.sapbydesign.com'"
              }
          ]
      }
```
:::

---
### SAP OData

**Provider value:**
```json
"provider": "sap_s4_hana_cloud"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "domain",
                  "type": "string",
                  "label": "Service URL",
                  "hint": "Your SAP Service URL to validate authentication. For example, <b>http://sap.intranet.acme.com:7654/sap/opu/odata/sap/ZEMPLOYEE_SRV</b>."
              },
              {
                  "name": "username",
                  "type": "string",
                  "label": "Username"
              },
              {
                  "name": "password",
                  "type": "string",
                  "label": "Password"
              },
              {
                  "name": "client",
                  "type": "string",
                  "optional": true,
                  "label": "Client",
                  "hint": "SAP client ID. Leave blank to use the default logon client."
              }
          ]
      }
```
:::

---
### SAP RFC

**Provider value:**
```json
"provider": "sap"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "profile",
                  "type": "string",
                  "label": "On-prem agent connection profile",
                  "hint": "<a href='https://docs.workato.com/connectors/sap.html' target='_blank'>Click here</a> to learn how to configure SAP connection."
              }
          ]
      }
```
:::

---
### Scheduler by Workato

**Provider value:**
```json
"provider": "clock"
```

---
### SendGrid

**Provider value:**
```json
"provider": "sendgrid"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "api_key",
                  "type": "string",
                  "optional": false,
                  "label": "API key",
                  "hint": "Go to settings -> API keys -> create API key"
              }
          ]
      }
```
:::

---
### ServiceM8

**Provider value:**
```json
"provider": "servicem8"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "user",
                  "type": "string",
                  "label": "User"
              },
              {
                  "name": "password",
                  "type": "string",
                  "label": "Password"
              }
          ]
      }
```
:::

---
### ServiceMax

**Provider value:**
```json
"provider": "service_max"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "sandbox",
                  "type": "boolean",
                  "optional": true,
                  "label": "Sandbox",
                  "hint": "Is this connecting to a sandbox account?",
                  "default": "false"
              }
          ]
      }
```
:::

---
### ServiceNow

**Provider value:**
```json
"provider": "service_now"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "authentication_type",
                  "type": "string",
                  "label": "Authentication type",
                  "hint": "Only Istanbul version or later supports OAuth 2.0. <a href=\"http://docs.workato.com/connectors/servicenow.html\" target=\"_blank\">Learn more</a> about the authentication types.",
                  "pick_list":
                  [
                      [
                          "Username/Password",
                          "basic"
                      ],
                      [
                          "OAuth 2.0",
                          "oauth"
                      ]
                  ],
                  "default": "basic"
              },
              {
                  "name": "subdomain",
                  "type": "string",
                  "label": "Instance name",
                  "hint": "If your ServiceNow url is <b>https://acme.service-now.com</b>, then instance name is <b>'acme'</b>."
              },
              {
                  "name": "username",
                  "type": "string",
                  "label": "Username",
                  "hint": "Make sure that you have sufficient access control to all the tables you wish to work with. <a href=\"http://docs.workato.com/connectors/servicenow.html#roles-and-permissions-required-to-connect\" target=\"_blank\">Learn more</a>."
              },
              {
                  "name": "password",
                  "type": "string",
                  "label": "Password"
              },
              {
                  "name": "client_id",
                  "type": "string",
                  "label": "Client ID",
                  "hint": "<a href=\"http://docs.workato.com/connectors/servicenow.html#oauth-20\" target=\"_blank\">Learn more</a> about setting up OAuth in your ServiceNow instance."
              },
              {
                  "name": "client_secret",
                  "type": "string",
                  "label": "Client secret"
              }
          ]
      }
```
:::

---
### ServiceNow (Secondary)

**Provider value:**
```json
"provider": "service_now_secondary"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "authentication_type",
                  "type": "string",
                  "label": "Authentication type",
                  "hint": "Only Istanbul version or later supports OAuth 2.0. <a href=\"http://docs.workato.com/connectors/servicenow.html\" target=\"_blank\">Learn more</a> about the authentication types.",
                  "pick_list":
                  [
                      [
                          "Username/Password",
                          "basic"
                      ],
                      [
                          "OAuth 2.0",
                          "oauth"
                      ]
                  ],
                  "default": "basic"
              },
              {
                  "name": "subdomain",
                  "type": "string",
                  "label": "Instance name",
                  "hint": "If your ServiceNow url is <b>https://acme.service-now.com</b>, then instance name is <b>'acme'</b>."
              },
              {
                  "name": "username",
                  "type": "string",
                  "label": "Username",
                  "hint": "Make sure that you have sufficient access control to all the tables you wish to work with. <a href=\"http://docs.workato.com/connectors/servicenow.html#roles-and-permissions-required-to-connect\" target=\"_blank\">Learn more</a>."
              },
              {
                  "name": "password",
                  "type": "string",
                  "label": "Password"
              },
              {
                  "name": "client_id",
                  "type": "string",
                  "label": "Client ID",
                  "hint": "<a href=\"http://docs.workato.com/connectors/servicenow.html#oauth-20\" target=\"_blank\">Learn more</a> about setting up OAuth in your ServiceNow instance."
              },
              {
                  "name": "client_secret",
                  "type": "string",
                  "label": "Client secret"
              }
          ]
      }
```
:::

---
### SFTP

**Provider value:**
```json
"provider": "sftp"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "auth_type",
                  "type": "string",
                  "label": "Auth type",
                  "pick_list":
                  [
                      [
                          "Username/password",
                          "username_password"
                      ],
                      [
                          "Public/private key pair",
                          "pubkey"
                      ]
                  ],
                  "default": "username_password"
              },
              {
                  "name": "username",
                  "type": "string",
                  "label": "Username"
              },
              {
                  "name": "password",
                  "type": "string",
                  "label": "Password"
              },
              {
                  "name": "private_key",
                  "type": "string",
                  "label": "Private key",
                  "hint": "Please use an OpenSSH private key, without password protection. <a href=\"https://www.ssh.com/ssh/keygen/\" target=\"_blank\">Learn more</a>"
              },
              {
                  "name": "hostname",
                  "type": "string",
                  "label": "Hostname",
                  "hint": "Contact your SFTP server administrator to whitelist Workato IP addresses. <a href=\"http://docs.workato.com/security.html\" target=\"_blank\">Learn more</a>"
              },
              {
                  "name": "port",
                  "type": "integer",
                  "label": "Port",
                  "hint": "The standard port is 22, contact your SFTP server administrator for the correct port.",
              },
              {
                  "name": "host_key_fingerprint",
                  "type": "string",
                  "optional": true,
                  "label": "Host key fingerprint",
                  "hint": "The connection will still be encrypted without this, but without protection against <a href=\"https://en.wikipedia.org/wiki/Man-in-the-middle_attack\">MITM</a><br/>Contact SFTP server administrator for the key fingerprint."
              },
              {
                  "name": "transfer_buffer_size",
                  "type": "integer",
                  "label": "Transfer buffer size",
                  "hint": "Size of the buffer used to transfer files. Minimum is 32768.\nLarger sizes, if supported by the SFTP server, generally speed up transfers.\nMaximum is 327680.\n",
              },
              {
                  "name": "force_close",
                  "type": "boolean",
                  "optional": true,
                  "label": "Force close",
                  "hint": "Shuts down the underlying SSH connection at the end of the transaction.\nOnly needed for servers where the connection attempt seems to hang, should\nbe left unset otherwise to allow a clean connection close.\n"
              }
          ]
      }
```
:::

---
### SFTP (Secondary)

**Provider value:**
```json
"provider": "sftp_secondary
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "auth_type",
                  "type": "string",
                  "label": "Auth type",
                  "pick_list":
                  [
                      [
                          "Username/password",
                          "username_password"
                      ],
                      [
                          "Public/private key pair",
                          "pubkey"
                      ]
                  ],
                  "default": "username_password"
              },
              {
                  "name": "username",
                  "type": "string",
                  "label": "Username"
              },
              {
                  "name": "password",
                  "type": "string",
                  "label": "Password"
              },
              {
                  "name": "private_key",
                  "type": "string",
                  "label": "Private key",
                  "hint": "Please use an OpenSSH private key, without password protection. <a href=\"https://www.ssh.com/ssh/keygen/\" target=\"_blank\">Learn more</a>"
              },
              {
                  "name": "hostname",
                  "type": "string",
                  "label": "Hostname",
                  "hint": "Contact your SFTP server administrator to whitelist Workato IP addresses. <a href=\"http://docs.workato.com/security.html\" target=\"_blank\">Learn more</a>"
              },
              {
                  "name": "port",
                  "type": "integer",
                  "label": "Port",
                  "hint": "The standard port is 22, contact your SFTP server administrator for the correct port.",
              },
              {
                  "name": "host_key_fingerprint",
                  "type": "string",
                  "optional": true,
                  "label": "Host key fingerprint",
                  "hint": "The connection will still be encrypted without this, but without protection against <a href=\"https://en.wikipedia.org/wiki/Man-in-the-middle_attack\">MITM</a><br/>Contact SFTP server administrator for the key fingerprint."
              },
              {
                  "name": "transfer_buffer_size",
                  "type": "integer",
                  "label": "Transfer buffer size",
                  "hint": "Size of the buffer used to transfer files. Minimum is 32768.\nLarger sizes, if supported by the SFTP server, generally speed up transfers.\nMaximum is 327680.\n",
              },
              {
                  "name": "force_close",
                  "type": "boolean",
                  "optional": true,
                  "label": "Force close",
                  "hint": "Shuts down the underlying SSH connection at the end of the transaction.\nOnly needed for servers where the connection attempt seems to hang, should\nbe left unset otherwise to allow a clean connection close.\n"
              }
          ]
      }
```
:::

---
### Shopify

**Provider value:**
```json
"provider": "shopify"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "shop_name",
                  "type": "string",
                  "label": "Shop Name",
                  "hint": "Your shop name Eg. <b>shopname</b>.myshopify.com/admin"
              }
          ]
      }
```
:::

---
### Showpad

**Provider value:**
```json
"provider": "showpad"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "subdomain",
                  "type": "string",
                  "label": "Subdomain",
                  "hint": "Your Showpad subdomain, usually a company name; for example, the <b>acme</b> part in https://acme.showpad.biz"
              }
          ]
      }
```
:::

---
### Slack

**Provider value:**
```json
"provider": "slack"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Slack (Secondary)

**Provider value:**
```json
"provider": "slack_secondary"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Smartsheet

**Provider value:**
```json
"provider": "smartsheet"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "advanced_settings",
                  "type": "object",
                  "optional": true,
                  "label": "Advanced settings",
                  "properties":
                  [
                      {
                          "name": "api_scope",
                          "type": "string",
                          "optional": true,
                          "label": "Requested permissions (Oauth scopes)",
                          "hint": "                      Select <a href=\"https://smartsheet-platform.github.io/api-docs/#access-scopes\" target=\"_blank\">permissions</a>\n                      to request for this connection. Defaults to minimum permissions, if left blank.\n                      <br/>Minimum permissions required are <b>READ_SHEETS</b>, <b>WRITE_SHEETS</b>, <b>ADMIN_WEBHOOKS</b> and <b>CREATE_SHEETS</b>;\n                      those are always requested in addition to selected permissions.\n"
                      }
                  ]
              }
          ]
      }
```
:::

---
### SMS by Workato

**Provider value:**
```json
"provider": "sms"
```

---
### Snowflake

**Provider value:**
```json
"provider": "snowflake"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "host",
                  "type": "string",
                  "optional": false,
                  "label": "Account name",
                  "hint": "Account name of your Snowflake instance. This depends on the cloud platform (AWS or Azure)\nand region where your Snowflake instance is hosted.\n<a target=\"_blank\" href=\"https://docs.workato.com/connectors/snowflake.html#how-to-connect-to-snowflake-on-workato\">Learn more</a>."
              },
              {
                  "name": "warehouse",
                  "type": "string",
                  "label": "Warehouse",
                  "hint": "Full name of warehouse to perform all operations for this connection.\n<a target=\"_blank\" href=\"https://docs.workato.com/connectors/snowflake.html#considerations-for-warehouse\">Learn more</a>"
              },
              {
                  "name": "database",
                  "type": "string",
                  "label": "Database name"
              },
              {
                  "name": "user",
                  "type": "string",
                  "label": "User name"
              },
              {
                  "name": "password",
                  "type": "string",
                  "optional": false,
                  "label": "Password"
              },
              {
                  "name": "schema_name",
                  "type": "string",
                  "optional": true,
                  "label": "Schema",
                  "hint": "\"public\" schema by default"
              },
              {
                  "name": "db_timezone",
                  "type": "string",
                  "optional": true,
                  "label": "Database timezone",
                  "hint": "Apply this to all timestamps without timezone.\n<a target=\"_blank\" href=\"https://docs.workato.com/connectors/snowflake.html#database-timezone\">Learn more</a>",
                  "pick_list":
                  [
                      [
                          "American Samoa",
                          "American Samoa"
                      ],
                      [
                          "International Date Line West",
                          "International Date Line West"
                      ],
                      [
                          "Midway Island",
                          "Midway Island"
                      ],
                      [
                          "Hawaii",
                          "Hawaii"
                      ],
                      [
                          "Alaska",
                          "Alaska"
                      ],
                      [
                          "Pacific Time (US & Canada)",
                          "Pacific Time (US & Canada)"
                      ],
                      [
                          "Tijuana",
                          "Tijuana"
                      ],
                      [
                          "Arizona",
                          "Arizona"
                      ],
                      [
                          "Chihuahua",
                          "Chihuahua"
                      ],
                      [
                          "Mazatlan",
                          "Mazatlan"
                      ],
                      [
                          "Mountain Time (US & Canada)",
                          "Mountain Time (US & Canada)"
                      ],
                      [
                          "Central America",
                          "Central America"
                      ],
                      [
                          "Central Time (US & Canada)",
                          "Central Time (US & Canada)"
                      ],
                      [
                          "Guadalajara",
                          "Guadalajara"
                      ],
                      [
                          "Mexico City",
                          "Mexico City"
                      ],
                      [
                          "Monterrey",
                          "Monterrey"
                      ],
                      [
                          "Saskatchewan",
                          "Saskatchewan"
                      ],
                      [
                          "Bogota",
                          "Bogota"
                      ],
                      [
                          "Eastern Time (US & Canada)",
                          "Eastern Time (US & Canada)"
                      ],
                      [
                          "Indiana (East)",
                          "Indiana (East)"
                      ],
                      [
                          "Lima",
                          "Lima"
                      ],
                      [
                          "Quito",
                          "Quito"
                      ],
                      [
                          "Atlantic Time (Canada)",
                          "Atlantic Time (Canada)"
                      ],
                      [
                          "Caracas",
                          "Caracas"
                      ],
                      [
                          "Georgetown",
                          "Georgetown"
                      ],
                      [
                          "La Paz",
                          "La Paz"
                      ],
                      [
                          "Santiago",
                          "Santiago"
                      ],
                      [
                          "Newfoundland",
                          "Newfoundland"
                      ],
                      [
                          "Brasilia",
                          "Brasilia"
                      ],
                      [
                          "Buenos Aires",
                          "Buenos Aires"
                      ],
                      [
                          "Greenland",
                          "Greenland"
                      ],
                      [
                          "Montevideo",
                          "Montevideo"
                      ],
                      [
                          "Mid-Atlantic",
                          "Mid-Atlantic"
                      ],
                      [
                          "Azores",
                          "Azores"
                      ],
                      [
                          "Cape Verde Is.",
                          "Cape Verde Is."
                      ],
                      [
                          "Casablanca",
                          "Casablanca"
                      ],
                      [
                          "Dublin",
                          "Dublin"
                      ],
                      [
                          "Edinburgh",
                          "Edinburgh"
                      ],
                      [
                          "Lisbon",
                          "Lisbon"
                      ],
                      [
                          "London",
                          "London"
                      ],
                      [
                          "Monrovia",
                          "Monrovia"
                      ],
                      [
                          "UTC",
                          "UTC"
                      ],
                      [
                          "Amsterdam",
                          "Amsterdam"
                      ],
                      [
                          "Belgrade",
                          "Belgrade"
                      ],
                      [
                          "Berlin",
                          "Berlin"
                      ],
                      [
                          "Bern",
                          "Bern"
                      ],
                      [
                          "Bratislava",
                          "Bratislava"
                      ],
                      [
                          "Brussels",
                          "Brussels"
                      ],
                      [
                          "Budapest",
                          "Budapest"
                      ],
                      [
                          "Copenhagen",
                          "Copenhagen"
                      ],
                      [
                          "Ljubljana",
                          "Ljubljana"
                      ],
                      [
                          "Madrid",
                          "Madrid"
                      ],
                      [
                          "Paris",
                          "Paris"
                      ],
                      [
                          "Prague",
                          "Prague"
                      ],
                      [
                          "Rome",
                          "Rome"
                      ],
                      [
                          "Sarajevo",
                          "Sarajevo"
                      ],
                      [
                          "Skopje",
                          "Skopje"
                      ],
                      [
                          "Stockholm",
                          "Stockholm"
                      ],
                      [
                          "Vienna",
                          "Vienna"
                      ],
                      [
                          "Warsaw",
                          "Warsaw"
                      ],
                      [
                          "West Central Africa",
                          "West Central Africa"
                      ],
                      [
                          "Zagreb",
                          "Zagreb"
                      ],
                      [
                          "Athens",
                          "Athens"
                      ],
                      [
                          "Bucharest",
                          "Bucharest"
                      ],
                      [
                          "Cairo",
                          "Cairo"
                      ],
                      [
                          "Harare",
                          "Harare"
                      ],
                      [
                          "Helsinki",
                          "Helsinki"
                      ],
                      [
                          "Jerusalem",
                          "Jerusalem"
                      ],
                      [
                          "Kaliningrad",
                          "Kaliningrad"
                      ],
                      [
                          "Kyiv",
                          "Kyiv"
                      ],
                      [
                          "Pretoria",
                          "Pretoria"
                      ],
                      [
                          "Riga",
                          "Riga"
                      ],
                      [
                          "Sofia",
                          "Sofia"
                      ],
                      [
                          "Tallinn",
                          "Tallinn"
                      ],
                      [
                          "Vilnius",
                          "Vilnius"
                      ],
                      [
                          "Baghdad",
                          "Baghdad"
                      ],
                      [
                          "Istanbul",
                          "Istanbul"
                      ],
                      [
                          "Kuwait",
                          "Kuwait"
                      ],
                      [
                          "Minsk",
                          "Minsk"
                      ],
                      [
                          "Moscow",
                          "Moscow"
                      ],
                      [
                          "Nairobi",
                          "Nairobi"
                      ],
                      [
                          "Riyadh",
                          "Riyadh"
                      ],
                      [
                          "St. Petersburg",
                          "St. Petersburg"
                      ],
                      [
                          "Tehran",
                          "Tehran"
                      ],
                      [
                          "Abu Dhabi",
                          "Abu Dhabi"
                      ],
                      [
                          "Baku",
                          "Baku"
                      ],
                      [
                          "Muscat",
                          "Muscat"
                      ],
                      [
                          "Samara",
                          "Samara"
                      ],
                      [
                          "Tbilisi",
                          "Tbilisi"
                      ],
                      [
                          "Volgograd",
                          "Volgograd"
                      ],
                      [
                          "Yerevan",
                          "Yerevan"
                      ],
                      [
                          "Kabul",
                          "Kabul"
                      ],
                      [
                          "Ekaterinburg",
                          "Ekaterinburg"
                      ],
                      [
                          "Islamabad",
                          "Islamabad"
                      ],
                      [
                          "Karachi",
                          "Karachi"
                      ],
                      [
                          "Tashkent",
                          "Tashkent"
                      ],
                      [
                          "Chennai",
                          "Chennai"
                      ],
                      [
                          "Kolkata",
                          "Kolkata"
                      ],
                      [
                          "Mumbai",
                          "Mumbai"
                      ],
                      [
                          "New Delhi",
                          "New Delhi"
                      ],
                      [
                          "Sri Jayawardenepura",
                          "Sri Jayawardenepura"
                      ],
                      [
                          "Kathmandu",
                          "Kathmandu"
                      ],
                      [
                          "Almaty",
                          "Almaty"
                      ],
                      [
                          "Astana",
                          "Astana"
                      ],
                      [
                          "Dhaka",
                          "Dhaka"
                      ],
                      [
                          "Urumqi",
                          "Urumqi"
                      ],
                      [
                          "Rangoon",
                          "Rangoon"
                      ],
                      [
                          "Bangkok",
                          "Bangkok"
                      ],
                      [
                          "Hanoi",
                          "Hanoi"
                      ],
                      [
                          "Jakarta",
                          "Jakarta"
                      ],
                      [
                          "Krasnoyarsk",
                          "Krasnoyarsk"
                      ],
                      [
                          "Novosibirsk",
                          "Novosibirsk"
                      ],
                      [
                          "Beijing",
                          "Beijing"
                      ],
                      [
                          "Chongqing",
                          "Chongqing"
                      ],
                      [
                          "Hong Kong",
                          "Hong Kong"
                      ],
                      [
                          "Irkutsk",
                          "Irkutsk"
                      ],
                      [
                          "Kuala Lumpur",
                          "Kuala Lumpur"
                      ],
                      [
                          "Perth",
                          "Perth"
                      ],
                      [
                          "Singapore",
                          "Singapore"
                      ],
                      [
                          "Taipei",
                          "Taipei"
                      ],
                      [
                          "Ulaanbaatar",
                          "Ulaanbaatar"
                      ],
                      [
                          "Osaka",
                          "Osaka"
                      ],
                      [
                          "Sapporo",
                          "Sapporo"
                      ],
                      [
                          "Seoul",
                          "Seoul"
                      ],
                      [
                          "Tokyo",
                          "Tokyo"
                      ],
                      [
                          "Yakutsk",
                          "Yakutsk"
                      ],
                      [
                          "Adelaide",
                          "Adelaide"
                      ],
                      [
                          "Darwin",
                          "Darwin"
                      ],
                      [
                          "Brisbane",
                          "Brisbane"
                      ],
                      [
                          "Canberra",
                          "Canberra"
                      ],
                      [
                          "Guam",
                          "Guam"
                      ],
                      [
                          "Hobart",
                          "Hobart"
                      ],
                      [
                          "Melbourne",
                          "Melbourne"
                      ],
                      [
                          "Port Moresby",
                          "Port Moresby"
                      ],
                      [
                          "Sydney",
                          "Sydney"
                      ],
                      [
                          "Vladivostok",
                          "Vladivostok"
                      ],
                      [
                          "Magadan",
                          "Magadan"
                      ],
                      [
                          "New Caledonia",
                          "New Caledonia"
                      ],
                      [
                          "Solomon Is.",
                          "Solomon Is."
                      ],
                      [
                          "Srednekolymsk",
                          "Srednekolymsk"
                      ],
                      [
                          "Auckland",
                          "Auckland"
                      ],
                      [
                          "Fiji",
                          "Fiji"
                      ],
                      [
                          "Kamchatka",
                          "Kamchatka"
                      ],
                      [
                          "Marshall Is.",
                          "Marshall Is."
                      ],
                      [
                          "Wellington",
                          "Wellington"
                      ],
                      [
                          "Chatham Is.",
                          "Chatham Is."
                      ],
                      [
                          "Nuku'alofa",
                          "Nuku'alofa"
                      ],
                      [
                          "Samoa",
                          "Samoa"
                      ],
                      [
                          "Tokelau Is.",
                          "Tokelau Is."
                      ]
                  ]
              }
          ]
      }
```
:::

---
### Snowflake (Secondary)

**Provider value:**
```json
"provider": "snowflake_secondary"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "host",
                  "type": "string",
                  "optional": false,
                  "label": "Account name",
                  "hint": "Account name of your Snowflake instance. This depends on the cloud platform (AWS or Azure)\nand region where your Snowflake instance is hosted.\n<a target=\"_blank\" href=\"https://docs.workato.com/connectors/snowflake.html#how-to-connect-to-snowflake-on-workato\">Learn more</a>."
              },
              {
                  "name": "warehouse",
                  "type": "string",
                  "label": "Warehouse",
                  "hint": "Full name of warehouse to perform all operations for this connection.\n<a target=\"_blank\" href=\"https://docs.workato.com/connectors/snowflake.html#considerations-for-warehouse\">Learn more</a>"
              },
              {
                  "name": "database",
                  "type": "string",
                  "label": "Database name"
              },
              {
                  "name": "user",
                  "type": "string",
                  "label": "User name"
              },
              {
                  "name": "password",
                  "type": "string",
                  "optional": false,
                  "label": "Password"
              },
              {
                  "name": "schema_name",
                  "type": "string",
                  "optional": true,
                  "label": "Schema",
                  "hint": "\"public\" schema by default"
              },
              {
                  "name": "db_timezone",
                  "type": "string",
                  "optional": true,
                  "label": "Database timezone",
                  "hint": "Apply this to all timestamps without timezone.\n<a target=\"_blank\" href=\"https://docs.workato.com/connectors/snowflake.html#database-timezone\">Learn more</a>",
                  "pick_list":
                  [
                      [
                          "American Samoa",
                          "American Samoa"
                      ],
                      [
                          "International Date Line West",
                          "International Date Line West"
                      ],
                      [
                          "Midway Island",
                          "Midway Island"
                      ],
                      [
                          "Hawaii",
                          "Hawaii"
                      ],
                      [
                          "Alaska",
                          "Alaska"
                      ],
                      [
                          "Pacific Time (US & Canada)",
                          "Pacific Time (US & Canada)"
                      ],
                      [
                          "Tijuana",
                          "Tijuana"
                      ],
                      [
                          "Arizona",
                          "Arizona"
                      ],
                      [
                          "Chihuahua",
                          "Chihuahua"
                      ],
                      [
                          "Mazatlan",
                          "Mazatlan"
                      ],
                      [
                          "Mountain Time (US & Canada)",
                          "Mountain Time (US & Canada)"
                      ],
                      [
                          "Central America",
                          "Central America"
                      ],
                      [
                          "Central Time (US & Canada)",
                          "Central Time (US & Canada)"
                      ],
                      [
                          "Guadalajara",
                          "Guadalajara"
                      ],
                      [
                          "Mexico City",
                          "Mexico City"
                      ],
                      [
                          "Monterrey",
                          "Monterrey"
                      ],
                      [
                          "Saskatchewan",
                          "Saskatchewan"
                      ],
                      [
                          "Bogota",
                          "Bogota"
                      ],
                      [
                          "Eastern Time (US & Canada)",
                          "Eastern Time (US & Canada)"
                      ],
                      [
                          "Indiana (East)",
                          "Indiana (East)"
                      ],
                      [
                          "Lima",
                          "Lima"
                      ],
                      [
                          "Quito",
                          "Quito"
                      ],
                      [
                          "Atlantic Time (Canada)",
                          "Atlantic Time (Canada)"
                      ],
                      [
                          "Caracas",
                          "Caracas"
                      ],
                      [
                          "Georgetown",
                          "Georgetown"
                      ],
                      [
                          "La Paz",
                          "La Paz"
                      ],
                      [
                          "Santiago",
                          "Santiago"
                      ],
                      [
                          "Newfoundland",
                          "Newfoundland"
                      ],
                      [
                          "Brasilia",
                          "Brasilia"
                      ],
                      [
                          "Buenos Aires",
                          "Buenos Aires"
                      ],
                      [
                          "Greenland",
                          "Greenland"
                      ],
                      [
                          "Montevideo",
                          "Montevideo"
                      ],
                      [
                          "Mid-Atlantic",
                          "Mid-Atlantic"
                      ],
                      [
                          "Azores",
                          "Azores"
                      ],
                      [
                          "Cape Verde Is.",
                          "Cape Verde Is."
                      ],
                      [
                          "Casablanca",
                          "Casablanca"
                      ],
                      [
                          "Dublin",
                          "Dublin"
                      ],
                      [
                          "Edinburgh",
                          "Edinburgh"
                      ],
                      [
                          "Lisbon",
                          "Lisbon"
                      ],
                      [
                          "London",
                          "London"
                      ],
                      [
                          "Monrovia",
                          "Monrovia"
                      ],
                      [
                          "UTC",
                          "UTC"
                      ],
                      [
                          "Amsterdam",
                          "Amsterdam"
                      ],
                      [
                          "Belgrade",
                          "Belgrade"
                      ],
                      [
                          "Berlin",
                          "Berlin"
                      ],
                      [
                          "Bern",
                          "Bern"
                      ],
                      [
                          "Bratislava",
                          "Bratislava"
                      ],
                      [
                          "Brussels",
                          "Brussels"
                      ],
                      [
                          "Budapest",
                          "Budapest"
                      ],
                      [
                          "Copenhagen",
                          "Copenhagen"
                      ],
                      [
                          "Ljubljana",
                          "Ljubljana"
                      ],
                      [
                          "Madrid",
                          "Madrid"
                      ],
                      [
                          "Paris",
                          "Paris"
                      ],
                      [
                          "Prague",
                          "Prague"
                      ],
                      [
                          "Rome",
                          "Rome"
                      ],
                      [
                          "Sarajevo",
                          "Sarajevo"
                      ],
                      [
                          "Skopje",
                          "Skopje"
                      ],
                      [
                          "Stockholm",
                          "Stockholm"
                      ],
                      [
                          "Vienna",
                          "Vienna"
                      ],
                      [
                          "Warsaw",
                          "Warsaw"
                      ],
                      [
                          "West Central Africa",
                          "West Central Africa"
                      ],
                      [
                          "Zagreb",
                          "Zagreb"
                      ],
                      [
                          "Athens",
                          "Athens"
                      ],
                      [
                          "Bucharest",
                          "Bucharest"
                      ],
                      [
                          "Cairo",
                          "Cairo"
                      ],
                      [
                          "Harare",
                          "Harare"
                      ],
                      [
                          "Helsinki",
                          "Helsinki"
                      ],
                      [
                          "Jerusalem",
                          "Jerusalem"
                      ],
                      [
                          "Kaliningrad",
                          "Kaliningrad"
                      ],
                      [
                          "Kyiv",
                          "Kyiv"
                      ],
                      [
                          "Pretoria",
                          "Pretoria"
                      ],
                      [
                          "Riga",
                          "Riga"
                      ],
                      [
                          "Sofia",
                          "Sofia"
                      ],
                      [
                          "Tallinn",
                          "Tallinn"
                      ],
                      [
                          "Vilnius",
                          "Vilnius"
                      ],
                      [
                          "Baghdad",
                          "Baghdad"
                      ],
                      [
                          "Istanbul",
                          "Istanbul"
                      ],
                      [
                          "Kuwait",
                          "Kuwait"
                      ],
                      [
                          "Minsk",
                          "Minsk"
                      ],
                      [
                          "Moscow",
                          "Moscow"
                      ],
                      [
                          "Nairobi",
                          "Nairobi"
                      ],
                      [
                          "Riyadh",
                          "Riyadh"
                      ],
                      [
                          "St. Petersburg",
                          "St. Petersburg"
                      ],
                      [
                          "Tehran",
                          "Tehran"
                      ],
                      [
                          "Abu Dhabi",
                          "Abu Dhabi"
                      ],
                      [
                          "Baku",
                          "Baku"
                      ],
                      [
                          "Muscat",
                          "Muscat"
                      ],
                      [
                          "Samara",
                          "Samara"
                      ],
                      [
                          "Tbilisi",
                          "Tbilisi"
                      ],
                      [
                          "Volgograd",
                          "Volgograd"
                      ],
                      [
                          "Yerevan",
                          "Yerevan"
                      ],
                      [
                          "Kabul",
                          "Kabul"
                      ],
                      [
                          "Ekaterinburg",
                          "Ekaterinburg"
                      ],
                      [
                          "Islamabad",
                          "Islamabad"
                      ],
                      [
                          "Karachi",
                          "Karachi"
                      ],
                      [
                          "Tashkent",
                          "Tashkent"
                      ],
                      [
                          "Chennai",
                          "Chennai"
                      ],
                      [
                          "Kolkata",
                          "Kolkata"
                      ],
                      [
                          "Mumbai",
                          "Mumbai"
                      ],
                      [
                          "New Delhi",
                          "New Delhi"
                      ],
                      [
                          "Sri Jayawardenepura",
                          "Sri Jayawardenepura"
                      ],
                      [
                          "Kathmandu",
                          "Kathmandu"
                      ],
                      [
                          "Almaty",
                          "Almaty"
                      ],
                      [
                          "Astana",
                          "Astana"
                      ],
                      [
                          "Dhaka",
                          "Dhaka"
                      ],
                      [
                          "Urumqi",
                          "Urumqi"
                      ],
                      [
                          "Rangoon",
                          "Rangoon"
                      ],
                      [
                          "Bangkok",
                          "Bangkok"
                      ],
                      [
                          "Hanoi",
                          "Hanoi"
                      ],
                      [
                          "Jakarta",
                          "Jakarta"
                      ],
                      [
                          "Krasnoyarsk",
                          "Krasnoyarsk"
                      ],
                      [
                          "Novosibirsk",
                          "Novosibirsk"
                      ],
                      [
                          "Beijing",
                          "Beijing"
                      ],
                      [
                          "Chongqing",
                          "Chongqing"
                      ],
                      [
                          "Hong Kong",
                          "Hong Kong"
                      ],
                      [
                          "Irkutsk",
                          "Irkutsk"
                      ],
                      [
                          "Kuala Lumpur",
                          "Kuala Lumpur"
                      ],
                      [
                          "Perth",
                          "Perth"
                      ],
                      [
                          "Singapore",
                          "Singapore"
                      ],
                      [
                          "Taipei",
                          "Taipei"
                      ],
                      [
                          "Ulaanbaatar",
                          "Ulaanbaatar"
                      ],
                      [
                          "Osaka",
                          "Osaka"
                      ],
                      [
                          "Sapporo",
                          "Sapporo"
                      ],
                      [
                          "Seoul",
                          "Seoul"
                      ],
                      [
                          "Tokyo",
                          "Tokyo"
                      ],
                      [
                          "Yakutsk",
                          "Yakutsk"
                      ],
                      [
                          "Adelaide",
                          "Adelaide"
                      ],
                      [
                          "Darwin",
                          "Darwin"
                      ],
                      [
                          "Brisbane",
                          "Brisbane"
                      ],
                      [
                          "Canberra",
                          "Canberra"
                      ],
                      [
                          "Guam",
                          "Guam"
                      ],
                      [
                          "Hobart",
                          "Hobart"
                      ],
                      [
                          "Melbourne",
                          "Melbourne"
                      ],
                      [
                          "Port Moresby",
                          "Port Moresby"
                      ],
                      [
                          "Sydney",
                          "Sydney"
                      ],
                      [
                          "Vladivostok",
                          "Vladivostok"
                      ],
                      [
                          "Magadan",
                          "Magadan"
                      ],
                      [
                          "New Caledonia",
                          "New Caledonia"
                      ],
                      [
                          "Solomon Is.",
                          "Solomon Is."
                      ],
                      [
                          "Srednekolymsk",
                          "Srednekolymsk"
                      ],
                      [
                          "Auckland",
                          "Auckland"
                      ],
                      [
                          "Fiji",
                          "Fiji"
                      ],
                      [
                          "Kamchatka",
                          "Kamchatka"
                      ],
                      [
                          "Marshall Is.",
                          "Marshall Is."
                      ],
                      [
                          "Wellington",
                          "Wellington"
                      ],
                      [
                          "Chatham Is.",
                          "Chatham Is."
                      ],
                      [
                          "Nuku'alofa",
                          "Nuku'alofa"
                      ],
                      [
                          "Samoa",
                          "Samoa"
                      ],
                      [
                          "Tokelau Is.",
                          "Tokelau Is."
                      ]
                  ]
              }
          ]
      }
```
:::

---
### SOAP tools by Workato

**Provider value:**
```json
"provider": "soap"
```

---
### Splunk

**Provider value:**
```json
"provider": "splunk"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "server_url",
                  "type": "string",
                  "label": "Server URL",
                  "hint": "                   The URL of the Splunk management port (for example, https://yourdomain:8089).\n                   You MUST install the <a href='https://splunkbase.splunk.com/apps/#/search/workato'>Workato Add-on for Splunk</a> first.\n"
              },
              {
                  "name": "username",
                  "type": "string",
                  "label": "Username",
                  "hint": "The Splunk username (for example, admin)"
              },
              {
                  "name": "password",
                  "type": "string",
                  "label": "Password",
                  "hint": "The password for the Splunk username"
              }
          ]
      }
```
:::

---
### SQL Server

**Provider value:**
```json
"provider": "mssql"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "profile",
                  "type": "string",
                  "label": "On-prem connection profile"
              },
              {
                  "name": "username",
                  "type": "string",
                  "label": "Username",
                  "hint": "For Azure SQL use username@server"
              },
              {
                  "name": "password",
                  "type": "string",
                  "label": "Password"
              },
              {
                  "name": "host",
                  "type": "string",
                  "label": "Host"
              },
              {
                  "name": "port",
                  "type": "string",
                  "optional": true,
                  "label": "Port",
                  "hint": "Port number, default is 1433",
                  "default": 1433
              },
              {
                  "name": "database",
                  "type": "string",
                  "label": "Database"
              },
              {
                  "name": "azure",
                  "type": "boolean",
                  "optional": true,
                  "label": "Azure SQL",
                  "hint": "Choose 'yes' if connecting to Azure SQL",
                  "default": "false"
              }
          ]
      }
```
:::

---
### SQL Server (Secondary)

**Provider value:**
```json
"provider": "mssql_secondary"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "profile",
                  "type": "string",
                  "label": "On-prem connection profile"
              },
              {
                  "name": "username",
                  "type": "string",
                  "label": "Username",
                  "hint": "For Azure SQL use username@server"
              },
              {
                  "name": "password",
                  "type": "string",
                  "label": "Password"
              },
              {
                  "name": "host",
                  "type": "string",
                  "label": "Host"
              },
              {
                  "name": "port",
                  "type": "string",
                  "optional": true,
                  "label": "Port",
                  "hint": "Port number, default is 1433",
                  "default": 1433
              },
              {
                  "name": "database",
                  "type": "string",
                  "label": "Database"
              },
              {
                  "name": "azure",
                  "type": "boolean",
                  "optional": true,
                  "label": "Azure SQL",
                  "hint": "Choose 'yes' if connecting to Azure SQL",
                  "default": "false"
              }
          ]
      }
```
:::

---
### Stripe

**Provider value:**
```json
"provider": "stripe"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "demo",
                  "type": "boolean",
                  "optional": true,
                  "label": "Demo",
                  "hint": "Is this connecting to a demo account?",
                  "default": "false"
              }
          ]
      }
```
:::

---
### SuccessFactors

**Provider value:**
```json
"provider": "success_factors"
```

---
### SurveyMonkey

**Provider value:**
```json
"provider": "surveymonkey"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Tango Card

**Provider value:**
```json
"provider": "tango_card"
```

---
### TaskRay

**Provider value:**
```json
"provider": "taskray"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "sandbox",
                  "type": "boolean",
                  "optional": true,
                  "label": "Sandbox",
                  "hint": "Is this connecting to a sandbox account?",
                  "default": "false"
              }
          ]
      }
```
:::

---
### TrackVia

**Provider value:**
```json
"provider": "trackvia"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "custom_domain",
                  "type": "string",
                  "optional": "true",
                  "label": "TrackVia subdomain",
                  "hint": "Enter your TrackVia subdomain. For example, customdomain.trackvia.com. By default, <b>go.trackvia.com</b> will be used."
              }
          ]
      }
```
:::

---
### Tradeshift

**Provider value:**
```json
"provider": "tradeshift"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "sandbox",
                  "type": "boolean",
                  "optional": true,
                  "label": "Sandbox",
                  "hint": "              If <b>yes</b>, click <a target='_blank' href=https://sandbox.tradeshift.com/#/apps/Tradeshift.AppStore/apps/Workato.tradeshiftAdapterProduction>here</a> to activate your sandbox account else click <a target='_blank' href=https://go.tradeshift.com/#/apps/Tradeshift.AppStore/apps/Workato.tradeshiftAdapterProduction>here</a> to activate your production account.\n",
                  "default": "false"
              }
          ]
      }
```
:::

---
### Trello

**Provider value:**
```json
"provider": "trello"
```

Connection parameter configuration **_is not required_** for this connector.

---
### TSheets

**Provider value:**
```json
"provider": "tsheets"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Twilio

**Provider value:**
```json
"provider": "twilio"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "sid",
                  "type": "string",
                  "label": "Account SID",
                  "hint": "See your Twilio <a href=\"https://www.twilio.com/user/account\">account page</a>"
              },
              {
                  "name": "token",
                  "type": "string",
                  "label": "Auth token",
                  "hint": "See your Twilio <a href=\"https://www.twilio.com/user/account\">account page</a>"
              }
          ]
      }
```
:::

---
### Twitter

**Provider value:**
```json
"provider": "twitter"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Twitter Ads

**Provider value:**
```json
"provider": "twitter_ads"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Unbounce

**Provider value:**
```json
"provider": "unbounce"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "api_key",
                  "type": "string",
                  "optional": false,
                  "label": "Api key",
                  "hint": "Profile (top right) > Manage Account > API Access"
              }
          ]
      }
```
:::

---
### Utilities

**Provider value:**
```json
"provider": "utility"
```

---
### Variables by Workato

**Provider value:**
```json
"provider": "workato_variable"
```

---
### Veeva CRM

**Provider value:**
```json
"provider": "veeva"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "sandbox",
                  "type": "boolean",
                  "optional": true,
                  "label": "Sandbox",
                  "hint": "Is this connecting to a sandbox account?",
                  "default": "false"
              }
          ]
      }
```
:::

---
### Vend

**Provider value:**
```json
"provider": "vend"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Vlocity

**Provider value:**
```json
"provider": "vlocity"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "sandbox",
                  "type": "boolean",
                  "optional": true,
                  "label": "Sandbox",
                  "hint": "Is this connecting to a sandbox account?",
                  "default": "false"
              }
          ]
      }
```
:::

---
### Watson Tone Analyzer

**Provider value:**
```json
"provider": "watson_tone_analyzer"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "username",
                  "type": "string",
                  "optional": false,
                  "label": "Username",
                  "hint": "Require Cloud Foundry service credentials. <a href='https://cloud.ibm.com/docs/services/watson?topic=watson-creating-credentials#creating-credentials' target='_blank'>Learn more</a>"
              },
              {
                  "name": "password",
                  "type": "string",
                  "optional": false,
                  "label": "Password",
                  "hint": "Require Cloud Foundry service credentials. <a href='https://cloud.ibm.com/docs/services/watson?topic=watson-creating-credentials#creating-credentials' target='_blank'>Learn more</a>"
              }
          ]
      }
```
:::

---
### Webhooks

**Provider value:**
```json
"provider": "workato_webhooks"
```

---
### WebMerge

**Provider value:**
```json
"provider": "webmerge"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "api_key",
                  "type": "string",
                  "optional": false,
                  "label": "API key",
                  "hint": "Select your profile icon->Api Access to get the API key"
              },
              {
                  "name": "api_secret",
                  "type": "string",
                  "optional": false,
                  "label": "API secret",
                  "hint": "Select your profile icon->Api Access to get the API secret"
              }
          ]
      }
```
:::

---
### WooCommerce

**Provider value:**
```json
"provider": "woocommerce"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "consumer_key",
                  "type": "string",
                  "label": "Consumer key",
                  "hint": "Consumer key is found at API tab of WooCommerce settings"
              },
              {
                  "name": "consumer_secret",
                  "type": "string",
                  "label": "Consumer secret",
                  "hint": "Consumer secret is found at API tab of WooCommerce settings"
              },
              {
                  "name": "host",
                  "type": "string",
                  "label": "Host",
                  "hint": "If your WooCommerce home page url is https://app.Woocommerce.com, then use app.Woocommerce.com"
              },
              {
                  "name": "order_ids",
                  "type": "string",
                  "optional": true,
                  "label": "Example order IDs",
                  "hint": "Comma separated order IDs to sample custom fields. Takes up to 3 values"
              }
          ]
      }
```
:::

---
<h3>WordPress.com</h3>

**Provider value:**
```json
"provider": "word_press"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Workato Track
**Provider value:**
```json
"provider": "workato_track"
```
---
### Workbot for Microsoft Teams
**Provider value:**
```json
"provider": "teams_bot"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Workbot for Microsoft Teams Old

**Provider value:**
```json
"provider": "skype_bot"
```

Connection parameter configuration **_is not required_** for this connector.

---
### Workbot for Slack

**Provider value:**
```json
"provider": "slack_bot"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "nlu_provider_shared_account_id",
                  "type": "string",
                  "optional": true,
                  "label": "NLU provider",
                  "hint": "Choose a connection for your conversational interface. Supports Google's DialogFlow and Amazon Lex."
              },
              {
                  "name": "advanced",
                  "type": "object",
                  "optional": true,
                  "label": "Advanced",
                  "hint": "Additional fields that are not needed for most users",
                  "properties":
                  [
                      {
                          "name": "extra_tokens",
                          "type": "string",
                          "optional": true,
                          "label": "Slash commands verification tokens",
                          "hint": "Used for invoking Custom Integration slash commands. Each slash command has a token. Separate tokens with commas to support multiple slash commands. <a href='https://docs.workato.com/workbot/legacy-slash-commands.html#configuring-the-workbot-connection' target='_blank'>Learn more.</a>"
                      },
                      {
                          "name": "custom_help",
                          "type": "string",
                          "optional": true,
                          "label": "Custom help",
                          "hint": "Provide simple text help OR rich help using a JSON document corresponding to Slack message.You can build a rich help message using the <a href='https://api.slack.com/docs/messages/builder' target='_blank'>Slack message builder.</a>"
                      }
                  ]
              }
          ]
      }
```
:::

---
### Workbot for Workplace

**Provider value:**
```json
"provider": "workplace_bot"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "custom_access_token",
                  "type": "string",
                  "optional": true,
                  "label": "Custom Access Token"
              }
          ]
      }
```
:::

---
### Workday

**Provider value:**
```json
"provider": "workday"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": false,
          "input":
          [
              {
                  "name": "login",
                  "type": "string",
                  "label": "Login name"
              },
              {
                  "name": "password",
                  "type": "string",
                  "label": "Password"
              },
              {
                  "name": "soap_api_version",
                  "type": "string",
                  "label": "Workday web services version",
                  "pick_list":
                  [
                      [
                          "29.0",
                          "29.0"
                      ],
                      [
                          "32.2",
                          "32.2"
                      ]
                  ],
                  "default": "29.0"
              },
              {
                  "name": "tenant_id",
                  "type": "string",
                  "label": "Tenant ID",
                  "hint": "Tenant ID can be found in the URL when you are logged into Workday.<br>\n    For example in https://impl.workday.com/sample_company/d/home.htmld, tenant ID is sample_company"
              },
              {
                  "name": "base_uri",
                  "type": "string",
                  "label": "WSDL URL",
                  "hint": "You need to provide any wsdl url. <br>\n    The manual how to get it could be found <a href='https://community.workday.com/articles/6120#endpoint' target='_blank'>here</a>",
                  "default": "https://wd2-impl-services1.workday.com/ccx/service/"
              },
              {
                  "name": "oauth",
                  "type": "boolean",
                  "label": "use custom objects?",
                  "hint": "Working with custom objects in Workday requires additional connection settings."
              },
              {
                  "name": "client_id",
                  "type": "string",
                  "optional": true,
                  "label": "Client ID",
                  "hint": "Found in API Client settings"
              },
              {
                  "name": "client_secret",
                  "type": "string",
                  "optional": true,
                  "label": "Client secret",
                  "hint": "Found in API Client settings"
              },
              {
                  "name": "refresh_token",
                  "type": "string",
                  "optional": true,
                  "label": "Refresh token",
                  "hint": "If API client for Integrations is used"
              },
              {
                  "name": "authorization_endpoint",
                  "type": "string",
                  "optional": true,
                  "label": "Authorization endpoint",
                  "hint": "Found in API Client settings"
              },
              {
                  "name": "token_endpoint",
                  "type": "string",
                  "optional": true,
                  "label": "Token endpoint",
                  "hint": "Found in API Client settings"
              }
          ]
      }
```
:::

---
### Workday REST

**Provider value:**
```json
"provider": "workday_rest"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "rest_api_endpoint",
                  "type": "string",
                  "label": "REST API endpoint",
                  "hint": "                 Found in the API client details page. Learn how to register an API client\n                 <a href='https://docs.workato.com/connectors/workday/connection_setup.html#register-api-client' target=_blank>here</a>.\n",
                  "default": "https://wd2-impl-services1.workday.com/ccx/service/acme"
              },
              {
                  "name": "authorization_endpoint",
                  "type": "string",
                  "label": "Authorization endpoint",
                  "hint": "Found in the API client details page."
              },
              {
                  "name": "token_endpoint",
                  "type": "string",
                  "label": "Token endpoint",
                  "hint": "Found in the API client details page."
              },
              {
                  "name": "client_id",
                  "type": "string",
                  "label": "Client ID",
                  "hint": "Found in the API client details page."
              },
              {
                  "name": "client_secret",
                  "type": "string",
                  "label": "Client secret",
                  "hint": "Found in the API client details page."
              },
              {
                  "name": "refresh_token",
                  "type": "string",
                  "optional": true,
                  "label": "Refresh token",
                  "hint": "                 Provide a refresh token if this connection needs to be authorized by an integration user instead of a user account.\n                 Authorization step will be skipped.\n"
              }
          ]
      }
```
:::

---
### Workday Web Services

**Provider value:**
```json
"provider": "workday_oauth"
```

---
### Workfront

**Provider value:**
```json
"provider": "workfront"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "username",
                  "type": "string",
                  "optional": false,
                  "label": "Username",
                  "hint": "Your Workfront username."
              },
              {
                  "name": "password",
                  "type": "string",
                  "optional": false,
                  "label": "Password",
                  "hint": "Your Workfront password."
              },
              {
                  "name": "subdomain",
                  "type": "string",
                  "optional": false,
                  "label": "Subdomain",
                  "hint": "Your Workfront subdomain name as found in your Workfront URL."
              }
          ]
      }
```
:::

---
### Workfront (Secondary)

**Provider value:**
```json
"provider": "workfront_secondary"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "username",
                  "type": "string",
                  "optional": false,
                  "label": "Username",
                  "hint": "Your Workfront username."
              },
              {
                  "name": "password",
                  "type": "string",
                  "optional": false,
                  "label": "Password",
                  "hint": "Your Workfront password."
              },
              {
                  "name": "subdomain",
                  "type": "string",
                  "optional": false,
                  "label": "Subdomain",
                  "hint": "Your Workfront subdomain name as found in your Workfront URL."
              }
          ]
      }
```
:::

---
### Wrike

**Provider value:**
```json
"provider": "wrike"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "advanced_settings",
                  "type": "object",
                  "optional": true,
                  "label": "Advanced settings",
                  "properties":
                  [
                      {
                          "name": "api_scope",
                          "type": "string",
                          "optional": true,
                          "label": "Api scope",
                          "hint": "               Select <a href=\"https://developers.wrike.com/documentation/api/overview\" target=\"_blank\">permissions</a>\n               to request for this connection. Defaults to <b>Default</b> if left blank.\n               <br/>Minimum permissions required is <b>Default</b>, which will be always requested in addition to selected permissions.\n"
                      }
                  ]
              }
          ]
      }
```
:::

---
### Wrike (Secondary)

**Provider value:**
```json
"provider": "wrike_secondary"
```

::: details View connection parameters JSON
```json
      {
          "oauth": true,
          "personalization": true,
          "input":
          [
              {
                  "name": "advanced_settings",
                  "type": "object",
                  "optional": true,
                  "label": "Advanced settings",
                  "properties":
                  [
                      {
                          "name": "api_scope",
                          "type": "string",
                          "optional": true,
                          "label": "Api scope",
                          "hint": "               Select <a href=\"https://developers.wrike.com/documentation/api/overview\" target=\"_blank\">permissions</a>\n               to request for this connection. Defaults to <b>Default</b> if left blank.\n               <br/>Minimum permissions required is <b>Default</b>, which will be always requested in addition to selected permissions.\n"
                      }
                  ]
              }
          ]
      }
```
:::

---
### Wufoo

**Provider value:**
```json
"provider": "wufoo"
```

::: details View connection parameters JSON
```json
      {
          "oauth": false,
          "personalization": false,
          "input":
          [
              {
                  "name": "api_key",
                  "type": "string",
                  "label": "API key",
                  "hint": "<a href=\"http://www.wufoo.com/docs/api/v3/#key\" target=\"_blank\">How do I find the Wufoo API key?</a>"
              },
              {
                  "name": "subdomain",
                  "type": "string",
                  "label": "Sub-domain",
                  "hint": "Enter only the subdomain (located before .wufoo.com)"
              }
          ]
      }
```
:::

---
### Xactly

**Provider value:**
```json
"provider": "xactly"
```

::: details View connection parameters JSON
```json
      {
         "oauth":false,
         "personalization":false,
         "input":[
            {
               "name":"subdomain",
               "type":"string",
               "optional":false,
               "label":"Sub-domain"
            },
            {
               "name":"client_id",
               "type":"string",
               "optional":false,
               "label":"Client ID"
            },
            {
               "name":"consumer",
               "type":"string",
               "optional":false,
               "label":"Consumer"
            },
            {
               "name":"username",
               "type":"string",
               "optional":false,
               "label":"Username"
            },
            {
               "name":"password",
               "type":"string",
               "optional":false,
               "label":"Password"
            }
         ]
      }
```
:::

---
### Xero

**Provider value:**
```json
"provider": "xero"
```

::: details View connection parameters JSON
```json
      {
         "oauth":true,
         "personalization":true,
         "input":[
            {
               "name":"payroll",
               "type":"boolean",
               "optional":true,
               "label":"Payroll",
               "hint":"Select 'Yes' if Xero account is enabled for payroll, note that payroll connectivity is only available in AU and US editions",
               "default":"false"
            }
         ]
      }
```
:::

---
### Xero Practice Manager

**Provider value:**
```json
"provider": "xero_practice_manager"
```

---
### XML tools by Workato

**Provider value:**
```json
"provider": "xml_tools"
```

---
### YAML parser by Workato

**Provider value:**
```json
"provider": "yaml_parser"
```

---
### Zendesk

**Provider value:**
```json
"provider": "zendesk"
```

::: details View connection parameters JSON
```json
      {
         "oauth":true,
         "personalization":true,
         "input":[
            {
               "name":"subdomain",
               "type":"string",
               "label":"Subdomain",
               "hint":"If your Zendesk URL is https://acme.zendesk.com then your subdomain is <b>acme</b>"
            },
            {
               "name":"authentication_type",
               "type":"string",
               "label":"Authentication type",
               "pick_list":[
                  [
                     "Basic",
                     "basic"
                  ],
                  [
                     "OAuth 2.0",
                     "oauth"
                  ]
               ],
               "default":"oauth"
            },
            {
               "name":"username",
               "type":"string",
               "label":"Username",
               "hint":"When authenticating with tokens, add <b>/token</b> to the end of your username."
            },
            {
               "name":"password",
               "type":"string",
               "label":"Password",
               "hint":"                   Enter api token if you are using api token authentication. Click <a href='https://support.zendesk.com/hc/en-us/articles/226022787-Generating-a-new-API-token-' target=\"_blank\">here</a> to generate api token.\n"
            }
         ]
      }
```
:::

---
### Zendesk (Secondary)

**Provider value:**
```json
"provider": "zendesk_secondary"
```

::: details View connection parameters JSON
```json
      {
         "oauth":true,
         "personalization":true,
         "input":[
            {
               "name":"subdomain",
               "type":"string",
               "label":"Subdomain",
               "hint":"If your Zendesk URL is https://acme.zendesk.com then your subdomain is <b>acme</b>"
            },
            {
               "name":"authentication_type",
               "type":"string",
               "label":"Authentication type",
               "pick_list":[
                  [
                     "Basic",
                     "basic"
                  ],
                  [
                     "OAuth 2.0",
                     "oauth"
                  ]
               ],
               "default":"oauth"
            },
            {
               "name":"username",
               "type":"string",
               "label":"Username",
               "hint":"When authenticating with tokens, add <b>/token</b> to the end of your username."
            },
            {
               "name":"password",
               "type":"string",
               "label":"Password",
               "hint":"                   Enter api token if you are using api token authentication. Click <a href='https://support.zendesk.com/hc/en-us/articles/226022787-Generating-a-new-API-token-' target=\"_blank\">here</a> to generate api token.\n"
            }
         ]
      }
```
:::

---
### Zendesk Sunshine

**Provider value:**
```json
"provider": "zendesk_sunshine"
```

---
### Zenefits

**Provider value:**
```json
"provider": "zenefits"
```

::: details View connection parameters JSON
```json
      {
         "oauth":true,
         "personalization":true,
         "input":[

         ]
      }
```
:::

---
### Zoho CRM

**Provider value:**
```json
"provider": "zohocrm"
```

::: details View connection parameters JSON
```json
      {
         "oauth":true,
         "personalization":true,
         "input":[
            {
               "name":"timezone",
               "type":"string",
               "optional":true,
               "label":"Account timezone",
               "hint":"Needed for consistency with Zoho - pick same as your Zoho profile",
               "pick_list":[
                  [
                     "American Samoa (-11:00)",
                     "American Samoa"
                  ],
                  [
                     "International Date Line West (-11:00)",
                     "International Date Line West"
                  ],
                  [
                     "Midway Island (-11:00)",
                     "Midway Island"
                  ],
                  [
                     "Hawaii (-10:00)",
                     "Hawaii"
                  ],
                  [
                     "Alaska (-9:00)",
                     "Alaska"
                  ],
                  [
                     "Pacific Time (US & Canada) (-8:00)",
                     "Pacific Time (US & Canada)"
                  ],
                  [
                     "Tijuana (-8:00)",
                     "Tijuana"
                  ],
                  [
                     "Arizona (-7:00)",
                     "Arizona"
                  ],
                  [
                     "Chihuahua (-7:00)",
                     "Chihuahua"
                  ],
                  [
                     "Mazatlan (-7:00)",
                     "Mazatlan"
                  ],
                  [
                     "Mountain Time (US & Canada) (-7:00)",
                     "Mountain Time (US & Canada)"
                  ],
                  [
                     "Central America (-6:00)",
                     "Central America"
                  ],
                  [
                     "Central Time (US & Canada) (-6:00)",
                     "Central Time (US & Canada)"
                  ],
                  [
                     "Guadalajara (-6:00)",
                     "Guadalajara"
                  ],
                  [
                     "Mexico City (-6:00)",
                     "Mexico City"
                  ],
                  [
                     "Monterrey (-6:00)",
                     "Monterrey"
                  ],
                  [
                     "Saskatchewan (-6:00)",
                     "Saskatchewan"
                  ],
                  [
                     "Bogota (-5:00)",
                     "Bogota"
                  ],
                  [
                     "Eastern Time (US & Canada) (-5:00)",
                     "Eastern Time (US & Canada)"
                  ],
                  [
                     "Indiana (East) (-5:00)",
                     "Indiana (East)"
                  ],
                  [
                     "Lima (-5:00)",
                     "Lima"
                  ],
                  [
                     "Quito (-5:00)",
                     "Quito"
                  ],
                  [
                     "Atlantic Time (Canada) (-4:00)",
                     "Atlantic Time (Canada)"
                  ],
                  [
                     "Caracas (-4:00)",
                     "Caracas"
                  ],
                  [
                     "Georgetown (-4:00)",
                     "Georgetown"
                  ],
                  [
                     "La Paz (-4:00)",
                     "La Paz"
                  ],
                  [
                     "Santiago (-4:00)",
                     "Santiago"
                  ],
                  [
                     "Newfoundland (-4:30)",
                     "Newfoundland"
                  ],
                  [
                     "Brasilia (-3:00)",
                     "Brasilia"
                  ],
                  [
                     "Buenos Aires (-3:00)",
                     "Buenos Aires"
                  ],
                  [
                     "Greenland (-3:00)",
                     "Greenland"
                  ],
                  [
                     "Montevideo (-3:00)",
                     "Montevideo"
                  ],
                  [
                     "Mid-Atlantic (-2:00)",
                     "Mid-Atlantic"
                  ],
                  [
                     "Azores (-1:00)",
                     "Azores"
                  ],
                  [
                     "Cape Verde Is. (-1:00)",
                     "Cape Verde Is."
                  ],
                  [
                     "Casablanca (+0:00)",
                     "Casablanca"
                  ],
                  [
                     "Dublin (+0:00)",
                     "Dublin"
                  ],
                  [
                     "Edinburgh (+0:00)",
                     "Edinburgh"
                  ],
                  [
                     "Lisbon (+0:00)",
                     "Lisbon"
                  ],
                  [
                     "London (+0:00)",
                     "London"
                  ],
                  [
                     "Monrovia (+0:00)",
                     "Monrovia"
                  ],
                  [
                     "UTC (+0:00)",
                     "UTC"
                  ],
                  [
                     "Amsterdam (+1:00)",
                     "Amsterdam"
                  ],
                  [
                     "Belgrade (+1:00)",
                     "Belgrade"
                  ],
                  [
                     "Berlin (+1:00)",
                     "Berlin"
                  ],
                  [
                     "Bern (+1:00)",
                     "Bern"
                  ],
                  [
                     "Bratislava (+1:00)",
                     "Bratislava"
                  ],
                  [
                     "Brussels (+1:00)",
                     "Brussels"
                  ],
                  [
                     "Budapest (+1:00)",
                     "Budapest"
                  ],
                  [
                     "Copenhagen (+1:00)",
                     "Copenhagen"
                  ],
                  [
                     "Ljubljana (+1:00)",
                     "Ljubljana"
                  ],
                  [
                     "Madrid (+1:00)",
                     "Madrid"
                  ],
                  [
                     "Paris (+1:00)",
                     "Paris"
                  ],
                  [
                     "Prague (+1:00)",
                     "Prague"
                  ],
                  [
                     "Rome (+1:00)",
                     "Rome"
                  ],
                  [
                     "Sarajevo (+1:00)",
                     "Sarajevo"
                  ],
                  [
                     "Skopje (+1:00)",
                     "Skopje"
                  ],
                  [
                     "Stockholm (+1:00)",
                     "Stockholm"
                  ],
                  [
                     "Vienna (+1:00)",
                     "Vienna"
                  ],
                  [
                     "Warsaw (+1:00)",
                     "Warsaw"
                  ],
                  [
                     "West Central Africa (+1:00)",
                     "West Central Africa"
                  ],
                  [
                     "Zagreb (+1:00)",
                     "Zagreb"
                  ],
                  [
                     "Athens (+2:00)",
                     "Athens"
                  ],
                  [
                     "Bucharest (+2:00)",
                     "Bucharest"
                  ],
                  [
                     "Cairo (+2:00)",
                     "Cairo"
                  ],
                  [
                     "Harare (+2:00)",
                     "Harare"
                  ],
                  [
                     "Helsinki (+2:00)",
                     "Helsinki"
                  ],
                  [
                     "Jerusalem (+2:00)",
                     "Jerusalem"
                  ],
                  [
                     "Kaliningrad (+2:00)",
                     "Kaliningrad"
                  ],
                  [
                     "Kyiv (+2:00)",
                     "Kyiv"
                  ],
                  [
                     "Pretoria (+2:00)",
                     "Pretoria"
                  ],
                  [
                     "Riga (+2:00)",
                     "Riga"
                  ],
                  [
                     "Sofia (+2:00)",
                     "Sofia"
                  ],
                  [
                     "Tallinn (+2:00)",
                     "Tallinn"
                  ],
                  [
                     "Vilnius (+2:00)",
                     "Vilnius"
                  ],
                  [
                     "Baghdad (+3:00)",
                     "Baghdad"
                  ],
                  [
                     "Istanbul (+3:00)",
                     "Istanbul"
                  ],
                  [
                     "Kuwait (+3:00)",
                     "Kuwait"
                  ],
                  [
                     "Minsk (+3:00)",
                     "Minsk"
                  ],
                  [
                     "Moscow (+3:00)",
                     "Moscow"
                  ],
                  [
                     "Nairobi (+3:00)",
                     "Nairobi"
                  ],
                  [
                     "Riyadh (+3:00)",
                     "Riyadh"
                  ],
                  [
                     "St. Petersburg (+3:00)",
                     "St. Petersburg"
                  ],
                  [
                     "Tehran (+3:30)",
                     "Tehran"
                  ],
                  [
                     "Abu Dhabi (+4:00)",
                     "Abu Dhabi"
                  ],
                  [
                     "Baku (+4:00)",
                     "Baku"
                  ],
                  [
                     "Muscat (+4:00)",
                     "Muscat"
                  ],
                  [
                     "Samara (+4:00)",
                     "Samara"
                  ],
                  [
                     "Tbilisi (+4:00)",
                     "Tbilisi"
                  ],
                  [
                     "Volgograd (+4:00)",
                     "Volgograd"
                  ],
                  [
                     "Yerevan (+4:00)",
                     "Yerevan"
                  ],
                  [
                     "Kabul (+4:30)",
                     "Kabul"
                  ],
                  [
                     "Ekaterinburg (+5:00)",
                     "Ekaterinburg"
                  ],
                  [
                     "Islamabad (+5:00)",
                     "Islamabad"
                  ],
                  [
                     "Karachi (+5:00)",
                     "Karachi"
                  ],
                  [
                     "Tashkent (+5:00)",
                     "Tashkent"
                  ],
                  [
                     "Chennai (+5:30)",
                     "Chennai"
                  ],
                  [
                     "Kolkata (+5:30)",
                     "Kolkata"
                  ],
                  [
                     "Mumbai (+5:30)",
                     "Mumbai"
                  ],
                  [
                     "New Delhi (+5:30)",
                     "New Delhi"
                  ],
                  [
                     "Sri Jayawardenepura (+5:30)",
                     "Sri Jayawardenepura"
                  ],
                  [
                     "Kathmandu (+5:45)",
                     "Kathmandu"
                  ],
                  [
                     "Almaty (+6:00)",
                     "Almaty"
                  ],
                  [
                     "Astana (+6:00)",
                     "Astana"
                  ],
                  [
                     "Dhaka (+6:00)",
                     "Dhaka"
                  ],
                  [
                     "Urumqi (+6:00)",
                     "Urumqi"
                  ],
                  [
                     "Rangoon (+6:30)",
                     "Rangoon"
                  ],
                  [
                     "Bangkok (+7:00)",
                     "Bangkok"
                  ],
                  [
                     "Hanoi (+7:00)",
                     "Hanoi"
                  ],
                  [
                     "Jakarta (+7:00)",
                     "Jakarta"
                  ],
                  [
                     "Krasnoyarsk (+7:00)",
                     "Krasnoyarsk"
                  ],
                  [
                     "Novosibirsk (+7:00)",
                     "Novosibirsk"
                  ],
                  [
                     "Beijing (+8:00)",
                     "Beijing"
                  ],
                  [
                     "Chongqing (+8:00)",
                     "Chongqing"
                  ],
                  [
                     "Hong Kong (+8:00)",
                     "Hong Kong"
                  ],
                  [
                     "Irkutsk (+8:00)",
                     "Irkutsk"
                  ],
                  [
                     "Kuala Lumpur (+8:00)",
                     "Kuala Lumpur"
                  ],
                  [
                     "Perth (+8:00)",
                     "Perth"
                  ],
                  [
                     "Singapore (+8:00)",
                     "Singapore"
                  ],
                  [
                     "Taipei (+8:00)",
                     "Taipei"
                  ],
                  [
                     "Ulaanbaatar (+8:00)",
                     "Ulaanbaatar"
                  ],
                  [
                     "Osaka (+9:00)",
                     "Osaka"
                  ],
                  [
                     "Sapporo (+9:00)",
                     "Sapporo"
                  ],
                  [
                     "Seoul (+9:00)",
                     "Seoul"
                  ],
                  [
                     "Tokyo (+9:00)",
                     "Tokyo"
                  ],
                  [
                     "Yakutsk (+9:00)",
                     "Yakutsk"
                  ],
                  [
                     "Adelaide (+9:30)",
                     "Adelaide"
                  ],
                  [
                     "Darwin (+9:30)",
                     "Darwin"
                  ],
                  [
                     "Brisbane (+10:00)",
                     "Brisbane"
                  ],
                  [
                     "Canberra (+10:00)",
                     "Canberra"
                  ],
                  [
                     "Guam (+10:00)",
                     "Guam"
                  ],
                  [
                     "Hobart (+10:00)",
                     "Hobart"
                  ],
                  [
                     "Melbourne (+10:00)",
                     "Melbourne"
                  ],
                  [
                     "Port Moresby (+10:00)",
                     "Port Moresby"
                  ],
                  [
                     "Sydney (+10:00)",
                     "Sydney"
                  ],
                  [
                     "Vladivostok (+10:00)",
                     "Vladivostok"
                  ],
                  [
                     "Magadan (+11:00)",
                     "Magadan"
                  ],
                  [
                     "New Caledonia (+11:00)",
                     "New Caledonia"
                  ],
                  [
                     "Solomon Is. (+11:00)",
                     "Solomon Is."
                  ],
                  [
                     "Srednekolymsk (+11:00)",
                     "Srednekolymsk"
                  ],
                  [
                     "Auckland (+12:00)",
                     "Auckland"
                  ],
                  [
                     "Fiji (+12:00)",
                     "Fiji"
                  ],
                  [
                     "Kamchatka (+12:00)",
                     "Kamchatka"
                  ],
                  [
                     "Marshall Is. (+12:00)",
                     "Marshall Is."
                  ],
                  [
                     "Wellington (+12:00)",
                     "Wellington"
                  ],
                  [
                     "Chatham Is. (+12:45)",
                     "Chatham Is."
                  ],
                  [
                     "Nuku'alofa (+13:00)",
                     "Nuku'alofa"
                  ],
                  [
                     "Samoa (+13:00)",
                     "Samoa"
                  ],
                  [
                     "Tokelau Is. (+13:00)",
                     "Tokelau Is."
                  ]
               ]
            },
            {
               "name":"data_center",
               "type":"string",
               "optional":true,
               "label":"Data center",
               "hint":"You can find this at the end of your Zoho URL 'https://accounts.zoho.[Data center]'. Default value: 'Others(com)'",
               "pick_list":[
                  [
                     "China(cn)",
                     "com.cn"
                  ],
                  [
                     "Europe(eu)",
                     "eu"
                  ],
                  [
                     "India(in)",
                     "in"
                  ],
                  [
                     "Others(com)",
                     "com"
                  ]
               ],
               "default":"com"
            }
         ]
      }
```
:::

---
### Zoho Invoice

**Provider value:**
```json
"provider": "zoho_invoice"
```

::: details View connection parameters JSON
```json
      {
         "oauth":false,
         "personalization":false,
         "input":[
            {
               "name":"auth_token",
               "type":"string",
               "label":"Authentication token",
               "hint":"Create your Zoho invoice token <a target='_blank' rel='noopener' href=\"https://accounts.zoho.com/apiauthtoken/create?SCOPE=ZohoInvoice/invoiceapi\">here</a>"
            },
            {
               "name":"timezone",
               "type":"string",
               "optional":true,
               "label":"Account timezone",
               "hint":"Needed for consistency with Zoho - pick same as your Zoho profile",
               "pick_list":[
                  [
                     "American Samoa (-11:00)",
                     "American Samoa"
                  ],
                  [
                     "International Date Line West (-11:00)",
                     "International Date Line West"
                  ],
                  [
                     "Midway Island (-11:00)",
                     "Midway Island"
                  ],
                  [
                     "Hawaii (-10:00)",
                     "Hawaii"
                  ],
                  [
                     "Alaska (-9:00)",
                     "Alaska"
                  ],
                  [
                     "Pacific Time (US & Canada) (-8:00)",
                     "Pacific Time (US & Canada)"
                  ],
                  [
                     "Tijuana (-8:00)",
                     "Tijuana"
                  ],
                  [
                     "Arizona (-7:00)",
                     "Arizona"
                  ],
                  [
                     "Chihuahua (-7:00)",
                     "Chihuahua"
                  ],
                  [
                     "Mazatlan (-7:00)",
                     "Mazatlan"
                  ],
                  [
                     "Mountain Time (US & Canada) (-7:00)",
                     "Mountain Time (US & Canada)"
                  ],
                  [
                     "Central America (-6:00)",
                     "Central America"
                  ],
                  [
                     "Central Time (US & Canada) (-6:00)",
                     "Central Time (US & Canada)"
                  ],
                  [
                     "Guadalajara (-6:00)",
                     "Guadalajara"
                  ],
                  [
                     "Mexico City (-6:00)",
                     "Mexico City"
                  ],
                  [
                     "Monterrey (-6:00)",
                     "Monterrey"
                  ],
                  [
                     "Saskatchewan (-6:00)",
                     "Saskatchewan"
                  ],
                  [
                     "Bogota (-5:00)",
                     "Bogota"
                  ],
                  [
                     "Eastern Time (US & Canada) (-5:00)",
                     "Eastern Time (US & Canada)"
                  ],
                  [
                     "Indiana (East) (-5:00)",
                     "Indiana (East)"
                  ],
                  [
                     "Lima (-5:00)",
                     "Lima"
                  ],
                  [
                     "Quito (-5:00)",
                     "Quito"
                  ],
                  [
                     "Atlantic Time (Canada) (-4:00)",
                     "Atlantic Time (Canada)"
                  ],
                  [
                     "Caracas (-4:00)",
                     "Caracas"
                  ],
                  [
                     "Georgetown (-4:00)",
                     "Georgetown"
                  ],
                  [
                     "La Paz (-4:00)",
                     "La Paz"
                  ],
                  [
                     "Santiago (-4:00)",
                     "Santiago"
                  ],
                  [
                     "Newfoundland (-4:30)",
                     "Newfoundland"
                  ],
                  [
                     "Brasilia (-3:00)",
                     "Brasilia"
                  ],
                  [
                     "Buenos Aires (-3:00)",
                     "Buenos Aires"
                  ],
                  [
                     "Greenland (-3:00)",
                     "Greenland"
                  ],
                  [
                     "Montevideo (-3:00)",
                     "Montevideo"
                  ],
                  [
                     "Mid-Atlantic (-2:00)",
                     "Mid-Atlantic"
                  ],
                  [
                     "Azores (-1:00)",
                     "Azores"
                  ],
                  [
                     "Cape Verde Is. (-1:00)",
                     "Cape Verde Is."
                  ],
                  [
                     "Casablanca (+0:00)",
                     "Casablanca"
                  ],
                  [
                     "Dublin (+0:00)",
                     "Dublin"
                  ],
                  [
                     "Edinburgh (+0:00)",
                     "Edinburgh"
                  ],
                  [
                     "Lisbon (+0:00)",
                     "Lisbon"
                  ],
                  [
                     "London (+0:00)",
                     "London"
                  ],
                  [
                     "Monrovia (+0:00)",
                     "Monrovia"
                  ],
                  [
                     "UTC (+0:00)",
                     "UTC"
                  ],
                  [
                     "Amsterdam (+1:00)",
                     "Amsterdam"
                  ],
                  [
                     "Belgrade (+1:00)",
                     "Belgrade"
                  ],
                  [
                     "Berlin (+1:00)",
                     "Berlin"
                  ],
                  [
                     "Bern (+1:00)",
                     "Bern"
                  ],
                  [
                     "Bratislava (+1:00)",
                     "Bratislava"
                  ],
                  [
                     "Brussels (+1:00)",
                     "Brussels"
                  ],
                  [
                     "Budapest (+1:00)",
                     "Budapest"
                  ],
                  [
                     "Copenhagen (+1:00)",
                     "Copenhagen"
                  ],
                  [
                     "Ljubljana (+1:00)",
                     "Ljubljana"
                  ],
                  [
                     "Madrid (+1:00)",
                     "Madrid"
                  ],
                  [
                     "Paris (+1:00)",
                     "Paris"
                  ],
                  [
                     "Prague (+1:00)",
                     "Prague"
                  ],
                  [
                     "Rome (+1:00)",
                     "Rome"
                  ],
                  [
                     "Sarajevo (+1:00)",
                     "Sarajevo"
                  ],
                  [
                     "Skopje (+1:00)",
                     "Skopje"
                  ],
                  [
                     "Stockholm (+1:00)",
                     "Stockholm"
                  ],
                  [
                     "Vienna (+1:00)",
                     "Vienna"
                  ],
                  [
                     "Warsaw (+1:00)",
                     "Warsaw"
                  ],
                  [
                     "West Central Africa (+1:00)",
                     "West Central Africa"
                  ],
                  [
                     "Zagreb (+1:00)",
                     "Zagreb"
                  ],
                  [
                     "Athens (+2:00)",
                     "Athens"
                  ],
                  [
                     "Bucharest (+2:00)",
                     "Bucharest"
                  ],
                  [
                     "Cairo (+2:00)",
                     "Cairo"
                  ],
                  [
                     "Harare (+2:00)",
                     "Harare"
                  ],
                  [
                     "Helsinki (+2:00)",
                     "Helsinki"
                  ],
                  [
                     "Jerusalem (+2:00)",
                     "Jerusalem"
                  ],
                  [
                     "Kaliningrad (+2:00)",
                     "Kaliningrad"
                  ],
                  [
                     "Kyiv (+2:00)",
                     "Kyiv"
                  ],
                  [
                     "Pretoria (+2:00)",
                     "Pretoria"
                  ],
                  [
                     "Riga (+2:00)",
                     "Riga"
                  ],
                  [
                     "Sofia (+2:00)",
                     "Sofia"
                  ],
                  [
                     "Tallinn (+2:00)",
                     "Tallinn"
                  ],
                  [
                     "Vilnius (+2:00)",
                     "Vilnius"
                  ],
                  [
                     "Baghdad (+3:00)",
                     "Baghdad"
                  ],
                  [
                     "Istanbul (+3:00)",
                     "Istanbul"
                  ],
                  [
                     "Kuwait (+3:00)",
                     "Kuwait"
                  ],
                  [
                     "Minsk (+3:00)",
                     "Minsk"
                  ],
                  [
                     "Moscow (+3:00)",
                     "Moscow"
                  ],
                  [
                     "Nairobi (+3:00)",
                     "Nairobi"
                  ],
                  [
                     "Riyadh (+3:00)",
                     "Riyadh"
                  ],
                  [
                     "St. Petersburg (+3:00)",
                     "St. Petersburg"
                  ],
                  [
                     "Tehran (+3:30)",
                     "Tehran"
                  ],
                  [
                     "Abu Dhabi (+4:00)",
                     "Abu Dhabi"
                  ],
                  [
                     "Baku (+4:00)",
                     "Baku"
                  ],
                  [
                     "Muscat (+4:00)",
                     "Muscat"
                  ],
                  [
                     "Samara (+4:00)",
                     "Samara"
                  ],
                  [
                     "Tbilisi (+4:00)",
                     "Tbilisi"
                  ],
                  [
                     "Volgograd (+4:00)",
                     "Volgograd"
                  ],
                  [
                     "Yerevan (+4:00)",
                     "Yerevan"
                  ],
                  [
                     "Kabul (+4:30)",
                     "Kabul"
                  ],
                  [
                     "Ekaterinburg (+5:00)",
                     "Ekaterinburg"
                  ],
                  [
                     "Islamabad (+5:00)",
                     "Islamabad"
                  ],
                  [
                     "Karachi (+5:00)",
                     "Karachi"
                  ],
                  [
                     "Tashkent (+5:00)",
                     "Tashkent"
                  ],
                  [
                     "Chennai (+5:30)",
                     "Chennai"
                  ],
                  [
                     "Kolkata (+5:30)",
                     "Kolkata"
                  ],
                  [
                     "Mumbai (+5:30)",
                     "Mumbai"
                  ],
                  [
                     "New Delhi (+5:30)",
                     "New Delhi"
                  ],
                  [
                     "Sri Jayawardenepura (+5:30)",
                     "Sri Jayawardenepura"
                  ],
                  [
                     "Kathmandu (+5:45)",
                     "Kathmandu"
                  ],
                  [
                     "Almaty (+6:00)",
                     "Almaty"
                  ],
                  [
                     "Astana (+6:00)",
                     "Astana"
                  ],
                  [
                     "Dhaka (+6:00)",
                     "Dhaka"
                  ],
                  [
                     "Urumqi (+6:00)",
                     "Urumqi"
                  ],
                  [
                     "Rangoon (+6:30)",
                     "Rangoon"
                  ],
                  [
                     "Bangkok (+7:00)",
                     "Bangkok"
                  ],
                  [
                     "Hanoi (+7:00)",
                     "Hanoi"
                  ],
                  [
                     "Jakarta (+7:00)",
                     "Jakarta"
                  ],
                  [
                     "Krasnoyarsk (+7:00)",
                     "Krasnoyarsk"
                  ],
                  [
                     "Novosibirsk (+7:00)",
                     "Novosibirsk"
                  ],
                  [
                     "Beijing (+8:00)",
                     "Beijing"
                  ],
                  [
                     "Chongqing (+8:00)",
                     "Chongqing"
                  ],
                  [
                     "Hong Kong (+8:00)",
                     "Hong Kong"
                  ],
                  [
                     "Irkutsk (+8:00)",
                     "Irkutsk"
                  ],
                  [
                     "Kuala Lumpur (+8:00)",
                     "Kuala Lumpur"
                  ],
                  [
                     "Perth (+8:00)",
                     "Perth"
                  ],
                  [
                     "Singapore (+8:00)",
                     "Singapore"
                  ],
                  [
                     "Taipei (+8:00)",
                     "Taipei"
                  ],
                  [
                     "Ulaanbaatar (+8:00)",
                     "Ulaanbaatar"
                  ],
                  [
                     "Osaka (+9:00)",
                     "Osaka"
                  ],
                  [
                     "Sapporo (+9:00)",
                     "Sapporo"
                  ],
                  [
                     "Seoul (+9:00)",
                     "Seoul"
                  ],
                  [
                     "Tokyo (+9:00)",
                     "Tokyo"
                  ],
                  [
                     "Yakutsk (+9:00)",
                     "Yakutsk"
                  ],
                  [
                     "Adelaide (+9:30)",
                     "Adelaide"
                  ],
                  [
                     "Darwin (+9:30)",
                     "Darwin"
                  ],
                  [
                     "Brisbane (+10:00)",
                     "Brisbane"
                  ],
                  [
                     "Canberra (+10:00)",
                     "Canberra"
                  ],
                  [
                     "Guam (+10:00)",
                     "Guam"
                  ],
                  [
                     "Hobart (+10:00)",
                     "Hobart"
                  ],
                  [
                     "Melbourne (+10:00)",
                     "Melbourne"
                  ],
                  [
                     "Port Moresby (+10:00)",
                     "Port Moresby"
                  ],
                  [
                     "Sydney (+10:00)",
                     "Sydney"
                  ],
                  [
                     "Vladivostok (+10:00)",
                     "Vladivostok"
                  ],
                  [
                     "Magadan (+11:00)",
                     "Magadan"
                  ],
                  [
                     "New Caledonia (+11:00)",
                     "New Caledonia"
                  ],
                  [
                     "Solomon Is. (+11:00)",
                     "Solomon Is."
                  ],
                  [
                     "Srednekolymsk (+11:00)",
                     "Srednekolymsk"
                  ],
                  [
                     "Auckland (+12:00)",
                     "Auckland"
                  ],
                  [
                     "Fiji (+12:00)",
                     "Fiji"
                  ],
                  [
                     "Kamchatka (+12:00)",
                     "Kamchatka"
                  ],
                  [
                     "Marshall Is. (+12:00)",
                     "Marshall Is."
                  ],
                  [
                     "Wellington (+12:00)",
                     "Wellington"
                  ],
                  [
                     "Chatham Is. (+12:45)",
                     "Chatham Is."
                  ],
                  [
                     "Nuku'alofa (+13:00)",
                     "Nuku'alofa"
                  ],
                  [
                     "Samoa (+13:00)",
                     "Samoa"
                  ],
                  [
                     "Tokelau Is. (+13:00)",
                     "Tokelau Is."
                  ]
               ]
            },
            {
               "name":"data_center",
               "type":"string",
               "optional":true,
               "label":"Data center",
               "hint":"You can find this at the end of your Zoho URL 'https://accounts.zoho.[Data center]'. Default value: 'Others(com)'",
               "pick_list":[
                  [
                     "China(cn)",
                     "cn"
                  ],
                  [
                     "Europe(eu)",
                     "eu"
                  ],
                  [
                     "Others(com)",
                     "com"
                  ]
               ],
               "default":"com"
            }
         ]
      }
```
:::

---
### Zoom

**Provider value:**
```json
"provider": "zoom"
```

---
### ZoomInfo

**Provider value:**
```json
"provider": "zoom_info"
```

---
### Zuora

**Provider value:**
```json
"provider": "zuora"
```

::: details View connection parameters JSON
```json
      {
         "oauth":false,
         "personalization":false,
         "input":[
            {
               "name":"client_id",
               "type":"string",
               "optional":false,
               "label":"Client ID",
               "hint":"Click <a href='https://knowledgecenter.zuora.com/CF_Users_and_Administrators/A_Administrator_Settings/Manage_Users#Create_an_OAuth_Client_for_a_User' target='_blank'>here</a> for client ID"
            },
            {
               "name":"client_secret",
               "type":"string",
               "optional":false,
               "label":"Client secret",
               "hint":"Click <a href='https://knowledgecenter.zuora.com/CF_Users_and_Administrators/A_Administrator_Settings/Manage_Users#Create_an_OAuth_Client_for_a_User' target='_blank'>here</a> for client secret"
            },
            {
               "name":"environment",
               "type":"string",
               "optional":false,
               "label":"Environment",
               "hint":"Click <a href='https://jp.zuora.com/api-reference/#section/Introduction/Endpoints' target='_blank'>here</a> for environment details",
               "pick_list":[
                  [
                     "US Production",
                     "rest"
                  ],
                  [
                     "US Sandbox",
                     "rest.apisandbox"
                  ],
                  [
                     "US Performance Test",
                     "rest.pt1"
                  ],
                  [
                     "EU Production",
                     "rest.eu"
                  ],
                  [
                     "EU Sandbox",
                     "rest.sandbox.eu"
                  ]
               ]
            },
            {
               "name":"version",
               "type":"string",
               "optional":false,
               "label":"Zuora SOAP API Version",
               "hint":"WSDL Service Version for example, 91.0, Find the <a href='https://knowledgecenter.zuora.com/DC_Developers/G_SOAP_API/Zuora_SOAP_API_Version_History' target='_blank'>latest version</a>."
            }
         ]
      }
```
:::

---
### Zuora for Salesforce

**Provider value:**
```json
"provider": "zuora_forcecom"
```

::: details View connection parameters JSON
```json
      {
         "oauth":true,
         "personalization":true,
         "input":[
            {
               "name":"sandbox",
               "type":"boolean",
               "optional":true,
               "label":"Sandbox",
               "hint":"Is this connecting to a sandbox account?",
               "default":"false"
            }
         ]
      }
```
:::

<!---

<table width="100%" style="table-layout: fixed;">
  <thead>
    <tr>
        <th>Connector</th>
        <th>Provider</th>
        <th>Configuration JSON</th>
    </tr>
  </thead>
  <tbody>
    <template v-for="connector in $frontmatter.connectors">
      <tr>
        <td width="20%; fixed">
          <pre style="overflow-wrap: break-word;">
          <strong>{{ connector.name }}</strong>
        </td>
        <td width="20%; fixed">
          {{ connector.provider }}
        </td>
        <td Display="block">
          <template v-if="connector.configuration_json">
            <details><summary><b>View JSON</b></summary>
              <div class="language- extra-class">
              <pre class="language-json" style="white-space: pre-wrap; overflow-wrap: break-word;">{{ connector.configuration_json }}</pre>
              </div>
              </details>
          </template>
        </td>
      </tr>
    </template>
  </tbody>
</table>

--->
