---
name: xmos-environment-setup
description: Use BEFORE running any XTC Tools command (`xcc`, `xmake`, `xrun`, `xsim`, `xgdb`, `xflash`, `xobjdump`) or an XCommon CMake configure/build (`cmake -G "Unix Makefiles"`, `xmake -C build`) for an XMOS project. Check activation in the executing shell; persistence between agent calls depends on the harness. Also use when commands are reported as "command not found" or "not recognized", or when setting up a shell/terminal/CI job to build or run XMOS code. Provides a one-command wrapper (scripts/xtc.ps1) for PowerShell. Covers XTC Tools 15.3.1.
---

# XMOS environment setup

## Quick start for agents (Windows PowerShell)

Agent harnesses may start independent shells for tool calls; do not assume earlier activation
persists. Activate and run in the **same** call using the wrapper in the `scripts` folder next to this
file. `<skill-dir>` below is the directory containing this `SKILL.md`; substitute its absolute
path:

```powershell
& "<skill-dir>\scripts\xtc.ps1" xmake -C build
& "<skill-dir>\scripts\xtc.ps1" xrun --xscope bin\app.xe
```

The wrapper imports `SetEnv.bat` into the PowerShell process, runs the command and exits with its
exit code. With no arguments it just activates the environment and prints `xcc --version`. It
defaults to XTC 15.3.1; set `$env:XTC_VERSION` (or `$env:XTC_SETENV` for a full path to
`SetEnv.bat`) to use another install. To run several commands in one call, dot-source it first:
`. "<skill-dir>\scripts\xtc.ps1"; cmake -G "Unix Makefiles" -B build; xmake -C build`.

The rest of this skill explains what the wrapper does and covers other shells and operating systems.

## Background

The XTC Tools (`xcc`, `xrun`, `xsim`, `xgdb`, `xflash`, `xmake`, `xobjdump`, ...) are not on `PATH`
by default. Ensure the executing shell has the selected tools environment, activating it when
absent. A child process normally inherits its parent's exported environment, but independent
terminals or agent calls may not share that parent. Missing activation is a common reason a
command "isn't found" or picks up the wrong tools version.

## Windows

**Interactively**:

1. Open the Start Menu.
2. Choose **XMOS → XTC Tools 15.3.1 Command Prompt**.
3. This opens a `cmd.exe` with the required environment variables already set. Run all XTC Tools
   commands from this prompt (or a shell launched from it).

**In an existing shell (PowerShell, a VS Code integrated terminal, a CI runner, or any context an
agent is already running in, where opening a new Start Menu shortcut isn't practical)**: the
install directory contains a `SetEnv.bat`, e.g.
`C:\Program Files\XMOS\XTC\15.3.1\SetEnv.bat` (find the exact install root first — see
[`xmos-toolchain-paths`](../xmos-toolchain-paths/SKILL.md) — version-numbered subdirectories are
common, e.g. multiple `C:\Program Files\XMOS\XTC\<version>\` installs side by side). Because it's a
batch file, running it directly from PowerShell (`.\SetEnv.bat` or `& SetEnv.bat`) does **not**
export its environment variables into the PowerShell session — the child `cmd.exe` process exits
and takes its environment with it. Instead, invoke it via `cmd /c` together with `set`, and import
the resulting variables into the current PowerShell session:

```powershell
cmd /c "`"C:\Program Files\XMOS\XTC\15.3.1\SetEnv.bat`" && set" | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        Set-Item -Path "env:$($matches[1])" -Value $matches[2]
    }
}
xcc --version   # confirm activation worked in this shell
```

This is the reliable way to activate the environment non-interactively (e.g. from an agent's own
terminal) without needing a fresh Command Prompt window. Repeat it when the executing PowerShell
session has not inherited the required environment.

## macOS

**Interactively**: run the installation's `SetEnv.command`, e.g.
`/Applications/XMOS_XTC_15.3.1/SetEnv.command`. It sources `SetEnv.sh` and then starts a
new configured `bash` shell; enter XTC Tools commands in that shell. It does not activate
the shell that launched it.

**Non-interactively (agents, scripts, CI)**: do not use `SetEnv.command`, which waits in a
new shell. Source the selected installation's `SetEnv.sh` and run the commands in the same
shell call, from the project directory:

```sh
source "/Applications/XMOS_XTC_15.3.1/SetEnv.sh" &&
xcc --version &&
xmake -C build
```

Substitute the path of the installation the project requires.

## Linux

**Interactively**: in a terminal, `cd` into the tools installation directory and `source`
its `SetEnv` script, then run XTC Tools commands in that same terminal:

```sh
cd ~/XMOS/XTC/15.3.1   # default install location - see below
source SetEnv
```

**Non-interactively (agents, scripts, CI)**: activate and run the commands in the same shell
call. The documented activation runs from the installation directory, so return to the
project directory before building:

```sh
cd ~/XMOS/XTC/15.3.1 && source SetEnv && cd - >/dev/null &&
xcc --version &&
xmake -C build
```

Run this from the project directory, substituting the installation the project requires.

### Default Linux install location

The XTC Tools Linux archive is conventionally extracted into the home directory:

```sh
tar -xf tools-15-linux-15-3-1.tgz -C ~
```

which installs to `~/XMOS/XTC/<version>` (the "tools installation directory" / "tools root"), e.g.
`~/XMOS/XTC/15.3.1`. If your installation used a different target directory, `source SetEnv` from
that directory instead.

## Any OS

Whatever the platform, the goal is the same: activation sets `XMOS_TOOL_PATH` and the related
`XCC_*`/`PATH` variables described in
[`xmos-toolchain-paths`](../xmos-toolchain-paths/SKILL.md) in the executing shell and its child
processes (these tools do not require a permanently-modified system-wide `PATH`).

## Verifying activation

After activating the environment (any OS), confirm it worked:

```sh
xcc --version
```

This should print the XTC Tools version (report this version in any bug report). If it fails,
the environment was not activated correctly in the current shell — re-run the activation step in
this exact shell/terminal rather than relying on an independent earlier tool call.

## Notes for scripts, CI, and agents

- Exported environment variables are inherited by child processes; see the
  [Bash environment reference](https://www.gnu.org/software/bash/manual/html_node/Environment.html).
  Changes made inside a child process do not update its parent, which is why running `SetEnv.bat`
  alone from PowerShell is insufficient. Independent CI steps or agent calls may start from an
  unactivated environment. Check the actual executing shell rather than assuming either persistence
  or a reset between calls.
- Prefer verifying with `xcc --version` at the start of a task rather than assuming the environment
  is active, especially in automated/agent-driven workflows.
- **PowerShell + `2>&1 | Select-Object`/`Out-String` can misreport a successful build as failed.**
  Piping an XTC Tools command's combined output (e.g. `xmake -C build 2>&1 | Select-Object -Last
  80`) through a formatting cmdlet converts stderr lines (like ordinary compiler warnings) into
  PowerShell error records, which can make the wrapping tool/script report a nonzero exit code even
  though the real build succeeded. Confirm the actual result via `$LASTEXITCODE` after a plain,
  unpiped invocation (or check for the expected `.xe` under `bin/`) rather than trusting the exit
  code of a piped/redirected command.
- See [`xmos-project-structure`](../xmos-project-structure/SKILL.md) for how environment activation
  fits into the wider convention of an XMOS sandbox (and why Python tooling in that sandbox should
  use its own virtual environment, separate from the XTC Tools environment).
