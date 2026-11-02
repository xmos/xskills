---
name: xmos-toolchain-paths
description: Use when locating XMOS header files, libraries, target/.xn platform files, or the XCommon CMake build system on disk; when resolving "file not found" for xcore/*.h, xs1.h, platform.h, or xscope.h; or when configuring IntelliSense/include paths for an editor or external build tool. Covers XTC Tools 15.3.1 on Windows/macOS/Linux.
---

# XMOS toolchain paths

Where XTC Tools content lives on disk, and how to resolve it programmatically instead of
hard-coding a path.

## Install root: `XMOS_TOOL_PATH`

Once the XTC Tools environment is activated (see
[`xmos-environment-setup`](../xmos-environment-setup/SKILL.md)), the environment variable
`XMOS_TOOL_PATH` holds the install root for the active tools version, for example on Windows:

```text
C:\Program Files\XMOS\XTC\15.3.1
```

Never hard-code this path in scripts or code — always resolve it from `%XMOS_TOOL_PATH%` /
`$XMOS_TOOL_PATH`, since the exact path varies by OS, install location, and tools version.

## Headers

Standard XTC Tools headers (`xs1.h`, `xcore/*.h`, `xscope.h`, etc.) are installed under:

```text
<XMOS_TOOL_PATH>/target/include
```

If an editor's IntelliSense/IntelliSense-equivalent cannot find these headers, add
`<XMOS_TOOL_PATH>/target/include` to its include path. When using the XTC Tools VS Code extension
with an XCommon CMake project, this is normally configured automatically — see
[`xmos-vscode-extension`](../xmos-vscode-extension/SKILL.md). For other editors or standalone
`xcc` invocations, this directory is on the compiler's default search path automatically once the
environment is activated; it only needs to be added explicitly to a *separate* tool (e.g. a
non-XMOS-aware language server).

`lib_xcore` public headers live directly under `<XMOS_TOOL_PATH>/target/include/xcore/` (e.g.
`parallel.h`, `channel.h`, `select.h`, `hwtimer.h`). Each public header's macro/inline-function
implementation details (what a macro like `DECLARE_JOB` actually expands to) are in a same-named
companion file under `<XMOS_TOOL_PATH>/target/include/xcore/_support/`, e.g. `parallel.h` ->
`_support/xcore_parallel_impl.h`. Go straight to these two known locations instead of a whole-disk
search (e.g. `find / -iname ...`) — it's slow and there are usually multiple stale/vendored copies
of these headers scattered across unrelated project checkouts on a dev machine, which is noise.
On WSL, the Windows install is also reachable at `/mnt/c/Program Files/XMOS/XTC/<version>/`; there
may additionally be a separate native WSL install (e.g. under `~/XMOS/XTC/<version>/`) — after
sourcing the tools' `SetEnv`, `$XMOS_TOOL_PATH` tells you which one is actually active rather than
guessing.

## Libraries and CMake build system

- `XMOS_CMAKE_PATH` points at the XCommon CMake support files:
  `<XMOS_TOOL_PATH>/build/xcommon_cmake`. See
  [`xmos-build-system`](../xmos-build-system/SKILL.md) for how this is used.
- To locate the library dependency sources a build uses, see
  [locating dependency sources](../xmos-build-system/SKILL.md#locating-dependency-sources).

## Environment variables that affect compiler search paths

These are set by the XTC Tools environment activation and read by `xcc`; only override them if you
have a specific reason to (e.g. an unusual out-of-tree header location):

| Variable | Purpose |
|---|---|
| `XCC_C_INCLUDE_PATH` | Extra include search path for C. |
| `XCC_CPLUS_INCLUDE_PATH` | Extra include search path for C++. |
| `XCC_XC_INCLUDE_PATH` | Extra include search path for XC. |
| `XCC_LIBRARY_PATH` | Extra library search path (for `-l`). |
| `XCC_DEVICE_PATH` | Search path for device/target (`.xn`) description files. |
| `XCC_TARGET_PATH` | Search path used to resolve `-target=<name>`. |
| `XCC_DEFAULT_TARGET` | Default target platform if `-target`/an `.xn` file is not given. |
| `XCC_EXEC_PREFIX` | Location of the compiler's internal executables/passes. |

Path-list variables use `;` as a separator on Windows and `:` on macOS/Linux, matching each OS's
native `PATH` convention.

## Verifying paths quickly

```sh
xcc --version                 # confirms environment is active at all
echo %XMOS_TOOL_PATH%         # Windows
echo $XMOS_TOOL_PATH          # macOS/Linux
```

Then list `<XMOS_TOOL_PATH>/target/include` to confirm headers are present, rather than assuming a
fixed path across machines/OSes.
