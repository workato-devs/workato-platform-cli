import re

import asyncclick as click

from dependency_injector.wiring import Provide, inject

from workato_platform import Workato
from workato_platform.cli.containers import Container
from workato_platform.cli.utils.exception_handler import handle_api_exceptions
from workato_platform.cli.utils.spinner import Spinner
from workato_platform.client.workato_api.models.api_client import ApiClient
from workato_platform.client.workato_api.models.api_client_create_request import (
    ApiClientCreateRequest,
)
from workato_platform.client.workato_api.models.api_key import ApiKey
from workato_platform.client.workato_api.models.api_key_create_request import (
    ApiKeyCreateRequest,
)


@click.group(name="api-clients")
def api_clients() -> None:
    """Manage API clients"""
    pass


@api_clients.command()
@click.option("--name", required=True, help="Name of the client")
@click.option("--description", help="Description of the client")
@click.option(
    "--project-id", type=int, help="ID of the project to create the client in"
)
@click.option(
    "--api-portal-id", type=int, help="ID of the API portal to assign the client"
)
@click.option(
    "--email", help="Email address for the client (required if api-portal-id provided)"
)
@click.option(
    "--api-collection-ids",
    required=True,
    help="Comma-separated list of API collection IDs to assign",
)
@click.option("--api-policy-id", type=int, help="ID of the API policy to apply")
@click.option(
    "--auth-type",
    required=True,
    type=click.Choice(["token", "jwt", "oauth2", "oidc"]),
    help="Authentication method (token, jwt, oauth2, oidc)",
)
@click.option(
    "--jwt-method",
    type=click.Choice(["hmac", "rsa"]),
    help="JWT signing method (hmac or rsa) - required when auth-type is jwt",
)
@click.option(
    "--jwt-secret",
    help="HMAC shared secret or RSA public key - required when auth-type is jwt",
)
@click.option("--oidc-issuer", help="Discovery URL for OIDC identity provider")
@click.option("--oidc-jwks-uri", help="JWKS URL for OIDC identity provider")
@click.option(
    "--access-profile-claim", help="JWT claim key for access profile identification"
)
@click.option("--required-claims", help="Comma-separated list of claims to enforce")
@click.option("--allowed-issuers", help="Comma-separated list of allowed issuers")
@click.option("--mtls-enabled", is_flag=True, help="Enable mutual TLS for this client")
@click.option("--validation-formula", help="Formula to validate client certificates")
@click.option(
    "--cert-bundle-ids", help="Comma-separated list of certificate bundle IDs for mTLS"
)
@inject
@handle_api_exceptions
async def create(
    name: str,
    auth_type: str,
    description: str | None = None,
    project_id: int | None = None,
    api_portal_id: int | None = None,
    email: str | None = None,
    api_collection_ids: str | None = None,
    api_policy_id: int | None = None,
    jwt_method: str | None = None,
    jwt_secret: str | None = None,
    oidc_issuer: str | None = None,
    oidc_jwks_uri: str | None = None,
    access_profile_claim: str | None = None,
    required_claims: str | None = None,
    allowed_issuers: str | None = None,
    mtls_enabled: bool | None = None,
    validation_formula: str | None = None,
    cert_bundle_ids: str | None = None,
    workato_api_client: Workato = Provide[Container.workato_api_client],
) -> None:
    """Create a new API client"""

    # Validate conditional parameters
    validation_errors = validate_create_parameters(
        auth_type,
        jwt_method,
        jwt_secret,
        oidc_issuer,
        oidc_jwks_uri,
        api_portal_id,
        email,
    )

    if validation_errors:
        click.echo("❌ Parameter validation failed:")
        for error in validation_errors:
            click.echo(f"  • {error}")
        return

    # Parse comma-separated lists
    try:
        collection_ids = (
            [int(id.strip()) for id in api_collection_ids.split(",")]
            if api_collection_ids
            else []
        )
    except ValueError:
        click.echo(
            "❌ Invalid API collection IDs. Please provide comma-separated integers."
        )
        return

    api_client_create_request = ApiClientCreateRequest(
        name=name,
        description=description,
        project_id=project_id,
        api_portal_id=api_portal_id,
        email=email,
        api_policy_id=api_policy_id,
        api_collection_ids=collection_ids,
        auth_type=auth_type,
        jwt_method=jwt_method,
        jwt_secret=jwt_secret,
        oidc_issuer=oidc_issuer,
        oidc_jwks_uri=oidc_jwks_uri,
        access_profile_claim=access_profile_claim,
        required_claims=[claim.strip() for claim in required_claims.split(",")]
        if required_claims
        else None,
        allowed_issuers=[issuer.strip() for issuer in allowed_issuers.split(",")]
        if allowed_issuers
        else None,
        mtls_enabled=mtls_enabled,
        validation_formula=validation_formula,
        cert_bundle_ids=[int(id.strip()) for id in cert_bundle_ids.split(",")]
        if cert_bundle_ids
        else None,
    )

    # Create the API client
    spinner = Spinner(f"Creating API client '{name}'")
    spinner.start()

    try:
        response = await workato_api_client.api_platform_api.create_api_client(
            api_client_create_request=api_client_create_request
        )
    finally:
        elapsed = spinner.stop()

    click.echo(f"✅ API client created successfully ({elapsed:.1f}s)")

    # Display client details
    client_data = response.data
    if client_data:
        click.echo(f"  📄 Name: {client_data.name}")
        click.echo(f"  🆔 ID: {client_data.id}")
        click.echo(f"  🔐 Auth Type: {client_data.auth_type}")

        # Show API token if it's token-based auth
        if client_data.auth_type == "token" and client_data.api_token:
            click.echo(f"  🔑 API Token: {client_data.api_token}")

        # Show assigned collections
        if client_data.api_collections:
            collection_names = [
                col.name or f"ID: {col.id}" for col in client_data.api_collections
            ]
            click.echo(f"  📚 Collections: {', '.join(collection_names)}")

    click.echo()
    click.echo("💡 Next steps:")
    click.echo("  • Configure your application to use the API client")
    if client_data.auth_type == "token":
        click.echo("  • Save the API token securely")
    click.echo("  • Test API access with the assigned collections")


