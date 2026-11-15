:orphan:

####################################################
xskills: AI coding-agent skills for XMOS development
####################################################

Summary
=======

AI coding-agent skills for XMOS XCORE development.

This repository provides reusable workflows for coding agents that support the
`Agent Skills standard <https://agentskills.io/specification>`_. The guidance
targets **XTC Tools 15.3.1** and **XS3 devices** (i.e. XCORE.AI).

Skills are loaded on demand for tasks such as building applications, programming
multicore C, debugging, and running on hardware or in simulation. Each skill
includes instructions and may include supporting scripts.

Skills
======

* `xmos-build-system <skills/xmos-build-system/SKILL.md>`_: Build and configure XCommon CMake projects.
* `xmos-c-programming <skills/xmos-c-programming/SKILL.md>`_: Write multicore XCORE C using ``lib_xcore``.
* `xmos-capability-discovery <skills/xmos-capability-discovery/SKILL.md>`_: Find and verify existing XMOS software using accessible official sources.
* `xmos-clock-domains <skills/xmos-clock-domains/SKILL.md>`_: Configure and reason about xcore.ai clocks.
* `xmos-debugging-profiling <skills/xmos-debugging-profiling/SKILL.md>`_: Debug and profile with xgdb, xgprof and structured xSCOPE probes.
* `xmos-embedded-c-practices <skills/xmos-embedded-c-practices/SKILL.md>`_: Apply safe, efficient embedded C practices.
* `xmos-real-time-programming <skills/xmos-real-time-programming/SKILL.md>`_: Wall-time, IO-time, program time and how to keep them separate.
* `xmos-environment-setup <skills/xmos-environment-setup/SKILL.md>`_: Activate and troubleshoot XTC Tools environments.
* `xmos-flashing <skills/xmos-flashing/SKILL.md>`_: Program persistent images with ``xflash``.
* `xmos-internal-repo-checks <skills/xmos-internal-repo-checks/SKILL.md>`_: Diagnose and fix repository checks using XMOS internal scripts.
* `xmos-library-repo-style <skills/xmos-library-repo-style/SKILL.md>`_: Follow XMOS library repository conventions.
* `xmos-multi-tile-architecture <skills/xmos-multi-tile-architecture/SKILL.md>`_: Structure applications across multiple tiles.
* `xmos-numeric-programming <skills/xmos-numeric-programming/SKILL.md>`_: Choose numeric representations and math libraries for DSP code.
* `xmos-printing-logging <skills/xmos-printing-logging/SKILL.md>`_: Choose printing/logging APIs, configure per-unit diagnostics and xSCOPE text I/O, and handle buffering.
* `xmos-project-structure <skills/xmos-project-structure/SKILL.md>`_: Organize XMOS projects, sandboxes, and tooling.
* `xmos-run-and-simulate <skills/xmos-run-and-simulate/SKILL.md>`_: Run applications using ``xrun`` or ``xsim``.
* `xmos-skill-authoring <skills/xmos-skill-authoring/SKILL.md>`_: Create and maintain skills in this repository.
* `xmos-testing <skills/xmos-testing/SKILL.md>`_: Write tests with lib_unity and test_support.
* `xmos-toolchain-paths <skills/xmos-toolchain-paths/SKILL.md>`_: Locate toolchain headers, libraries, and targets.
* `xmos-vscode-extension <skills/xmos-vscode-extension/SKILL.md>`_: Configure XMOS development in VS Code.
* `xmos-xs3-architecture <skills/xmos-xs3-architecture/SKILL.md>`_: Understand XS3 hardware and execution resources.

Setup
=====

Use the subsection for your coding tool. You need that tool installed with Agent
Skills support, and Git to clone or sync this repository. XTC Tools are required
for build and run workflows; an XMOS board and XTAG adapter are required when
running on hardware.

For setups using a local checkout, clone the repository into a convenient
location, such as ``~/xskills`` or ``C:\Users\<user>\xskills``:

.. code-block:: console

   git clone https://github.com/xmos/xskills.git

Adjust the example paths below to match your checkout. Install whole skill
directories, including their scripts and resources, rather than just copying
``SKILL.md`` files.

Skills link to related skills and to repository files such as ``README.rst``
and ``AGENTS.md`` using paths relative to this checkout. Copying an individual
skill does not copy those targets. If a linked file or skill is missing, find
the related skill by its installed name, or read it from an accessible xskills
checkout or the same release on GitHub, rather than a different version.
Linking the whole ``skills/`` directory keeps these references working.

