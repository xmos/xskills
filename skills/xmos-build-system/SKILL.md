---
name: xmos-build-system
description: Use when building or rebuilding XMOS software, selecting or identifying its build system (recommended XCommon CMake, legacy Make-based XCommon or Waf-based xwaf), setting up CMakeLists.txt or lib_build_info.cmake, configuring dependency versions, reading manifest.txt, or diagnosing target, stack/memory, build-driver or stale-cache errors. Includes direct xcc for small examples. Covers XTC Tools 15.3.1 XCommon CMake; follow repository documentation for legacy workflows.
---

# XMOS build system

**Prefer XCommon CMake for new XMOS projects and new build-system work.** It is
CMake-based and is the recommended default. Use another system only for a concrete
compatibility or project requirement. Direct `xcc` invocation is useful for small,
standalone examples.

Requires the XTC Tools environment to be active — see
[`xmos-environment-setup`](../xmos-environment-setup/SKILL.md).

## Identify the project's build system

Existing repositories may use legacy **Make-based XCommon** or **Waf-based xwaf**.
Read the repository's README, build files and CI before selecting commands:

| System | Typical indicators |
|---|---|
| XCommon CMake | `CMakeLists.txt` including `xcommon.cmake`; `lib_build_info.cmake` module metadata |
| Legacy XCommon | Makefiles including the XCommon build infrastructure; `module_build_info` metadata |
| xwaf | `wscript` files and repository instructions invoking `xwaf` |

These are clues, not definitive tests: a repository may contain multiple build systems
or a generic CMake/Make/Waf project unrelated to the corresponding XMOS framework.
The use of `xmake` alone does not distinguish the two XCommon systems; XCommon CMake
also uses generated Makefiles in the workflow below.

During maintenance, follow the established build workflow and preserve supported
toolchain/dependency versions. Keeping a working legacy build for an unrelated fix
is a valid compatibility reason; do not migrate it automatically. For a requested
migration, prefer XCommon CMake and verify equivalent targets, options, dependencies
and tests. Use the repository's documented commands for legacy XCommon or xwaf rather
than applying the CMake-specific commands and variables below to them. Run any xwaf
Python tooling in a compatible virtual environment.

## XCommon CMake (preferred for real projects)

Typical workflow, e.g. building one of the example apps shipped with the tools:

```sh
# Work in a writable directory - do not build in-place under the tools install directory.
cmake -G "Unix Makefiles" -B build
xmake -C build
```

This produces the built `.xe` executable(s) under `bin/` (per-application, per-configuration).
`xmake` is a bundled build of GNU Make, provided for convenience. To build/rebuild only one
application in a multi-app sandbox, pass its target name: `xmake -C build <app_name>` (e.g.
`xmake -C build app_lovo`). Plain CMake driver invocations like `cmake --build build --target
<app_name>` do not work here and fail with `CMake Error: Generator: execution of make failed` —
always drive the build through `xmake`, not `cmake --build`.

On Windows, `xmake -j` does not speed up an `xcc` build: compiles still run one at a time however
many jobs are requested. When several independent builds are needed (other targets, other
configurations, a native build in WSL), run them side by side as separate processes instead of
queueing them behind one another.

### Minimal application `CMakeLists.txt`

Every application/static-library `CMakeLists.txt` needs the same three-line header, then sets
variables, then registers itself:

```cmake
cmake_minimum_required(VERSION 3.21)
include($ENV{XMOS_CMAKE_PATH}/xcommon.cmake)
project(app_example)

set(XMOS_SANDBOX_DIR ${CMAKE_CURRENT_LIST_DIR}/../..)   # only needed if there are dependencies
set(APP_HW_TARGET XCORE-AI-EXPLORER)                    # or a local .xn file, e.g. xk-316-mc.xn
set(APP_COMPILER_FLAGS -g -O3 -Wall)
set(APP_DEPENDENT_MODULES "lib_i2c(6.1.1)" "lib_i2s(5.0.0)")   # quoted - contains parentheses

XMOS_REGISTER_APP()
```

`XMOS_REGISTER_APP()` must be called last (after every variable it uses is set); it defines the
build targets, fetches missing dependencies into the sandbox, and populates the sandbox manifest.
`project()` must appear after the `include(xcommon.cmake)` line, but `set()` calls for `APP_*`
variables may appear before or after `project()` — the only hard requirement is that they all
precede `XMOS_REGISTER_APP()`.

