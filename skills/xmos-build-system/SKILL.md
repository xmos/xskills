---
name: xmos-build-system
description: Use when building or rebuilding an XMOS application from the command line for any reason — including rebuilding after a code edit to check warnings/errors or verify a fix — setting up a CMakeLists.txt or lib_build_info.cmake for an XMOS project, choosing between XCommon CMake and a direct xcc invocation, configuring APP_DEPENDENT_MODULES/LIB_DEPENDENT_MODULES dependency versions, reading the sandbox manifest.txt, or diagnosing build errors like missing .xn target files, "-report" stack/memory warnings, or a plain `cmake --build`/`make` invocation failing with "execution of make failed" (XCommon CMake projects build via `xmake -C build <target>`, not a raw CMake build invocation), or a suspected stale build cache (e.g. after changing options or branches), or slow builds where `xmake -j` doesn't help on Windows. Covers XTC Tools 15.3.1 XCommon CMake.
---

# XMOS build system

XTC Tools 15.3.1 uses **XCommon CMake** as its standard build system for real applications. Direct
`xcc` invocation is only appropriate for small, single-file examples.

Requires the XTC Tools environment to be active — see
[`xmos-environment-setup`](../xmos-environment-setup/SKILL.md).

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

### Key application variables

| Variable | Required? | Purpose |
|---|---|---|
| `APP_HW_TARGET` | Required (unless doing a native/host build) | Target board name (e.g. `XCORE-AI-EXPLORER`) or an `.xn` file — just the filename is needed; child directories are searched for it. |
| `XMOS_SANDBOX_DIR` | Required if `APP_DEPENDENT_MODULES` is non-empty | Path to the sandbox root, conventionally `${CMAKE_CURRENT_LIST_DIR}/../..`. See [`xmos-project-structure`](../xmos-project-structure/SKILL.md). |
| `APP_DEPENDENT_MODULES` | Optional | This app's **direct** dependencies only (sub-dependencies are pulled in automatically from each module's own `LIB_DEPENDENT_MODULES`). Must be quoted — see "Dependency version format" below. |
| `APP_C_SRCS` / `APP_XC_SRCS` / `APP_CXX_SRCS` / `APP_ASM_SRCS` | Optional | Explicit source file lists. If unset, all matching files under `src/` (recursively) are compiled automatically; set to `""` to compile none of that language. |
| `APP_COMPILER_FLAGS` | Optional | Flags for all sources, e.g. `-g` (needed by `xgdb` — see [`xmos-debugging-profiling`](../xmos-debugging-profiling/SKILL.md)), `-O3`, `-DMY_DEF=123`. Also settable per-config (`APP_COMPILER_FLAGS_<config>`) or per-file (`APP_COMPILER_FLAGS_<filename>`). |
| `APP_INCLUDES` | Optional | Extra include directories. |
| `APP_DEPENDENT_ARCHIVES` | Optional | Static-library archives to link (the static lib must also be listed in `APP_DEPENDENT_MODULES`). |
| `APP_XSCOPE_SRCS` | Optional | `.xscope` config files (auto-discovered under `src/` if unset) — see [`xmos-debugging-profiling`](../xmos-debugging-profiling/SKILL.md). |
| `APP_PCA_ENABLE` | Optional | Enables Pre-Compilation Analysis (whole-program optimization, XC sources only). Default `OFF`. |
| `XMOS_DEP_DIR_<module>` | Optional | Overrides where a specific dependency is found on disk instead of the sandbox root — useful for pointing at a local working copy. |

