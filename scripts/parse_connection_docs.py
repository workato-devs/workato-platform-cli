#!/usr/bin/env python3
"""
Parse connections-parameters.md and convert to JSON for CLI usage
"""

import json
import logging
import re

from pathlib import Path
from typing import Any


def parse_connection_docs(logger: logging.Logger, file_path: Path) -> dict[str, Any]:
    """Parse the markdown document and extract connection parameters"""
    with open(file_path) as f:
        content = f.read()

    # Split content into sections by ### headers
    sections = re.split(r"\n### (.+)\n", content)

    connectors = {}

    # Process each section (skip first which is intro content)
    for i in range(1, len(sections), 2):
        if i + 1 >= len(sections):
            break

        connector_name = sections[i].strip()
        section_content = sections[i + 1]

        # Extract provider value
        provider_match = re.search(r'"provider":\s*"([^"]+)"', section_content)
        if not provider_match:
            continue

        provider = provider_match.group(1)

        # Extract the full JSON configuration
        json_match = re.search(
            r"::: details View connection parameters JSON\n```json\n(.*?)\n```\n:::",
            section_content,
            re.DOTALL,
        )

        if json_match:
            try:
                # Clean up the JSON (remove extra whitespace and fix formatting)
                json_str = json_match.group(1).strip()
                # Parse the JSON to validate it and reformat
                config = json.loads(json_str)

                connectors[provider] = {
                    "name": connector_name,
                    "provider": provider,
                    "oauth": config.get("oauth", False),
                    "personalization": config.get("personalization", False),
                    "secure_tunnel": config.get("secure_tunnel", False),
                    "input": config.get("input", []),
                }

            except json.JSONDecodeError as e:
                logger.warning(
                    f"Warning: Failed to parse JSON for {connector_name}: {e}"
                )
                continue

    return connectors


def extract_parameter_info(input_params: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Extract simplified parameter information from input configuration"""
    simple_params = []

    for param in input_params:
        param_info = {
            "name": param.get("name", ""),
            "type": param.get("type", "string"),
            "optional": param.get("optional", True),
            "label": param.get("label", ""),
            "hint": param.get("hint", "").replace("\n", " ").strip(),
        }

        # Include default value if present
        if "default" in param:
            param_info["default"] = param["default"]

        # For object types, include property information
        if param.get("type") == "object" and "properties" in param:
            param_info["properties"] = []
            for prop in param["properties"]:
                prop_info = {
                    "name": prop.get("name", ""),
                    "type": prop.get("type", "string"),
                    "optional": prop.get("optional", True),
                    "label": prop.get("label", ""),
                }
                param_info["properties"].append(prop_info)

        simple_params.append(param_info)

    return simple_params


def create_simplified_data(connectors: dict[str, Any]) -> dict[str, Any]:
    """Create a simplified version for easier CLI usage"""
    simplified = {}

    for provider, config in connectors.items():
        simplified[provider] = {
            "name": config["name"],
            "provider": provider,
            "oauth": config["oauth"],
            "personalization": config["personalization"],
            "secure_tunnel": config.get("secure_tunnel", False),
            "parameters": extract_parameter_info(config["input"]),
            "parameter_count": len(config["input"]),
        }

    return simplified


def main() -> None:
    """Main function to parse and convert"""
    logger = logging.getLogger(__name__)
    input_file = Path(__file__).parent.parent / "connections-parameters.md"
    output_file = (
        Path(__file__).parent.parent
        / "workato_platform"
        / "cli"
        / "data"
        / "connection-data.json"
    )
    output_simple = (
        Path(__file__).parent.parent
        / "workato_platform"
        / "cli"
        / "data"
        / "connection-data-simple.json"
    )

    if not input_file.exists():
        logger.error(f"❌ Input file not found: {input_file}")
        return

    # Create data directory if it doesn't exist
    output_file.parent.mkdir(exist_ok=True)

    # Parse the markdown
    logger.info(f"Parsing {input_file}...")
    connectors = parse_connection_docs(logger=logger, file_path=input_file)

    if not connectors:
        logger.error("❌ No connector data found")
        return

    # Create simplified version
    simplified = create_simplified_data(connectors)

    # Write full JSON file
    logger.info(f"Writing {len(connectors)} connectors to {output_file}...")
    with open(output_file, "w") as f:
        json.dump(connectors, f, indent=2, sort_keys=True)

    # Write simplified JSON file
    logger.info(f"Writing simplified data to {output_simple}...")
    with open(output_simple, "w") as f:
        json.dump(simplified, f, indent=2, sort_keys=True)

    logger.info("✅ Done!")

    # Show some stats
    logger.info("\nStats:")
    logger.info(f"  Total connectors: {len(connectors)}")

    oauth_count = sum(1 for c in connectors.values() if c["oauth"])
    logger.info(f"  OAuth connectors: {oauth_count}")

    param_counts = [
        (provider, len(config["input"])) for provider, config in connectors.items()
    ]
    param_counts.sort(key=lambda x: x[1], reverse=True)

    logger.info("  Top 5 connectors by parameter count:")
    for provider, count in param_counts[:5]:
        name = connectors[provider]["name"]
        logger.info(f"    {name} ({provider}): {count} parameters")


if __name__ == "__main__":
    main()
