---
name: xmos-project-structure
description: Use when setting up a new XMOS project or sandbox, navigating an existing XMOS repo layout, deciding where dependencies/libraries or the xskills guidance repo should live, or setting up Python tooling (always use a venv) for XMOS build/CI scripts. Covers general XMOS sandbox conventions with XCommon CMake.
---

# XMOS project structure

## Sandbox convention

XMOS projects are conventionally developed inside a **sandbox**: a directory that contains one or
more git repositories side by side (an application repo plus its library dependencies), rather than
vendoring dependencies inside a single repo. XCommon CMake (see
[`xmos-build-system`](../xmos-build-system/SKILL.md)) is aware of this convention through
`XMOS_SANDBOX_DIR` and resolves sibling library repos from it.

`xskills` is distributed independently of application dependencies. Guidance may be
installed in the coding tool, accessed from a local checkout or retrieved from an
official release. Do not assume a fixed checkout path or require it to live inside
or outside the sandbox. See [`README.rst`](../../README.rst) for tool-specific setup.

A real application sandbox typically looks like:

```text
<sandbox>/
├─ my_application/            # your app's repo
├─ lib_xcore/                 # a dependency, checked out as its own repo
├─ lib_i2c/                   # another dependency
└─ ...
```

Do not assume a single monolithic repo containing all dependencies — check for a sandbox layout
first when navigating an unfamiliar XMOS codebase.

The examples here describe XCommon CMake conventions, not a required layout for every
repository. Prefer XCommon CMake for new projects; existing repositories may use legacy
Make-based XCommon or Waf-based xwaf. Identify the actual build system from repository
documentation and CI, preserving its workflow during maintenance unless migration is
requested. See [build-system selection](../xmos-build-system/SKILL.md#identify-the-projects-build-system).

### Repo naming/prefix convention

XCommon CMake repos at the sandbox root follow a naming convention that indicates their role (see
[`xmos-build-system`](../xmos-build-system/SKILL.md) for the CMake configuration side of this):

- **`sw_*`** — an application repo. Inside it, each buildable application variant is its own
  `app_*` subdirectory containing `src/` and a `CMakeLists.txt`. A single `sw_*` repo can contain
  several `app_*` targets (e.g. one per hardware variant).
- **`lib_*`** — a module (source compiled directly into whatever links it) or a static-library repo
  (prebuilt archive, optionally with source to rebuild it). A module commonly provides
  `lib_build_info.cmake` for consumers. Static-library rebuild projects and a library's
  examples/tests may also provide `CMakeLists.txt` build entry points; inspect the actual
  repository rather than inferring buildability solely from its prefix.

These repositories conventionally sit as siblings at the sandbox root, allowing
applications to share dependency checkouts. Existing layouts and configured dependency
location overrides may differ; preserve a working arrangement rather than reorganising
it merely to match this example.

## Finding repository and central agent guidance

Read the application or library repository's `AGENTS.md` and other applicable project
instructions. Follow references to central XMOS guidance through an accessible installed
copy, checkout or official release; a link alone does not install or load skills.
Use the referenced release or version rather than assuming a particular branch or path.
If central guidance cannot be accessed, state that limitation and continue using the
project's documentation.

Library guidance may have a shared prefix followed by `## Repository-Specific Guidance`.
Read both, preserving the common instructions and any custom content. Repository-specific
hardware, compatibility and legacy requirements take precedence over general recommendations.
Do not infer that an older repository needs migration simply because its layout or
implementation differs from current guidance. See
[`xmos-library-repo-style`](../xmos-library-repo-style/SKILL.md) for maintaining library
instructions.

## Always use a Python virtual environment

Any Python tooling used for building, testing, or automating an XMOS sandbox (dependency-fetch
scripts, CI helpers, test runners, etc.) should run inside its own **virtual environment** (venv),
never installed into the system/global Python interpreter.

```sh
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
```

This is independent of, and in addition to, activating the XTC Tools environment (see
[`xmos-environment-setup`](../xmos-environment-setup/SKILL.md)) — the two environments serve
different purposes (Python tooling vs. the XCORE compiler toolchain) and should not be conflated.

### Windows: a bare `python`/`python3` on `PATH` may be a Microsoft Store stub, not a real interpreter

On Windows, `python -m venv .venv` (or any bare `python`/`python3` invocation) can silently resolve
to the Microsoft Store's "app execution alias" stub instead of a real interpreter, even when a real
Python is installed elsewhere on the machine. The stub prints `Python was not found; run without
arguments to install from the Microsoft Store...` and exits with a nonzero code — easy to mistake
for "Python isn't installed" when it actually is. Confirm which `python` you're about to use before
creating a venv (e.g. `where.exe python` / `Get-Command python` on PowerShell) — if it points under
`...\AppData\Local\Microsoft\WindowsApps\python.exe`, use a real interpreter's full path instead (or
the `py` launcher, e.g. `py -3 -m venv .venv`), and disable the alias under *Settings > Apps > App
execution aliases* if it keeps getting picked up first.

### Headless pytest runs that use matplotlib need `MPLBACKEND=Agg`

Several `lib_*` repos' Python test suites (e.g. `lib_sw_pll/tests/test_lib_sw_pll.py`) import
`matplotlib.pyplot` for diagnostic plotting even in tests that don't otherwise need a display.
Without a real display available (a typical agent/CI/headless shell), matplotlib's default
interactive backend (`TkAgg` on Windows) fails with an error such as `_tkinter.TclError: invalid
command name "tcl_findLibrary"` when a test tries to create a figure — this looks like a test
logic failure but is purely an environment/backend issue. Set the non-interactive `Agg` backend
before running pytest to fix it, without touching the repo's own test code:

```powershell
$env:MPLBACKEND = "Agg"    # PowerShell
```
```sh
export MPLBACKEND=Agg      # bash/zsh
```

Confirmed empirically: `lib_sw_pll`'s pure-Python `SimDut`-based tests (no compiled `.xe`/hardware
needed) went from 11 errors to 0 once `MPLBACKEND=Agg` was set, with no other change.

### Identify the test workflow before running tests

Read the repository's README and test documentation, then inspect its CI configuration —
particularly the `Jenkinsfile` and any scripts it invokes — for supported test commands, build
options and prerequisites. CI may depend on internal tooling or hardware fixtures, so identify
which steps can be reproduced locally rather than copying the pipeline blindly.

Do not infer the runner from a `tests/` directory or one file type alone: Python tests may build
or launch target applications, and target builds may invoke Python generators. Establish whether
the selected tests need a host runner, the simulator, hardware or additional fixtures.

Use the documented environment and dependency versions. Run Python tooling in a virtual
environment, activate XTC Tools when required, and select the smallest documented test target
that verifies the change. See [`xmos-build-system`](../xmos-build-system/SKILL.md) and
[`xmos-run-and-simulate`](../xmos-run-and-simulate/SKILL.md) for target applications.

## Where things live

- Application/library source, `CMakeLists.txt` — repo root or a conventional subdirectory per the
  specific repo's own layout.
- Build output — `build/` and `bin/` (git-ignored; regenerated by
  [`xmos-build-system`](../xmos-build-system/SKILL.md)).
- Library dependency sources — see
  [locating dependency sources](../xmos-build-system/SKILL.md#locating-dependency-sources).
