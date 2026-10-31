# Copyright 2026 XMOS LIMITED.
# This Software is subject to the terms of the XMOS Public Licence: Version 1.

"""Shared fixtures for repository paths and strict README parsing."""

from pathlib import Path

import pytest
from docutils.core import publish_doctree


@pytest.fixture(scope="session")
def repo_root():
    """Locate the checkout independently of pytest's working directory."""
    return Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def readme_tree(repo_root):
    """Parse README.rst once, failing on RST warnings or errors."""
    return publish_doctree(
        (repo_root / "README.rst").read_text(encoding="utf-8"),
        settings_overrides={
            "halt_level": 2,
            "report_level": 2,
            "syntax_highlight": "none",
        },
    )