def validate_create_parameters(
    auth_type: str | None = None,
    jwt_method: str | None = None,
    jwt_secret: str | None = None,
    oidc_issuer: str | None = None,
    oidc_jwks_uri: str | None = None,
    api_portal_id: int | None = None,
    email: str | None = None,
) -> list[str]:
    """Validate conditional parameters based on auth_type and other conditions"""
    errors = []

    # JWT validation
    if auth_type == "jwt":
        if not jwt_method:
            errors.append("--jwt-method is required when --auth-type is 'jwt'")
        if not jwt_secret:
            errors.append("--jwt-secret is required when --auth-type is 'jwt'")

    # OIDC validation
    if auth_type in ["jwt", "oidc"] and not oidc_issuer and not oidc_jwks_uri:
        errors.append(
            f"Either --oidc-issuer or --oidc-jwks-uri is required when "
            f"--auth-type is '{auth_type}'"
        )

    # API portal validation
    if api_portal_id and not email:
        errors.append("--email is required when --api-portal-id is provided")
    if email and not api_portal_id:
        errors.append("--api-portal-id is required when --email is provided")

    return errors


@api_clients.command(name="create-key")
@click.option(
    "--api-client-id",
    required=True,
    type=int,
    help="ID of the API client to create key for",
)
@click.option("--name", required=True, help="Name of the API key")
@click.option(
    "--active/--inactive",
    default=True,
    help="Whether the API key is enabled (default: active)",
)
@click.option(
    "--ip-allow-list", help="Comma-separated list of IP addresses to allowlist"
)
@click.option("--ip-deny-list", help="Comma-separated list of IP addresses to deny")
@inject
@handle_api_exceptions
async def create_key(
    api_client_id: int,
    name: str,
    active: bool = True,
    ip_allow_list: str | None = None,
    ip_deny_list: str | None = None,
    workato_api_client: Workato = Provide[Container.workato_api_client],
) -> None:
    """Create a new API key for an existing API client"""

    # Validate IP address lists if provided
    parsed_allow_list: list[str] | None = None
    parsed_deny_list: list[str] | None = None

    if ip_allow_list:
        parsed_allow_list = parse_ip_list(ip_allow_list, "allow")
        if parsed_allow_list is None:
            return

    if ip_deny_list:
        parsed_deny_list = parse_ip_list(ip_deny_list, "deny")
        if parsed_deny_list is None:
            return

    spinner = Spinner(f"Creating API key '{name}' for client {api_client_id}")
    spinner.start()

    try:
        response = await workato_api_client.api_platform_api.create_api_key(
            api_client_id=api_client_id,
            api_key_create_request=ApiKeyCreateRequest(
                name=name,
                active=active,
                ip_allow_list=parsed_allow_list,
                ip_deny_list=parsed_deny_list,
            ),
        )
    finally:
        elapsed = spinner.stop()

    click.echo(f"✅ API key created successfully ({elapsed:.1f}s)")
    click.echo(f"  📄 Name: {response.data.name}")
    click.echo(f"  🆔 Key ID: {response.data.id}")

    # Try different possible field names for the API key
    api_key_value = response.data.auth_token

    if api_key_value:
        click.echo(f"  🔑 API Key: {api_key_value}")
    else:
        click.echo("  🔑 API Key: Not provided in response")

    click.echo(f"  ✅ Status: {'Active' if response.data.active else 'Inactive'}")

    # Show IP restrictions if configured
    if response.data.ip_allow_list:
        allow_list = ", ".join(response.data.ip_allow_list)
        click.echo(f"  🟢 IP Allow List: {allow_list}")

    if response.data.ip_deny_list:
        deny_list = ", ".join(response.data.ip_deny_list)
        click.echo(f"  🔴 IP Deny List: {deny_list}")

    click.echo()
    click.echo("💡 Next steps:")
    click.echo("  • Save the API key securely")
    click.echo("  • Configure your application to use this key")
    click.echo("  • Test API access from allowed IP addresses")

    if response.data.ip_allow_list or response.data.ip_deny_list:
        click.echo("  • Verify IP restrictions are working as expected")


