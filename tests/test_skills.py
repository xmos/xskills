# Copyright 2026 XMOS LIMITED.
# This Software is subject to the terms of the XMOS Public Licence: Version 1.

"""Validate skill packaging and repository integration.

The Agent Skills reference validator checks standard frontmatter fields, required
name and description values, naming rules, directory matches, and length limits.
Additional checks cover optional field types, the repository's xmos- naming
convention, local Markdown links, bundled script paths, indexes, and the manifest.

These are structural checks: they do not execute scripts, validate technical
guidance, contact external URLs, or evaluate agent behaviour. Link fragments are
not checked. Script discovery checks explicit scripts/<filename> references;
it does not attempt to interpret arbitrary commands or application example paths.
"""

import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

import pytest
from docutils import nodes
from markdown_it import MarkdownIt
from skills_ref.parser import parse_frontmatter
from skills_ref.validator import validate


ROOT = Path(__file__).resolve().parents[1]
SKILLS = sorted((ROOT / "skills").iterdir())
MARKDOWN_FILES = sorted((ROOT / "skills").rglob("*.md")) + [
    ROOT / "AGENTS.md",
    ROOT / "CLAUDE.md",
    ROOT / ".github/copilot-instructions.md",
    ROOT / ".cursor/rules/xmos.mdc",
]


def local_targets(document):
    """Extract actual Markdown links, ignoring code examples and external URLs."""
    for token in MarkdownIt().parse(document):
        for child in token.children or []:
            attribute = {"link_open": "href", "image": "src"}.get(child.type)
            if attribute:
                target = child.attrGet(attribute)
                parsed = urlsplit(target)
                if not parsed.scheme and not parsed.netloc and parsed.path:
                    yield unquote(parsed.path)


def test_skills_present():
    """Require at least one skill so an empty collection cannot pass validation."""
    assert SKILLS, "No skills found"


@pytest.mark.parametrize("skill", SKILLS, ids=lambda path: path.name)
def test_skill_specification(skill):
    """Validate standard skill metadata and the repository's XMOS name prefix."""
    assert skill.is_dir(), f"Unexpected entry in skills/: {skill.name}"
    assert (skill / "SKILL.md").is_file(), f"Missing skill file: {skill / 'SKILL.md'}"
    errors = validate(skill)
    assert not errors, "\n".join(errors)
    assert skill.name.startswith("xmos-"), "XMOS skills must use the xmos- prefix"

    metadata, _ = parse_frontmatter((skill / "SKILL.md").read_text(encoding="utf-8"))
    if "metadata" in metadata:
        assert isinstance(metadata["metadata"], dict), "metadata must be a mapping"
        assert all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in metadata["metadata"].items()
        ), "Agent Skills metadata must map strings to strings"
    if "compatibility" in metadata:
        assert metadata["compatibility"].strip(), "compatibility must not be empty"
    for field in ("license", "allowed-tools"):
        if field in metadata:
            assert isinstance(metadata[field], str), f"{field} must be a string"


@pytest.mark.parametrize("document", MARKDOWN_FILES, ids=lambda path: str(path.relative_to(ROOT)))
def test_markdown_local_links(document):
    """Require local link and image targets to exist relative to each document."""
    missing = [
        target
        for target in local_targets(document.read_text(encoding="utf-8"))
        if not (document.parent / target).exists()
    ]
    assert not missing, f"Broken local links in {document}: {missing}"


@pytest.mark.parametrize("skill", SKILLS, ids=lambda path: path.name)
def test_skill_script_references(skill):
    """Require explicitly referenced scripts to exist in the skill directory."""
    # These are bundled resources, unlike application paths in code examples.
    references = re.findall(
        r"scripts[/\\][A-Za-z0-9_./-]+\.[A-Za-z0-9]+",
        (skill / "SKILL.md").read_text(encoding="utf-8"),
    )
    for reference in references:
        assert (skill / reference.replace("\\", "/")).is_file(), (
            f"Missing bundled script in {skill.name}: {reference}"
        )


def test_skill_indexes(repo_root, readme_tree):
    """Require both published skill indexes to match the available directories.

Only the README's Skills section and the AGENTS.md table count as indexes;
incidental skill links elsewhere do not satisfy this check.
"""
    expected = {f"skills/{skill.name}/SKILL.md" for skill in SKILLS}
    skills_section = next(
        section
        for section in readme_tree.findall(nodes.section)
        if section[0].astext() == "Skills"
    )
    readme_index = {
        reference["refuri"]
        for reference in skills_section.findall(nodes.reference)
        if reference.get("refuri", "").startswith("skills/")
        and reference["refuri"].endswith("/SKILL.md")
    }
    agents_table = "\n".join(
        line
        for line in (repo_root / "AGENTS.md").read_text(encoding="utf-8").splitlines()
        if line.startswith("| ")
    )
    agents_index = {
        target.removeprefix("./")
        for target in local_targets(agents_table)
        if target.removeprefix("./").startswith("skills/")
        and target.endswith("/SKILL.md")
    }
    for label, index in (("README", readme_index), ("AGENTS.md", agents_index)):
        assert index == expected, (
            f"{label} skill index differs from skills/: "
            f"missing={sorted(expected - index)}, stale={sorted(index - expected)}"
        )


def test_manifest(repo_root):
    """Check instruction files are unique, local Markdown paths including AGENTS.md.

This checks the repository's manifest contents, not plugin runtime behaviour
or the external JSON schema URL.
"""
    manifest = json.loads((repo_root / "manifest.json").read_text(encoding="utf-8"))
    instructions = manifest["instructions"]
    assert isinstance(instructions, list) and instructions, (
        "Manifest instructions must be a non-empty list"
    )
    assert "AGENTS.md" in instructions, "Manifest must import core AGENTS.md guidance"
    assert len(instructions) == len(set(instructions)), "Duplicate instruction paths"
    for instruction in instructions:
        assert isinstance(instruction, str), "Instruction paths must be strings"
        path = Path(instruction)
        assert not path.is_absolute() and ".." not in path.parts, (
            f"Instruction path must be relative without traversal: {instruction}"
        )
        assert "\\" not in instruction and path.suffix == ".md", (
            f"Instruction path must use forward slashes and end in .md: {instruction}"
        )
        assert (repo_root / path).is_file(), f"Missing instruction file: {instruction}"
