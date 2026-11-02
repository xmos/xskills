# xskills

AI coding-agent skills for XMOS XCORE development.

Copyright 2026 XMOS LIMITED. This Software is subject to the terms of the
[XMOS Public Licence: Version 1](LICENSE.rst).

## Skills

- [xmos-build-system](skills/xmos-build-system/SKILL.md): Build and configure XCommon CMake projects.
- [xmos-c-programming](skills/xmos-c-programming/SKILL.md): Write multicore XCORE C using `lib_xcore`.
- [xmos-clock-domains](skills/xmos-clock-domains/SKILL.md): Configure and reason about xcore.ai clocks.
- [xmos-debugging-profiling](skills/xmos-debugging-profiling/SKILL.md): Debug and profile with xgdb, xSCOPE, and xgprof.
- [xmos-embedded-c-practices](skills/xmos-embedded-c-practices/SKILL.md): Apply safe, efficient embedded C practices.
- [xmos-environment-setup](skills/xmos-environment-setup/SKILL.md): Activate and troubleshoot XTC Tools environments.
- [xmos-flashing](skills/xmos-flashing/SKILL.md): Program persistent images with `xflash`.
- [xmos-internal-repo-checks](skills/xmos-internal-repo-checks/SKILL.md): Diagnose and fix repository checks using XMOS internal scripts.
- [xmos-library-repo-style](skills/xmos-library-repo-style/SKILL.md): Follow XMOS library repository conventions.
- [xmos-multi-tile-architecture](skills/xmos-multi-tile-architecture/SKILL.md): Structure applications across multiple tiles.
- [xmos-project-structure](skills/xmos-project-structure/SKILL.md): Organize XMOS projects, sandboxes, and tooling.
- [xmos-run-and-simulate](skills/xmos-run-and-simulate/SKILL.md): Run applications using `xrun` or `xsim`.
- [xmos-skill-authoring](skills/xmos-skill-authoring/SKILL.md): Create and maintain skills in this repository.
- [xmos-toolchain-paths](skills/xmos-toolchain-paths/SKILL.md): Locate toolchain headers, libraries, and targets.
- [xmos-vscode-extension](skills/xmos-vscode-extension/SKILL.md): Configure XMOS development in VS Code.
- [xmos-xs3-architecture](skills/xmos-xs3-architecture/SKILL.md): Understand XS3 hardware and execution resources.

---

## Setup (Claude Code)

Claude Code (CLI, desktop app, and the VS Code extension) loads personal skills from
`~/.claude/skills/`. All three share this same location, so setting it up once covers
all of them — no extra per-tool config needed.

Since this repo already keeps its skills under a `skills/` subfolder, point
`~/.claude/skills` at it with a directory junction. This only works if
`~/.claude/skills` doesn't already exist (i.e. you have no other personal skills there).

Windows (PowerShell, no admin required — junctions, unlike symlinks, don't need elevation):
```powershell
New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills" -Target "C:\Users\<user>\xskills\skills"
```

macOS/Linux:
```bash
ln -s ~/xskills/skills ~/.claude/skills
```

If `~/.claude/skills` already has other personal skills in it, symlink individual skill
folders into it instead of linking the whole directory:
```powershell
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\xmos-build-system" -Target "C:\Users\<user>\xskills\skills\xmos-build-system"
```

Start a new Claude Code session (CLI/desktop) or reload the VS Code window afterwards
so the newly linked skills are picked up.

---

## Setup (OpenCode)

Use the [opencode-remote-config plugin](https://github.com/jgordijn/opencode-remote-config)
to sync skills automatically. This repository's `manifest.json` also imports the core
XMOS guidance from `AGENTS.md`.

The paths below configure this globally. For project-specific setup, add the plugin to
the project's `opencode.json` and create `.opencode/remote-config.json` instead. The plugin
uses project-level remote configuration when present, falling back to global configuration.
Choose project-specific setup if you only want the XMOS guidance in that project.

### 1. Configure the plugin

Add `@jgordijn/opencode-remote-config` to the `plugin` array in your existing
`~/.config/opencode/opencode.json` or `opencode.jsonc`, preserving other settings and plugins.
If you do not have a config file, create one with:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["@jgordijn/opencode-remote-config"]
}
```

OpenCode installs npm plugins automatically at startup; no global npm installation is required.

### 2. Configure the repository

Create `~/.config/opencode/remote-config.json`, or add this repository to its existing
`repositories` array:
```json
{
  "$schema": "https://raw.githubusercontent.com/jgordijn/opencode-remote-config/main/remote-skills.schema.json",
  "repositories": [
    {
      "url": "https://github.com/xmos/xskills.git",
      "ref": "develop"
    }
  ]
}
```

On Windows without symlink support, add `"installMethod": "copy"` at the top level of
`remote-config.json`, alongside `repositories`. This also works for environments where
symlinks are unsuitable, such as containers with different host and container paths.

### 3. Restart and verify

Skills and core XMOS instructions sync on startup. Ask OpenCode to list its available
XMOS skills and confirm that names such as `xmos-build-system` and `xmos-c-programming`
appear. Check startup output for sync errors if they are missing.

See the [plugin documentation](https://github.com/jgordijn/opencode-remote-config#readme)
for selective imports, local checkouts, and additional configuration options.

### Troubleshooting

**Plugin not loading:** Check your `~/.config/opencode/opencode.json` or `opencode.jsonc` contains the plugin entry.

**Skills not syncing:** Check the configured branch and startup errors. If the cached checkout needs resetting, delete only the xskills checkout under `~/.cache/opencode/remote-config/repos/` and restart OpenCode.

**Git auth issues:** Verify access using `git ls-remote` with the configured repository URL. For SSH, check your SSH key; for HTTPS, check your Git credential helper.


## Setup (VSCode)

It is recommended to check
out this repo into a common location (e.g. ``C:\Users\<user>\xskills\`` or ``~/xskills/``)
and then point your coding tool at it.

For VS Code users, this can be done by adding the xskills folder to your
``chat.agentSkillsLocations`` setting in your user or workspace ``.vscode/settings.json`` file.
Note the path must be relative to your home directory::

    {
      "chat.agentSkillsLocations": {
          "~/Documents/xskills/skills": true
      }
    }

This can also be done by searching for "agent skills" in File -> Preferences -> Settings.

See the full docs at
[Use Agent Skills in VS Code](https://code.visualstudio.com/docs/agent-customization/agent-skills).


## Setup (Copilot CLI)

It is recommended to check
out this repo into a common location (e.g. ``C:\Users\<user>\xskills\`` or ``~/xskills/``)
and then point your coding tool at it.

You can add skills in the Copilot CLI with:

```
/skills add ~/xskills
```

Alternatively you can use the ``gh`` API to install the skills::

```
gh skill install xmos/xskills
```

See the full docs at [Adding agent skills for GitHub Copilot](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills#adding-a-skill-that-someone-else-has-created).

## Structure

```
xskills/
├── README.md
└── skills/
    ├── <skill-name>/SKILL.md
    └── ...
```

Can add `agent/*.md`, `command/*.ts`, `plugin/*.ts` later.
