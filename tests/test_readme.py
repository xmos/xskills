# Copyright 2026 XMOS LIMITED.
# This Software is subject to the terms of the XMOS Public Licence: Version 1.

"""Validate the public README's RST syntax and local file links.

Docutils parsing treats warnings as errors and disables syntax highlighting so
validation does not require Pygments. These checks do not assess visual rendering,
external URLs, link fragments, or the correctness of installation commands.
"""

from urllib.parse import unquote, urlsplit

from docutils import nodes


def test_readme_rst(readme_tree):
    """Require warning-free RST parsing and at least one document section."""
    assert list(readme_tree.findall(nodes.section)), "README must contain RST sections"


def test_readme_local_links(repo_root, readme_tree):
    """Require README file links to resolve relative to the repository root."""
    for reference in readme_tree.findall(nodes.reference):
        target = reference.get("refuri")
        if target:
            parsed = urlsplit(target)
            if not parsed.scheme and not parsed.netloc and parsed.path:
                assert (repo_root / unquote(parsed.path)).exists(), (
                    f"Broken README local link: {target}"
                )
