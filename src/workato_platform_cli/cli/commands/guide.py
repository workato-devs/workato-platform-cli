import json
import re

from pathlib import Path
from typing import Any

import asyncclick as click


@click.group()
async def guide() -> None:
    """AI agent documentation interface"""
    pass


@guide.command()
async def topics() -> None:
    """List all available documentation topics"""
    docs_dir = Path(__file__).parent.parent / "resources" / "docs"

    if not docs_dir.exists():
        click.echo("ERROR: Documentation not found")
        return

    # Core topics
    core_topics = [
        "recipe-fundamentals",
        "block-structure",
        "triggers",
        "actions",
        "data-mapping",
        "formulas",
        "naming-conventions",
        "recipe-deployment-workflow",
    ]

    # Formula topics
    formula_topics = [
        "string-formulas",
        "number-formulas",
        "date-formulas",
        "array-list-formulas",
        "conditions",
        "other-formulas",
    ]

    # Output as structured data for AI parsing
    result = {
        "core_topics": core_topics,
        "formula_topics": formula_topics,
        "total_topics": len(core_topics) + len(formula_topics),
    }

    click.echo(json.dumps(result, indent=2))


@guide.command()
@click.argument("topic")
async def content(topic: str) -> None:
    """Get full content of a specific topic"""
    docs_dir = Path(__file__).parent.parent / "resources" / "docs"

    if not docs_dir.exists():
        click.echo("ERROR: Documentation not found")
        return

    # Try to find the topic file
    topic_file = None

    # Check core topics first (with and without numbers)
    topic_file = None

    # Try exact match first
    core_file = docs_dir / f"{topic}.md"
    if core_file.exists():
        topic_file = core_file
    else:
        # Try with number prefixes
        for file_path in docs_dir.glob("*.md"):
            if file_path.stem.endswith(f"-{topic}"):
                topic_file = file_path
                break

    # If still not found, check formulas
    if not topic_file:
        formula_file = docs_dir / "formulas" / f"{topic}.md"
        if formula_file.exists():
            topic_file = formula_file

    if not topic_file:
        click.echo(f"ERROR: Topic '{topic}' not found")
        return

    content = topic_file.read_text(encoding="utf-8")

    # Clean up content for AI consumption
    lines = content.split("\n")
    cleaned_lines: list[str] = []

    for line in lines:
        # Skip frontmatter
        if line.startswith("---"):
            continue
        # Skip empty lines at start
        if not cleaned_lines and not line.strip():
            continue
        cleaned_lines.append(line)

    # Output clean content
    click.echo("".join(cleaned_lines))


@guide.command()
@click.argument("query")
@click.option("--topic", help="Limit to specific topic")
@click.option("--max-results", default=10, help="Maximum results to return")
async def search(query: str, topic: str | None, max_results: int) -> None:
    """Search documentation content"""
    docs_dir = Path(__file__).parent.parent / "resources" / "docs"

    if not docs_dir.exists():
        click.echo("ERROR: Documentation not found")
        return

    results = []

    def search_file(file_path: Path, search_query: str) -> list[dict]:
        """Search single file and return structured results"""
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        matches = []

        for i, line in enumerate(lines):
            if search_query.lower() in line.lower():
                # Get context (2 lines before, 2 lines after)
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                context = lines[start:end]

                matches.append(
                    {
                        "file": str(file_path.relative_to(docs_dir)),
                        "line": i + 1,
                        "match": line.strip(),
                        "context": context,
                    }
                )

        return matches

    # Search core topics
    if not topic or topic in ["core", "concepts"]:
        for file_path in docs_dir.glob("*.md"):
            matches = search_file(file_path, query)
            results.extend(matches)

    # Search specific topic
    elif topic and topic != "formulas":
        topic_file = docs_dir / f"{topic}.md"
        if topic_file.exists():
            matches = search_file(topic_file, query)
            results.extend(matches)

    # Search formulas
    if not topic or topic in ["formulas", "formula"]:
        formulas_dir = docs_dir / "formulas"
        if formulas_dir.exists():
            for file_path in formulas_dir.glob("*.md"):
                matches = search_file(file_path, query)
                results.extend(matches)

    # Limit results
    results = results[:max_results]

    # Output structured results for AI parsing
    output = {"query": query, "results_count": len(results), "results": results}

    click.echo(json.dumps(output, indent=2))


@guide.command()
@click.argument("topic")
async def structure(topic: str) -> None:
    """Show structure and relationships for a topic"""
    docs_dir = Path(__file__).parent.parent / "resources" / "docs"

    if not docs_dir.exists():
        click.echo("ERROR: Documentation not found")
        return

    # Find the topic file
    topic_file: Path | None = None
    if (docs_dir / f"{topic}.md").exists():
        topic_file = docs_dir / f"{topic}.md"
    elif (docs_dir / "formulas" / f"{topic}.md").exists():
        topic_file = docs_dir / "formulas" / f"{topic}.md"

    if not topic_file:
        click.echo(f"ERROR: Topic '{topic}' not found")
        return

    content = topic_file.read_text(encoding="utf-8")

    # Extract structure information
    structure_info: dict[str, Any] = {
        "topic": topic,
        "file": str(topic_file.relative_to(docs_dir)),
        "sections": [],
        "links": [],
        "code_blocks": 0,
    }

    lines = content.split("\n")
    current_section: str | None = None

    for line in lines:
        # Track sections
        if line.startswith("## "):
            current_section = line[3:].strip()
            structure_info["sections"].append(current_section)
        elif line.startswith("### "):
            if current_section:
                structure_info["sections"].append(f"  {line[4:].strip()}")

        # Track links
        links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", line)
        for link_text, link_path in links:
            structure_info["links"].append({"text": link_text, "path": link_path})

        # Track code blocks
        if line.startswith("```"):
            structure_info["code_blocks"] += 1

    click.echo(json.dumps(structure_info, indent=2))


@guide.command()
async def index() -> None:
    """Generate full documentation index for AI consumption"""
    docs_dir = Path(__file__).parent.parent / "resources" / "docs"

    if not docs_dir.exists():
        click.echo("ERROR: Documentation not found")
        return

    index_data: dict[str, Any] = {
        "documentation_index": {},
        "formula_index": {},
        "cross_references": {},
    }

    # Index core topics
    for file_path in docs_dir.glob("*.md"):
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        # Extract title
        title = ""
        for line in lines:
            if line.startswith("# "):
                title = line[2:].strip()
                break

        # Extract key sections
        sections = []
        for line in lines:
            if line.startswith("## "):
                sections.append(line[3:].strip())

        # Extract links
        links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)

        index_data["documentation_index"][file_path.stem] = {
            "title": title,
            "sections": sections,
            "links": links,
            "file": str(file_path.relative_to(docs_dir)),
        }

    # Index formulas
    formulas_dir = docs_dir / "formulas"
    if formulas_dir.exists():
        for file_path in formulas_dir.glob("*.md"):
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            # Extract title
            title = ""
            for line in lines:
                if line.startswith("# "):
                    title = line[2:].strip()
                    break

            # Extract formula examples
            examples = []
            in_code_block = False
            current_example: list[str] = []

            for line in lines:
                if line.startswith("```"):
                    in_code_block = not in_code_block
                    if not in_code_block and current_example:
                        examples.append("\n".join(current_example))
                        current_example = []
                elif in_code_block:
                    current_example.append(line)

            index_data["formula_index"][file_path.stem] = {
                "title": title,
                "examples": examples,
                "file": str(file_path.relative_to(docs_dir)),
            }

    # Output complete index
    click.echo(json.dumps(index_data, indent=2))