Skills and core instructions
----------------------------

``skills/<name>/SKILL.md`` contains task-specific guidance loaded on demand.
`AGENTS.md <AGENTS.md>`_ contains core XMOS principles and the skill index.
Installing skills alone does not necessarily load those core instructions.

For Claude Code, reference the absolute path to this repository's ``AGENTS.md``
from your XMOS project's ``CLAUDE.md`` using Claude's ``@/path/to/file`` import
syntax. For GitHub Copilot in VS Code or CLI, reference it from the project's
``AGENTS.md`` or ``.github/copilot-instructions.md``, asking the agent to read it
when working on XMOS code. Preserve your existing project instructions.

The OpenCode remote-config setup below imports ``AGENTS.md`` automatically via
`manifest.json <manifest.json>`_. A global configuration applies this guidance
across projects; a project-level configuration limits it to that project.

Claude Code
-----------

Claude Code supports personal skills in ``~/.claude/skills/`` and project skills
in ``.claude/skills/``. The examples below use personal skills for local sessions.
For project-only use, substitute the project's ``.claude/skills/`` directory.

If ``~/.claude/skills`` does not already exist, link it to the checkout's
``skills/`` directory.

Windows PowerShell (a directory junction does not require administrator access):

.. code-block:: powershell

   New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude"
   New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills" -Target "C:\Users\<user>\xskills\skills"

macOS/Linux:

.. code-block:: bash

   mkdir -p ~/.claude
   ln -s ~/xskills/skills ~/.claude/skills

If the skills directory already contains other skills, link individual xskills
folders into it. Repeat for each skill you want to use.

Windows PowerShell (symbolic links require Developer Mode or administrator access):

.. code-block:: powershell

   New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\xmos-build-system" -Target "C:\Users\<user>\xskills\skills\xmos-build-system"

macOS/Linux:

.. code-block:: bash

   ln -s ~/xskills/skills/xmos-build-system ~/.claude/skills/xmos-build-system

Start a fresh Claude Code session and check the ``/`` menu for
``/xmos-build-system``. These local paths do not configure Cowork or cloud
sessions; see the `Claude Code skills documentation
<https://code.claude.com/docs/en/skills>`_ for those environments.

GitHub Copilot in VS Code
-------------------------

Use ``~/.copilot/skills/`` for personal skills or ``.github/skills/`` in your
project for project-specific skills. Copy or link the selected skill directories
from this checkout into that location. The linking approach shown for Claude
Code also works with these paths.

Start a fresh chat with the Copilot harness. Open **Chat: Open Customizations**
from the Command Palette, select **Skills**, and confirm the XMOS skills appear.
You can invoke a skill through the ``/`` menu, for example
``/xmos-build-system``.

Native skill folders also work across Copilot clients, whereas VS Code's custom
skill-location settings are editor-specific. See `Use Agent Skills in VS Code
<https://code.visualstudio.com/docs/agent-customization/agent-skills>`_.

GitHub Copilot CLI
------------------

Add the local checkout's skills directory from an interactive Copilot CLI session:

.. code-block:: text

   /skills add ~/xskills/skills
   /skills reload
   /skills list

On Windows, substitute the full path to the checkout's ``skills`` directory.
Alternatively, copy or link skill directories into ``~/.copilot/skills/`` for
personal use, or ``.github/skills/`` in your project. Skills installed there for
VS Code can also be used by Copilot CLI.

Verify an individual skill with ``/skills info xmos-build-system``. See `Adding
agent skills for GitHub Copilot CLI
<https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-skills>`_
for installation and skill-management details.

OpenCode
--------

Use the `opencode-remote-config plugin
<https://github.com/jgordijn/opencode-remote-config>`_ to sync skills and the core
``AGENTS.md`` guidance automatically. Git must be available on ``PATH``.

The paths below configure this globally. For project-specific setup, add the
plugin to the project's ``opencode.json`` and create
``.opencode/remote-config.json`` instead. The plugin uses project-level remote
configuration when present, falling back to global configuration.

**Configure the plugin**

Add ``@jgordijn/opencode-remote-config`` to the ``plugin`` array in your existing
``~/.config/opencode/opencode.json`` or ``opencode.jsonc``, preserving other
settings and plugins. If you do not have a config file, create one with:

.. code-block:: json

   {
     "$schema": "https://opencode.ai/config.json",
     "plugin": ["@jgordijn/opencode-remote-config"]
   }