def parse_ip_list(ip_list_str: str, list_type: str) -> list[str] | None:
    """Parse and validate IP address list"""
    ip_addresses = [ip.strip() for ip in ip_list_str.split(",")]

    # Basic IP address validation
    for ip in ip_addresses:
        if not ip:
            continue

        # Simple validation - could be enhanced with proper IP validation
        if not validate_ip_address(ip):
            click.echo(f"❌ Invalid IP address in {list_type} list: {ip}")
            click.echo(
                "💡 Please provide valid IP addresses (IPv4 or IPv6) or CIDR blocks"
            )
            return None

    return [ip for ip in ip_addresses if ip]


def validate_ip_address(ip: str) -> bool:
    """Basic IP address validation"""
    # IPv4 pattern (including CIDR)
    ipv4_pattern = r"^(\d{1,3}\.){3}\d{1,3}(\/\d{1,2})?$"

    # IPv6 pattern (basic - could be more comprehensive)
    ipv6_pattern = r"^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^::1$|^::$"

    # Check if it matches IPv4 or IPv6 patterns
    if re.match(ipv4_pattern, ip):
        # Validate IPv4 octets
        parts = ip.split("/")
        octets = parts[0].split(".")
        for octet in octets:
            if not (0 <= int(octet) <= 255):
                return False

        # Validate CIDR if present
        if len(parts) == 2:
            cidr = int(parts[1])
            if not (0 <= cidr <= 32):
                return False

        return True

    elif re.match(ipv6_pattern, ip):
        return True

    return False