Some boards are known to the tools under more than one `APP_HW_TARGET` name. For example
`XCORE-AI-EXPLORER` and `XK-EVK-XU316` are two separate `.xn` files shipped under
`<XMOS_TOOL_PATH>/targets/`, but describe the electrically identical board (same tile/port/JTAG
topology, confirmed by diffing the two `.xn` files) — either name builds and runs correctly on a
physical XK-EVK-XU316 (e.g. `lib_board_support`'s own `app_evk_316_simple_c` example targets
`XCORE-AI-EXPLORER` specifically because that's the name this exact board shipped under). Don't
assume a board-name mismatch between two working examples targeting "the same board" is a bug —
check the actual `.xn` contents (or just try running the `.xe` on the board) before concluding they
target different hardware.

### Multi-app directories: aggregator `CMakeLists.txt` + shared `deps.cmake`

A `sw_*` repo with several `app_*` variants (e.g. one per hardware board) commonly has a thin
top-level `CMakeLists.txt` that just aggregates them with plain CMake `add_subdirectory()` — it has
no `APP_HW_TARGET`/`XMOS_REGISTER_APP()` of its own, since each `app_*` subdirectory is its own real
build entry point. This same aggregator pattern is equally common for a `lib_*` repo's own
`examples/` and `tests/` directories (e.g. `lib_i2c/examples/CMakeLists.txt` and
`lib_xua/examples/CMakeLists.txt` both just `add_subdirectory()` each example/test app and share a
sibling `deps.cmake`) — it isn't limited to `sw_*` repos, since a library's examples/tests are
themselves standalone apps, not the library module itself:

```cmake
# sw_example/CMakeLists.txt - configures every app variant in one `cmake` invocation
cmake_minimum_required(VERSION 3.21)
include($ENV{XMOS_CMAKE_PATH}/xcommon.cmake)
project(sw_example)

add_subdirectory(app_example_board_a)
add_subdirectory(app_example_board_b)
```

When every variant shares the same dependencies, factor `APP_DEPENDENT_MODULES` into a single
`deps.cmake` next to the app directories and `include()` it from each `app_*/CMakeLists.txt`
(alongside that app's own `APP_HW_TARGET`/`XMOS_REGISTER_APP()`), instead of repeating the
dependency list in every app:

```cmake
# sw_example/deps.cmake
set(APP_DEPENDENT_MODULES "lib_foo(1.2.0)" "lib_bar(3.0.0)")
```

```cmake
# sw_example/app_example_board_a/CMakeLists.txt
cmake_minimum_required(VERSION 3.21)
include($ENV{XMOS_CMAKE_PATH}/xcommon.cmake)

set(XMOS_SANDBOX_DIR ${CMAKE_CURRENT_LIST_DIR}/../..)
include(${CMAKE_CURRENT_LIST_DIR}/../deps.cmake)
set(APP_COMPILER_FLAGS -O3 -g -Wall)

project(app_example_board_a)
set(APP_HW_TARGET board_a.xn)

XMOS_REGISTER_APP()
```

You can then run `cmake -B build` / `xmake -C build` once from the `sw_*` root to build every app
variant, or `cd` into a single `app_*` directory to configure/build just that one.

#### `deps.cmake` fetching a non-standalone dependency via plain CMake `FetchContent`

Not every dependency a `deps.cmake` needs is itself a standalone `lib_*` repo resolvable through
`APP_DEPENDENT_MODULES`'s normal name/version mechanism. `lib_mic_array`'s `examples/deps.cmake` is
a real example: its `i2s`/`i2c` modules only exist inside a separate monorepo (`fwk_io`), not as
their own `lib_i2s`/`lib_i2c` checkouts, so it fetches that monorepo directly with plain CMake
`FetchContent` (using a `git@github.com:...` SSH URL, not the `lib_name(version)` string format)
into the sandbox root, then points `XMOS_DEP_DIR_i2s`/`XMOS_DEP_DIR_i2c` at subdirectories inside it:

```cmake
set(XMOS_DEP_DIR_i2s ${XMOS_SANDBOX_DIR}/fwk_io/modules)
set(XMOS_DEP_DIR_i2c ${XMOS_SANDBOX_DIR}/fwk_io/modules)
if(NOT EXISTS ${XMOS_SANDBOX_DIR}/fwk_io)
    include(FetchContent)
    FetchContent_Declare(fwk_io GIT_REPOSITORY git@github.com:xmos/fwk_io GIT_TAG feature/xcommon_cmake
                          SOURCE_DIR ${XMOS_SANDBOX_DIR}/fwk_io)
    FetchContent_Populate(fwk_io)
endif()
set(APP_DEPENDENT_MODULES "lib_mic_array" "i2s" "i2c")
```

If you see a raw `FetchContent_Declare`/`FetchContent_Populate` block in a `deps.cmake` (rather than
just a version string in `APP_DEPENDENT_MODULES`), this is why — it's fetching a shared repo that
one of the listed modules lives inside, and `XMOS_DEP_DIR_<module>` is what actually redirects that
module's resolution into the fetched checkout. This requires working `git` SSH access to the target
host; on a first configure it clones into the sandbox root exactly like a normal dependency (visible
in `build/manifest.txt`).

### Modules (`lib_build_info.cmake`)

A library module (`lib_*`) has no `CMakeLists.txt` of its own — it's never the build entry point.
Instead it provides `lib_build_info.cmake`, included by anything that depends on it:

```cmake
set(LIB_NAME lib_foo)
set(LIB_VERSION 3.2.1)
set(LIB_INCLUDES api)
set(LIB_COMPILER_FLAGS -Os)
set(LIB_DEPENDENT_MODULES "lib_bar")     # or "" (quoted empty string) if no dependencies

XMOS_REGISTER_MODULE()
```

`LIB_NAME`, `LIB_VERSION`, and `LIB_DEPENDENT_MODULES` are required (the last must still be set,
even if empty). Source-file and compiler-flag variables mirror the `APP_*` ones above but prefixed
`LIB_` (`LIB_C_SRCS`, `LIB_COMPILER_FLAGS_<filename>`, etc.), scanning `src/` by default. Every
module also gets an automatic optional header `<name-without-lib_>_conf.h` for app-side
configuration overrides, without needing to list it in `LIB_OPTIONAL_HEADERS`.

### Static libraries (prebuilt archive + optional source)

A static-library repo (also `lib_*` by convention) provides its own `lib_build_info.cmake` using
`LIB_ARCHIVE_*`-prefixed variables (`LIB_ARCHIVE_C_SRCS`, `LIB_ARCHIVE_COMPILER_FLAGS`,
`LIB_ARCHIVE_DEPENDENT_MODULES`, `LIB_ARCHIVE_ARCHS` — default `xs3a`) and calls
`XMOS_REGISTER_STATIC_LIB()`. If the repo also ships source to rebuild the archive itself, it adds
a `CMakeLists.txt` with the same 3-line header plus `XMOS_SANDBOX_DIR` and
`include(lib_build_info.cmake)`, so the same variables serve both "rebuild the archive" and "link
the archive into an app" workflows.

### Dependency version format

Values in `APP_DEPENDENT_MODULES`/`LIB_DEPENDENT_MODULES` are always quoted strings (they contain
parentheses). The common external form is a name plus a released version:

```cmake
set(APP_DEPENDENT_MODULES "lib_i2c(6.1.1)")   # clones github.com/xmos/lib_i2c, checks out tag v6.1.1
```

Internal-development variants let you override location and/or version independently:
`lib_abc` (default location, default branch head), `myuser/lib_abc` (different GitHub org/user),
`othergitserver.com:myuser/lib_abc` (SSH to another server), `https://othergitserver.com/myuser/lib_abc`
(plain HTTPS), each optionally combined with a version suffix — `(v1.2.3)` (tag), `(develop)`
(branch head), or `(4fa35fe)` (commit hash). Dependencies are cloned once into the sandbox root and
never modified automatically after that; to move a dependency to a different version, `git checkout`
it manually inside the sandbox and re-run `cmake`. If `cmake` reports a version mismatch for an
already-cloned dependency, run `git -C <sandbox>/<lib_name> fetch && git -C <sandbox>/<lib_name>
checkout <tag>` then re-run `cmake`.

### Sandbox manifest

Every `cmake` configure run writes `build/manifest.txt` listing, for the app and every resolved
dependency: name, git remote location, branch/tag, and commit hash (add `-D FULL_MANIFEST=TRUE` to
also show each dependency's own sub-dependencies). Use this to see exactly which dependency
versions a given build actually used.

XCommon CMake resolves its own support files via `XMOS_CMAKE_PATH`
(`<XMOS_TOOL_PATH>/build/xcommon_cmake` — see
[`xmos-toolchain-paths`](../xmos-toolchain-paths/SKILL.md)) and caches fetched library dependencies
under `XMOS_HOME`. The full XCommon CMake reference lives at
<https://www.xmos.com/documentation/XM-015090-PC/html/> (a separate documentation site from the XTC
Tools manual); consult it directly for variables not covered here rather than guessing at their
names.

A worked example using XCommon CMake ships with the tools under
`<XMOS_TOOL_PATH>/examples/ExampleXCommonCMake` (see its own `README` for exact steps). Copy it to a
directory you have write permission to before building — you normally can't write under the tools
install directory itself.

## Direct `xcc` invocation (small examples only)

For a quick one-off program with no library dependencies, you can skip CMake entirely:

```sh
xcc -target=<platform.xn> file1.c file2.xc -o a.xe
```

This does not scale to multi-file/multi-library applications — use XCommon CMake for anything
beyond a quick example.

## Key `xcc` flags worth knowing

| Flag | Purpose |
|---|---|
| `-g` | Emit debug info (needed for `xgdb` source-level debugging). |
| `-O0`…`-O3`, `-Os` | Optimization level (`-O0` is the default). |
| `-report` | Prints a per-tile breakdown of stack, code, and data memory usage. Use this to check stack sizing rather than guessing — see [`xmos-c-programming`](../xmos-c-programming/SKILL.md) on why stack size is statically calculated on XCORE. |
| `-target=<platform>` or a `.xn` file as an input | Selects the target hardware platform. Prefer passing an explicit `.xn` file as a build input over `-target=` for any project expected to live for a while, since it is more explicit and reproducible. |
| `-Wall`, `-Werror` | Standard warning controls. |
| `-fxscope[=link]` | Enables xSCOPE without a separate `.xscope` config file — see [`xmos-debugging-profiling`](../xmos-debugging-profiling/SKILL.md). |
| `-mcmodel=small\|large\|hybrid` | Selects the memory model (per source file); `small` (default) is most efficient but requires a tile's static data to fit in one contiguous 256KB region; switch to `hybrid`/`large` only if the linker reports a size/range error — see [`xmos-c-programming`](../xmos-c-programming/SKILL.md) for the full explanation. |

## Suspected stale build cache: delete the build directory

CMake caches configure-time decisions in the build directory (`CMakeCache.txt`, generated sources,
fetched/generated tables), and changing options, dependency versions or branches does not always
invalidate them. If a build fails in a way that suggests stale cached state — for example
undefined references to symbols that should be generated or provided by a dependency, or a setting change that
seems to have no effect — delete the build directory and configure and build again from scratch:

```sh
rm -rf build            # PowerShell: Remove-Item -Recurse -Force build
cmake -G "Unix Makefiles" -B build
xmake -C build
```

Do this before investigating which cache variable is stale, and don't work around it by switching
to a different build directory; a clean reconfigure is quicker and settles the question.

## After building

A `.xe` file is not a single binary — it's a package containing one ELF file per tile in the target
(this is why `xobjdump -s` splits it into per-tile ELFs, e.g. for `xgprof`; see
[`xmos-debugging-profiling`](../xmos-debugging-profiling/SKILL.md)).

- Run on hardware or in the simulator — see
  [`xmos-run-and-simulate`](../xmos-run-and-simulate/SKILL.md).
- Debug or profile — see [`xmos-debugging-profiling`](../xmos-debugging-profiling/SKILL.md).
- If using VS Code, the XTC Tools extension can drive this same build system through its Build
  button/tasks — see [`xmos-vscode-extension`](../xmos-vscode-extension/SKILL.md).