OpenCode installs npm plugins automatically at startup; no global npm
installation is required.

**Configure the repository**

Create ``~/.config/opencode/remote-config.json``, or add this repository to its
existing ``repositories`` array:

.. code-block:: json

   {
     "$schema": "https://raw.githubusercontent.com/jgordijn/opencode-remote-config/main/remote-skills.schema.json",
     "repositories": [
       {
         "url": "https://github.com/xmos/xskills.git",
         "ref": "main"
       }
     ]
   }

On Windows without symlink support, add ``"installMethod": "copy"`` at the top
level of ``remote-config.json``, alongside ``repositories``. This also works
where symlinks are unsuitable, such as containers with different host and
container paths.

**Restart and verify**

Skills and core XMOS instructions sync on startup. Ask OpenCode to list its
available XMOS skills and confirm that names such as ``xmos-build-system`` and
``xmos-c-programming`` appear. See the `plugin documentation
<https://github.com/jgordijn/opencode-remote-config#readme>`_ for selective imports,
local checkouts, and additional configuration options.

**Troubleshooting**

* **Plugin not loading:** Check the applicable ``opencode.json`` or
  ``opencode.jsonc`` contains the plugin entry.
* **Skills not syncing:** Check the configured branch and startup errors. If
  the cached checkout needs resetting, delete only the xskills checkout under
  ``~/.cache/opencode/remote-config/repos/`` and restart OpenCode.
* **Git authentication issues:** Verify access using ``git ls-remote`` with
  the configured repository URL. For SSH, check your SSH key; for HTTPS, check
  your Git credential helper.

Updating
========

For a local checkout, pull updates from its configured upstream branch:

.. code-block:: console

   git -C <path-to-xskills> pull --ff-only

Linked skills use the updated files. If you copied skills instead, refresh the
copies from the checkout, preserving any local customisations. If a skill is
renamed, update individual links or copies to use its new directory name.

Start a fresh agent session after updating; Copilot CLI can use
``/skills reload``. OpenCode remote-config fetches updates on startup from the
configured branch. A tag or commit reference remains pinned to that version.

Library repository integration
==============================

XMOS library repositories can use their root ``AGENTS.md`` to direct agents to
this guidance while retaining repository-specific compatibility and legacy
instructions. Follow the setup instructions for your coding tool: a link alone
does not install or load skills.

References to ``main`` use the latest approved xskills release; release tags
allow a pinned baseline. Use an accessible candidate checkout during pilots
until the first approved release is available on ``main``.

Repository validation
=====================

The repository validation suite checks Agent Skills frontmatter, skill names,
local links, bundled script references, skill indexes, the instruction manifest,
and README RST syntax.
The tests require Python 3.12 and Git, but no XTC Tools or hardware. External URLs
and the technical behaviour of skills are not tested.

Run the same suite locally from the repository root using a virtual environment.

macOS/Linux:

.. code-block:: bash

   python3 -m venv .venv
   .venv/bin/python -m pip install -r tests/requirements.txt
   .venv/bin/python -m pytest tests

Windows PowerShell:

.. code-block:: powershell

   py -3.12 -m venv .venv
   .venv\Scripts\python.exe -m pip install -r tests/requirements.txt
   .venv\Scripts\python.exe -m pytest tests

Feedback and contributions
==========================

Report problems or suggest improvements through `GitHub issues
<https://github.com/xmos/xskills/issues>`_. Include the skill name, coding agent
and version, operating system, XTC version, and relevant commands or errors.

Pull requests are welcome. Follow `xmos-skill-authoring
<skills/xmos-skill-authoring/SKILL.md>`_, keep skills in the standard
``SKILL.md`` format, and cite the relevant XMOS documentation for technical
guidance.

Repository structure
====================

.. code-block:: text

   xskills/
   ├── README.rst
   ├── LICENSE.rst
   ├── AGENTS.md
   ├── CLAUDE.md
   ├── manifest.json
   ├── Jenkinsfile
   ├── tests/                           # structural validation suite
   ├── .github/copilot-instructions.md
   ├── .cursor/rules/xmos.mdc
   └── skills/
       └── <skill-name>/
           ├── SKILL.md
           └── scripts/                 # optional supporting scripts

Licence
=======

Copyright 2026 XMOS LIMITED. This Software is subject to the terms of the
`XMOS Public Licence: Version 1 <LICENSE.rst>`_.