@api_clients.command(name="refresh-secret")
@click.option("--api-client-id", required=True, type=int, help="ID of the API client")
@click.option(
    "--api-key-id", required=True, type=int, help="ID of the API key to refresh"
)
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
@handle_api_exceptions
async def refresh_secret(
    api_client_id: int,
    api_key_id: int,
    force: bool | None = None,
) -> None:
    """Refresh the secret for an existing API key"""

    # Show warning and confirmation unless --force is used
    if force is False:
        click.echo("⚠️  Warning: Refreshing the API key secret will:")
        click.echo("  • Generate a new API key")
        click.echo("  • Invalidate the current API key immediately")
        click.echo("  • Require updating all applications using this key")
        click.echo()

        if not click.confirm("Do you want to continue?"):
            click.echo("Cancelled")
            return

    # Refresh the API key secret
    await refresh_api_key_secret(api_client_id, api_key_id)


@inject
async def refresh_api_key_secret(
    api_client_id: int,
    api_key_id: int,
    workato_api_client: Workato = Provide[Container.workato_api_client],
) -> None:
    """Refresh the API key secret using the Workato API"""
    spinner = Spinner(f"Refreshing secret for API key {api_key_id}")
    spinner.start()

    try:
        response = await workato_api_client.api_platform_api.refresh_api_key_secret(
            api_client_id=api_client_id,
            api_key_id=api_key_id,
        )
    finally:
        elapsed = spinner.stop()

    click.echo(f"✅ API key secret refreshed successfully ({elapsed:.1f}s)")

    # Display updated key details - check for 'data' field first (new format)
    key_data = response.data
    click.echo(f"  📄 Name: {key_data.name}")
    click.echo(f"  🆔 Key ID: {key_data.id}")
    click.echo(f"  🔐 Auth Type: {key_data.auth_type}")

    # Get the new API key/token
    api_key_value = key_data.auth_token
    click.echo(f"  🔑 New API Key: {api_key_value}")
    click.echo(f"  ✅ Status: {'Active' if key_data.active else 'Inactive'}")

    # Show activation time if available
    if key_data.active_since:
        click.echo(f"  🕐 Active Since: {key_data.active_since.isoformat()}")

    # Show IP restrictions if configured
    if key_data.ip_allow_list:
        allow_list = ", ".join(key_data.ip_allow_list)
        click.echo(f"  🟢 IP Allow List: {allow_list}")

    if key_data.ip_deny_list:
        deny_list = ", ".join(key_data.ip_deny_list)
        click.echo(f"  🔴 IP Deny List: {deny_list}")

    click.echo()
    click.echo("🚨 Important:")
    click.echo("  • The old API key is now invalid")
    click.echo("  • Update all applications with the new API key")
    click.echo("  • Test connectivity with the new key")
    click.echo("  • Store the new key securely")


@api_clients.command(name="list")
@click.option("--project-id", type=int, help="Filter API clients by project ID")
@inject
@handle_api_exceptions
async def list_api_clients(
    project_id: int | None = None,
    workato_api_client: Workato = Provide[Container.workato_api_client],
) -> None:
    """List API clients, optionally filtered by project"""
    filter_text = f" for project {project_id}" if project_id else ""
    spinner = Spinner(f"Fetching API clients{filter_text}")
    spinner.start()

    try:
        response = await workato_api_client.api_platform_api.list_api_clients(
            project_id=project_id,
        )
    finally:
        elapsed = spinner.stop()

    clients = response.data

    if project_id:
        click.echo(
            f"📋 API Clients for Project {project_id} ({len(clients)} found) "
            f"- ({elapsed:.1f}s)"
        )
    else:
        click.echo(f"📋 All API Clients ({len(clients)} found) - ({elapsed:.1f}s)")

    if not clients:
        click.echo("  ℹ️  No API clients found")
        if project_id:
            click.echo("  💡 Try without --project-id to see all clients")
        return

    click.echo()

    # Display clients
    for client in clients:
        display_client_summary(client)
        click.echo()

    click.echo("💡 Commands:")
    click.echo(
        "  • Create API key: workato api-clients create-key --api-client-id <ID>"
    )
    click.echo(
        "  • List client keys: workato api-clients list-keys --api-client-id <ID>"
    )


