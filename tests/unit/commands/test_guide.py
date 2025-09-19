"""Tests for the guide command group."""

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from workato_platform.cli.commands import guide


@pytest.fixture
def docs_setup(tmp_path, monkeypatch):
    module_file = tmp_path / "fake" / "guide.py"
    module_file.parent.mkdir(parents=True)
    module_file.write_text("# dummy")
    docs_dir = tmp_path / "resources" / "docs"
    (docs_dir / "formulas").mkdir(parents=True)
    monkeypatch.setattr(guide, "__file__", str(module_file))
    return docs_dir


@pytest.mark.asyncio
async def test_topics_lists_available_docs(docs_setup, monkeypatch):
    captured: list[str] = []
    monkeypatch.setattr(guide.click, "echo", lambda msg="": captured.append(msg))

    await guide.topics.callback()

    payload = json.loads("".join(captured))
    assert payload["total_topics"] == len(payload["core_topics"]) + len(
        payload["formula_topics"]
    )


@pytest.mark.asyncio
async def test_topics_missing_docs(tmp_path, monkeypatch):
    module_file = tmp_path / "fake" / "guide.py"
    module_file.parent.mkdir(parents=True)
    module_file.write_text("# dummy")
    monkeypatch.setattr(guide, "__file__", str(module_file))

    captured: list[str] = []
    monkeypatch.setattr(guide.click, "echo", lambda msg="": captured.append(msg))

    await guide.topics.callback()

    assert "Documentation not found" in "".join(captured)


@pytest.mark.asyncio
async def test_content_returns_topic(docs_setup, monkeypatch):
    topic_file = docs_setup / "sample.md"
    topic_file.write_text("---\nmetadata\n---\nActual content\nNext line")

    captured: list[str] = []
    monkeypatch.setattr(guide.click, "echo", lambda msg="": captured.append(msg))

    await guide.content.callback("sample")

    output = "".join(captured)
    assert "Actual content" in output
    assert "metadata" in output


@pytest.mark.asyncio
async def test_content_missing_topic(docs_setup, monkeypatch):
    captured: list[str] = []
    monkeypatch.setattr(guide.click, "echo", lambda msg="": captured.append(msg))

    await guide.content.callback("missing")

    assert "Topic 'missing' not found" in "".join(captured)


@pytest.mark.asyncio
async def test_search_returns_matches(docs_setup, monkeypatch):
    (docs_setup / "guide.md").write_text("This line mentions Trigger\nSecond line")
    (docs_setup / "formulas" / "calc.md").write_text("Formula trigger usage")

    captured: list[str] = []
    monkeypatch.setattr(guide.click, "echo", lambda msg="": captured.append(msg))

    await guide.search.callback("trigger", topic=None, max_results=5)

    payload = json.loads("".join(captured))
    assert payload["results_count"] > 0
    assert payload["query"] == "trigger"


@pytest.mark.asyncio
async def test_structure_outputs_relationships(docs_setup, monkeypatch):
    (docs_setup / "overview.md").write_text(
        "# Overview\n## Section One\n### Details\nLink to [docs](other.md)\n````code````"
    )

    captured: list[str] = []
    monkeypatch.setattr(guide.click, "echo", lambda msg="": captured.append(msg))

    await guide.structure.callback("overview")

    payload = json.loads("".join(captured))
    assert payload["topic"] == "overview"
    assert "Section One" in payload["sections"][0]
    assert payload["code_blocks"] >= 1
    assert payload["links"]


@pytest.mark.asyncio
async def test_structure_missing_topic(docs_setup, monkeypatch):
    captured: list[str] = []
    monkeypatch.setattr(guide.click, "echo", lambda msg="": captured.append(msg))

    await guide.structure.callback("missing")

    assert "Topic 'missing' not found" in "".join(captured)


@pytest.mark.asyncio
async def test_index_builds_summary(docs_setup, monkeypatch):
    (docs_setup / "core.md").write_text("# Core\n## Section")
    formulas_dir = docs_setup / "formulas"
    (formulas_dir / "calc.md").write_text("# Formula\n```\nSUM(1,2)\n```\n")

    captured: list[str] = []
    monkeypatch.setattr(guide.click, "echo", lambda msg="": captured.append(msg))

    await guide.index.callback()

    payload = json.loads("".join(captured))
    assert "core" in payload["documentation_index"]
    assert "calc" in payload["formula_index"]


@pytest.mark.asyncio
async def test_guide_group_invocation(monkeypatch):
    captured: list[str] = []
    monkeypatch.setattr(guide.click, "echo", lambda msg="": captured.append(msg))

    await guide.guide.callback()

    assert captured == []


