# xskills

Skills repository for XMOS-based software development.

## Skills

### fix-repo-checks

`test_repo_checks` is used in many XMOS originated repositories to ensure quality, consistency etc. 
This skill automatically fixes `test_repo_checks` failures in XMOS library repositories. 

**What it does:**
- Runs pytest to identify failures
- Sets up infr_apps environment (clones if needed, creates `.venv_<repo_name>`)
- Auto-fixes: copyright headers, LICENSE.rst, CHANGELOG.rst
- AI-fixes: README.rst, settings.yml, version consistency, metadata, docs, deps
- Validates `xmos_public_v1` license appropriateness
- Reports results (changes left uncommitted)

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

How to sync automatically with OpenCode's remote config plugin.

### 1. Install opencode-remote-config plugin

```bash
npm install -g @jgordijn/opencode-remote-config
```

### 2. Configure OpenCode

Add to `~/.config/opencode/opencode.json`:
```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["@jgordijn/opencode-remote-config"]
}
```

Create `~/.config/opencode/remote-config.json`:
```json
{
  "$schema": "https://raw.githubusercontent.com/jgordijn/opencode-remote-config/main/remote-skills.schema.json",
  "repositories": [
    {
      "url": "https://github.com/xmos/xskills.git",
      "ref": "main"
    }
  ]
}
```

### 3. Restart OpenCode

Skills sync on startup.


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
    └── fix-repo-checks/SKILL.md
```

Can add `agent/*.md`, `command/*.ts`, `plugin/*.ts` later.

---

## Troubleshooting

**Plugin not loading:** Check `~/.config/opencode/opencode.json` contains plugin entry

**Skills not syncing:** Delete `~/.cache/opencode/remote-config/repos/` and restart OpenCode

**Git auth issues:** Use SSH (`git@github.com:...`) or HTTPS with token
