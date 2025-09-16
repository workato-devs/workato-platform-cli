#!/usr/bin/env python3
"""
Parse picklist-parameters.md and convert to JSON for CLI usage
"""

import json
import logging

from pathlib import Path
from typing import Any


def parse_markdown_table(file_path: Path) -> list[dict[str, Any]]:
    """Parse the markdown table and extract picklist data"""
    with open(file_path) as f:
        content = f.read()

    # Find the table section
    lines = content.split("\n")
    table_start = None
    table_data = []

    for i, line in enumerate(lines):
        # Look for the table header
        if "| Adapter" in line and "Picklist name" in line and "Parameters" in line:
            table_start = i + 2  # Skip header and separator line
            break

    if table_start is None:
        raise ValueError("Could not find picklist table in markdown")

    # Parse table rows
    for line in lines[table_start:]:
        line = line.strip()
        if not line or not line.startswith("|"):
            continue

        # Split by | and clean up
        parts = [
            part.strip() for part in line.split("|")[1:-1]
        ]  # Remove empty first/last

        if len(parts) == 3:
            adapter, picklist_name, parameters = parts

            # Parse parameters - split by comma if multiple
            param_list = []
            if parameters and parameters.strip():
                param_list = [p.strip() for p in parameters.split(",")]

            table_data.append(
                {
                    "adapter": adapter,
                    "picklist_name": picklist_name,
                    "parameters": param_list,
                }
            )

    return table_data


def group_by_adapter(data: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group picklists by adapter"""
    grouped: dict[str, list[dict[str, Any]]] = {}

    for item in data:
        adapter = item["adapter"]
        if adapter not in grouped:
            grouped[adapter] = []

        grouped[adapter].append(
            {"name": item["picklist_name"], "parameters": item["parameters"]}
        )

    return grouped


def main() -> None:
    """Main function to parse and convert"""
    logger = logging.getLogger(__name__)
    input_file = Path(__file__).parent.parent / "picklist-parameters.md"
    output_file = (
        Path(__file__).parent.parent / "workato.cli" / "data" / "picklist-data.json"
    )

    # Create data directory if it doesn't exist
    output_file.parent.mkdir(exist_ok=True)

    # Parse the markdown
    logger.info(f"Parsing {input_file}...")
    table_data = parse_markdown_table(input_file)

    # Group by adapter
    grouped_data = group_by_adapter(table_data)

    # Write JSON file
    logger.info(
        f"Writing {len(table_data)} picklist entries for {len(grouped_data)} "
        "adapters to {output_file}..."
    )
    with open(output_file, "w") as f:
        json.dump(grouped_data, f, indent=2, sort_keys=True)

    logger.info("✅ Done!")

    # Show some stats
    logger.info("\nStats:")
    logger.info(f"  Total adapters: {len(grouped_data)}")
    logger.info(f"  Total picklists: {len(table_data)}")
    logger.info("  Top 5 adapters by picklist count:")

    adapter_counts = [
        (adapter, len(picklists)) for adapter, picklists in grouped_data.items()
    ]
    adapter_counts.sort(key=lambda x: x[1], reverse=True)

    for adapter, count in adapter_counts[:5]:
        logger.info(f"    {adapter}: {count} picklists")


if __name__ == "__main__":
    main()