@pytest.mark.asyncio
async def test_content_missing_docs(tmp_path, monkeypatch):
    """Test content command when docs directory doesn't exist."""
    module_file = tmp_path / "fake" / "guide.py"
    module_file.parent.mkdir(parents=True)
    module_file.write_text("# dummy")
    monkeypatch.setattr(guide, "__file__", str(module_file))

    captured: list[str] = []
    monkeypatch.setattr(guide.click, "echo", lambda msg="": captured.append(msg))

    await guide.content.callback("sample")

    assert "Documentation not found" in "".join(captured)


@pytest.mark.asyncio
async def test_content_finds_numbered_topic(docs_setup, monkeypatch):
    """Test content command finding topic with number prefix."""
    topic_file = docs_setup / "01-recipe-fundamentals.md"
    topic_file.write_text("Recipe fundamentals content")

    captured: list[str] = []
    monkeypatch.setattr(guide.click, "echo", lambda msg="": captured.append(msg))

    await guide.content.callback("recipe-fundamentals")

    output = "".join(captured)
    assert "Recipe fundamentals content" in output


@pytest.mark.asyncio
async def test_content_finds_formula_topic(docs_setup, monkeypatch):
    """Test content command finding topic in formulas directory."""
    formula_file = docs_setup / "formulas" / "string-formulas.md"
    formula_file.write_text("String formula content")

    captured: list[str] = []
    monkeypatch.setattr(guide.click, "echo", lambda msg="": captured.append(msg))

    await guide.content.callback("string-formulas")

    output = "".join(captured)
    assert "String formula content" in output


@pytest.mark.asyncio
async def test_content_handles_empty_lines_at_start(docs_setup, monkeypatch):
    """Test content command skipping empty lines at start."""
    topic_file = docs_setup / "sample.md"
    topic_file.write_text("---\nmetadata\n---\n\n\n\nActual content")

    captured: list[str] = []
    monkeypatch.setattr(guide.click, "echo", lambda msg="": captured.append(msg))

    await guide.content.callback("sample")

    output = "".join(captured)
    assert "Actual content" in output


@pytest.mark.asyncio
async def test_search_missing_docs(tmp_path, monkeypatch):
    """Test search command when docs directory doesn't exist."""
    module_file = tmp_path / "fake" / "guide.py"
    module_file.parent.mkdir(parents=True)
    module_file.write_text("# dummy")
    monkeypatch.setattr(guide, "__file__", str(module_file))

    captured: list[str] = []
    monkeypatch.setattr(guide.click, "echo", lambda msg="": captured.append(msg))

    await guide.search.callback("query", topic=None, max_results=10)

    assert "Documentation not found" in "".join(captured)


@pytest.mark.asyncio
async def test_search_specific_topic(docs_setup, monkeypatch):
    """Test search command with specific topic."""
    topic_file = docs_setup / "triggers.md"
    topic_file.write_text("This line mentions trigger functionality")

    captured: list[str] = []
    monkeypatch.setattr(guide.click, "echo", lambda msg="": captured.append(msg))

    await guide.search.callback("trigger", topic="triggers", max_results=10)

    payload = json.loads("".join(captured))
    assert payload["results_count"] > 0


@pytest.mark.asyncio
async def test_structure_missing_docs(tmp_path, monkeypatch):
    """Test structure command when docs directory doesn't exist."""
    module_file = tmp_path / "fake" / "guide.py"
    module_file.parent.mkdir(parents=True)
    module_file.write_text("# dummy")
    monkeypatch.setattr(guide, "__file__", str(module_file))

    captured: list[str] = []
    monkeypatch.setattr(guide.click, "echo", lambda msg="": captured.append(msg))

    await guide.structure.callback("sample")

    assert "Documentation not found" in "".join(captured)


@pytest.mark.asyncio
async def test_structure_formula_topic(docs_setup, monkeypatch):
    """Test structure command with formula topic."""
    formula_file = docs_setup / "formulas" / "string-formulas.md"
    formula_file.write_text("# String Formulas\n## Basic Functions\n### UPPER\n```ruby\nUPPER('test')\n```")

    captured: list[str] = []
    monkeypatch.setattr(guide.click, "echo", lambda msg="": captured.append(msg))

    await guide.structure.callback("string-formulas")

    payload = json.loads("".join(captured))
    assert payload["topic"] == "string-formulas"
    assert "Basic Functions" in payload["sections"]


@pytest.mark.asyncio
async def test_index_missing_docs(tmp_path, monkeypatch):
    """Test index command when docs directory doesn't exist."""
    module_file = tmp_path / "fake" / "guide.py"
    module_file.parent.mkdir(parents=True)
    module_file.write_text("# dummy")
    monkeypatch.setattr(guide, "__file__", str(module_file))

    captured: list[str] = []
    monkeypatch.setattr(guide.click, "echo", lambda msg="": captured.append(msg))

    await guide.index.callback()

    assert "Documentation not found" in "".join(captured)
