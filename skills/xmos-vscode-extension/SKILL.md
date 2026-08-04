---
name: xmos-vscode-extension
description: Use when building, running, debugging, or flashing an XMOS application from within VS Code using the XMOS XTC Tools extension; configuring tasks.json/launch.json for xtc-tools; fixing IntelliSense errors for XMOS headers; or resolving conflicts with the Microsoft CMake Tools extension. Covers the XTC Tools VS Code extension for XTC Tools 15.3.1.
---

# XMOS XTC Tools VS Code extension

This skill covers the **XTC Tools VS Code extension** specifically. For the underlying CLI tools it
wraps, see [`xmos-build-system`](../xmos-build-system/SKILL.md),
[`xmos-run-and-simulate`](../xmos-run-and-simulate/SKILL.md), and
[`xmos-debugging-profiling`](../xmos-debugging-profiling/SKILL.md) — everything the extension does
can also be done from the command line.

## Setup

- Select the active tools version via the extension's "Configure Global/Local XTC Tools" command
  (stored in the `xtc-tools.toolPath` setting).
- **Disable the Microsoft CMake Tools extension** if installed — it conflicts with this extension's
  own XCommon CMake integration.
- IntelliSense requires the Microsoft C/C++ extension (`ms-vscode.cpptools`); it understands C/C++
  files but **not** XC files.

## Views

- **Getting Started** — browse and download XMOS application-note example projects.
- **XTC Tools** — quick actions: Open XTC Terminal, Build, Clean, Run, Debug, Flash Device.
- **Build Projects** — tree of detected CMake-based projects in the workspace.
- **Build Configurations** — available build targets/configurations from the build system.
- **Devices** — connected xtag adapters; refresh manually after plugging one in; select a default
  device when more than one is connected.

"Open XTC Terminal" opens a terminal with the XTC Tools environment already activated — the VS Code
equivalent of manually activating the environment on the command line (see
[`xmos-environment-setup`](../xmos-environment-setup/SKILL.md)). It can be set as the default
terminal profile.

## Build / Run / Debug / Flash

The Build/Clean/Run/Debug/Flash actions can be overridden or customized via workspace configuration:

- `tasks.json` — use a task of type `xtc-tools.script` (with `purpose: build` or `purpose: clean`)
  or `xtc-tools.flash` for custom build/clean/flash behavior.
- `launch.json` — use a configuration of type `xtc-tools.xrun` (run) or `xtc-tools.debug` (debug),
  which drive `xrun`/`xgdb` under the hood.

## Debugging

Set a breakpoint in the gutter, then use the Debug button/launch configuration. This starts an
`xgdb`-backed debug session with the usual VS Code Call Stack / Variables views; the Debug Console
also accepts raw `xgdb` commands directly.

If VS Code reports something like "No debug information found," the application was built without
`-g`. Add `-g` (and typically `-report` for stack/memory usage) to `APP_COMPILER_FLAGS` in
`CMakeLists.txt` and rebuild — see [`xmos-build-system`](../xmos-build-system/SKILL.md).

## Inspecting a built `.xe`

Double-clicking a `.xe` file in the Explorer opens a disassembly/symbol-table viewer — the GUI
equivalent of running `xobjdump` from the command line.

## Settings of note

| Setting | Purpose |
|---|---|
| `xtc-tools.toolPath` | Path to the active XTC Tools install. |
| `xtc-tools.buildDirectory` | Build output directory (default `build`). |
| `xtc-tools.numberOfBuildJobs` | Parallel build jobs (`0` = auto). |
| `xtc-tools.runOutputLocation` | Where run output is shown: terminal / debug console / both. |
| `xtc-tools.buildBeforeRun` | Whether Run automatically builds first (default `false`). |
| `xtc-tools.autoSelectRootProject` | Auto-select a single detected root project. |

## Syntax highlighting

The extension contributes syntax highlighting for `.xc` (XC) and `.S` (XCORE assembly) files.