@api_clients.command(name="list-keys")
@click.option(
    "--api-client-id",
    required=True,
    type=int,
    help="ID of the API client to list keys for",
)
@inject
@handle_api_exceptions
async def list_api_keys(
    api_client_id: int,
    workato_api_client: Workato = Provide[Container.workato_api_client],
) -> None:
    """List API keys for a specific API client"""

    spinner = Spinner(f"Fetching API keys for client {api_client_id}")
    spinner.start()

    try:
        response = await workato_api_client.api_platform_api.list_api_keys(
            api_client_id=api_client_id,
        )
    finally:
        elapsed = spinner.stop()

    # Parse the response
    keys = response.data

    click.echo(
        f"🔑 API Keys for Client {api_client_id} ({len(keys)} found) - ({elapsed:.1f}s)"
    )

    if not keys:
        click.echo("  ℹ️  No API keys found for this client")
        click.echo(
            "  💡 Create one: workato api-clients create-key "
            "--api-client-id {api_client_id}"
        )
        return

    click.echo()

    # Display keys
    for key in keys:
        display_key_summary(key)
        click.echo()

    click.echo("💡 Commands:")
    click.echo(
        f"  • Create new key: workato api-clients create-key "
        f"--api-client-id {api_client_id}"
    )
    click.echo(
        f"  • Refresh key: workato api-clients refresh-secret "
        f"--api-client-id {api_client_id} --api-key-id <KEY_ID>"
    )


def display_client_summary(client: ApiClient) -> None:
    """Display a summary of an API client"""

    click.echo(f"  {client.name}")
    click.echo(f"    🆔 ID: {client.id}")
    click.echo(f"    🔐 Auth Type: {client.auth_type}")

    # Show API collections if available
    for collection in client.api_collections:
        click.echo(f"    📚 {collection.name} (ID: {collection.id})")

    # Show email if available (API portal integration)
    if client.email:
        click.echo(f"    📧 Email: {client.email}")

    click.echo(f"    🕐 Created: {client.created_at.isoformat()[:10]}")


def display_key_summary(key: ApiKey) -> None:
    """Display a summary of an API key"""
    name = key.name
    key_id = key.id
    active = key.active

    status_icon = "✅" if active else "❌"
    status_text = "Active" if active else "Inactive"

    click.echo(f"  {status_icon} {name}")
    click.echo(f"    🆔 Key ID: {key_id}")
    click.echo(f"    📊 Status: {status_text}")

    # Show partial API key if available (first 8 + last 4 characters)
    api_key = key.auth_token
    if api_key:
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        click.echo(f"    🔑 Key: {masked_key}")

    # Show IP restrictions if configured
    if key.ip_allow_list:
        allow_count = len(key.ip_allow_list)
        if allow_count <= 2:
            allow_list = ", ".join(key.ip_allow_list)
            click.echo(f"    🟢 Allow List: {allow_list}")
        else:
            click.echo(f"    🟢 Allow List: {allow_count} IP addresses")

    if key.ip_deny_list:
        deny_count = len(key.ip_deny_list)
        if deny_count <= 2:
            deny_list = ", ".join(key.ip_deny_list)
            click.echo(f"    🔴 Deny List: {deny_list}")
        else:
            click.echo(f"    🔴 Deny List: {deny_count} IP addresses")

    click.echo(
        f"    🕐 Created: {key.active_since.isoformat()[:10]}"
    )  # Just the date part