Keep the target the project specifies. `XCORE-AI-EXPLORER` and `XK-EVK-XU316` are target names for
the same board.

### Variables, modules and dependencies

Consult the [XCommon CMake documentation](https://www.xmos.com/documentation/XM-015090-PC/html/)
matching the project's version for application, module (`lib_build_info.cmake`) and static-library
variables, multi-application layouts, dependency version syntax and resolution, and configuration
options. Inspect the repository's existing build files before adding settings, and follow its
established patterns (for example a shared `deps.cmake`, or a raw `FetchContent` block for a
dependency that lives inside another repository). Do not guess variable names or copy defaults
from another version.

Dependency entries are quoted strings because they contain parentheses, e.g.
`"lib_i2c(6.1.1)"`. Pin exact versions for library repositories as described in
[dependency version pinning](../xmos-library-repo-style/SKILL.md#dependency-version-pinning).

### Multiple applications: share one `deps.cmake`

Applications built in the same sandbox share its dependency checkouts, so they must all use the
exact same dependency list and versions. When a repository has several applications (e.g. `app_*`
variants, or a library's `examples/` and `tests/`), define `APP_DEPENDENT_MODULES` once in a
shared `deps.cmake` and `include()` it from each application's `CMakeLists.txt`, rather than
repeating the list. This keeps the versions identical by construction:

```cmake
# deps.cmake (next to the app directories)
set(APP_DEPENDENT_MODULES "lib_foo(1.2.0)" "lib_bar(3.0.0)")
```

```cmake
# app_example_board_a/CMakeLists.txt
cmake_minimum_required(VERSION 3.21)
include($ENV{XMOS_CMAKE_PATH}/xcommon.cmake)
project(app_example_board_a)

set(XMOS_SANDBOX_DIR ${CMAKE_CURRENT_LIST_DIR}/../..)
include(${CMAKE_CURRENT_LIST_DIR}/../deps.cmake)
set(APP_HW_TARGET board_a.xn)

XMOS_REGISTER_APP()
```

If a repository already has a `deps.cmake`, add or change dependencies there, not in individual
applications. A top-level `CMakeLists.txt` that calls `add_subdirectory()` for each application
lets one configure build them all.

### Non-standard dependencies

Not every dependency is a standalone `lib_*` repository fetched by name. A module may live inside
a larger repository; an existing `deps.cmake` may then fetch that repository with CMake
`FetchContent` and set `XMOS_DEP_DIR_<module>` so the module resolves inside it. In XTC 15.3.1's
XCommon CMake, `XMOS_DEP_DIR_<module>` names the directory containing the module's own
directory, i.e. `<dir>/<module>/lib_build_info.cmake`:

```cmake
# deps.cmake: modules i2c and i2s live under <sandbox>/fwk_io/modules/
set(XMOS_DEP_DIR_i2c ${XMOS_SANDBOX_DIR}/fwk_io/modules)
set(XMOS_DEP_DIR_i2s ${XMOS_SANDBOX_DIR}/fwk_io/modules)
if(NOT EXISTS ${XMOS_SANDBOX_DIR}/fwk_io)
    include(FetchContent)
    FetchContent_Declare(fwk_io
        GIT_REPOSITORY https://github.com/xmos/fwk_io
        GIT_TAG <pinned release tag or commit>
        SOURCE_DIR ${XMOS_SANDBOX_DIR}/fwk_io)
    FetchContent_Populate(fwk_io)
endif()
set(APP_DEPENDENT_MODULES "lib_mic_array(<version>)" "i2c" "i2s")
```

Preserve such arrangements when maintaining a repository, and change them in the shared
`deps.cmake`. When adding one, pin an accessible release or commit rather than a branch, and
confirm the override semantics for the project's XCommon CMake version.

### Modules and static libraries

- **Source module:** a `lib_*` repository provides `lib_build_info.cmake` calling
  `XMOS_REGISTER_MODULE()`; its sources are compiled into each consuming application.
- **Prebuilt static library:** `lib_build_info.cmake` describes the archive using `LIB_ARCHIVE_*`
  variables and calls `XMOS_REGISTER_STATIC_LIB()`; consuming applications link the archive.
- **Archive rebuild:** a static-library repository that ships source may also have its own
  `CMakeLists.txt` that includes `lib_build_info.cmake` to rebuild the archive. That is a build
  entry point, unlike a source module.

See the XCommon CMake documentation for the module, archive and architecture variables.

### Sandbox manifest

Every `cmake` configure run writes `build/manifest.txt` listing, for the app and every resolved
dependency: name, git remote location, branch/tag, and commit hash (add `-D FULL_MANIFEST=TRUE` to
also show each dependency's own sub-dependencies). Use this to see exactly which dependency
versions a given build actually used.

XCommon CMake resolves its own support files via `XMOS_CMAKE_PATH`
(`<XMOS_TOOL_PATH>/build/xcommon_cmake` — see
[`xmos-toolchain-paths`](../xmos-toolchain-paths/SKILL.md)).

### Locating dependency sources

Consult the [XCommon CMake documentation](https://www.xmos.com/documentation/XM-015090-PC/html/)
for the project's XCommon CMake version to establish dependency search locations,
checkout behaviour and overrides. Before editing a dependency, inspect the configure
output and generated `manifest.txt` to identify the sources actually used, and check
that checkout's status so local changes are not overwritten.

A worked example using XCommon CMake ships with the tools under
`<XMOS_TOOL_PATH>/examples/ExampleXCommonCMake` (see its own `README` for exact steps). Copy it to a
directory you have write permission to before building — you normally can't write under the tools
install directory itself.

## Direct `xcc` invocation (small examples only)

For a quick one-off program with no library dependencies, you can skip CMake entirely:

```sh
xcc -target=<platform.xn> file1.c file2.xc -o a.xe
```

## Key `xcc` flags worth knowing

| Flag | Purpose |
|---|---|
| `-g` | Emit debug info (needed for `xgdb` source-level debugging). |
| `-O0`…`-O3`, `-Os` | Optimization level (`-O0` is the default). |
| `-report` | Prints a per-tile breakdown of stack, code, and data memory usage. Use this to check stack sizing rather than guessing — see [`xmos-c-programming`](../xmos-c-programming/SKILL.md) on why stack size is statically calculated on XCORE. |
| `-target=<platform>` or a `.xn` file as an input | Selects the target hardware platform. Prefer passing an explicit `.xn` file as a build input over `-target=` for any project expected to live for a while, since it is more explicit and reproducible. |
| `-Wall`, `-Werror` | Standard warning controls. |
| `-fxscope[=link]` | Enables xSCOPE and its target library without a `.xscope` config file; does not redirect text I/O (`ioMode="none"`) — see [`xmos-printing-logging`](../xmos-printing-logging/SKILL.md#configure-xscope-text-io). |
| `-mcmodel=small\|large\|hybrid` | Selects the memory model (per source file); `small` (default) is most efficient but requires a tile's static data to fit in one contiguous 256KB region; switch to `hybrid`/`large` only if the linker reports a size/range error — see [`xmos-c-programming`](../xmos-c-programming/SKILL.md) for the full explanation. |

## Suspected stale build cache

CMake caches configure-time decisions in the build directory (`CMakeCache.txt`, generated sources,
fetched/generated tables), and changing options, dependency versions or branches does not always
invalidate them. Symptoms include undefined references to symbols that should be generated or
provided by a dependency, or a setting change that seems to have no effect.

1. Identify the actual build directory and record its configure options (for example from
   `CMakeCache.txt` or the command used), so the build can be reproduced.
2. Test the hypothesis with a clean configure in a separate directory, preserving the existing
   one as evidence:

   ```sh
   cmake -G "Unix Makefiles" -B build_clean <same options>
   xmake -C build_clean
   ```

3. If the clean build succeeds, the old directory was stale. Remove it only once its contents are
   confirmed to be generated and disposable, then regenerate it if the project expects that path.
4. If the clean build fails the same way, the problem is in the configuration, sources or
   dependencies, not stale cache; investigate those instead.

## After building

A `.xe` file is not a single binary — it's a package containing one ELF file per tile in the target
(this is why `xobjdump -s` splits it into per-tile ELFs, e.g. for `xgprof`; see
[`xmos-debugging-profiling`](../xmos-debugging-profiling/SKILL.md)).

- Run on hardware or in the simulator — see
  [`xmos-run-and-simulate`](../xmos-run-and-simulate/SKILL.md).
- Debug or profile — see [`xmos-debugging-profiling`](../xmos-debugging-profiling/SKILL.md).
- If using VS Code, the XTC Tools extension can drive this same build system through its Build
  button/tasks — see [`xmos-vscode-extension`](../xmos-vscode-extension/SKILL.md).
