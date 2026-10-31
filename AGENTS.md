# XMOS Agent Guidance

This file is the entrypoint for AI coding agents (GitHub Copilot, Claude, Cursor, or any
`AGENTS.md`-aware tool) working in an XMOS XCORE / XS3 codebase. It applies to every task in this
repository. Deeper, task-specific guidance lives in [`skills/`](./skills/) and is
loaded on demand — see the index below.

## Scope and audience

This guidance targets **XMOS XTC Tools 15.3.1** and the **XS3 architecture** (XCORE.AI and other
XS3-based devices). It is written for use both inside XMOS and by external customers, and is
intentionally tool-neutral: it does not assume VS Code, Copilot, or any specific editor.

## Core principles

1. **C over XC.** New code should be written in C using `lib_xcore`, not the XC language, unless a
   task specifically requires an XC-only feature. See
   [`xmos-c-programming`](./skills/xmos-c-programming/SKILL.md).
2. **No dynamic memory.** Do not use `malloc`/`free`/`new` in embedded application code. Use static
   or stack allocation with tool-calculated stack sizes. See
   [`xmos-embedded-c-practices`](./skills/xmos-embedded-c-practices/SKILL.md).
3. **Always activate the XTC Tools environment before building or running.** Commands like `xcc`,
   `xrun`, `xsim`, `xgdb` only work once the XTC environment is active, and each new agent shell
   starts without it. On Windows, prefix the command with the `scripts/xtc.ps1` wrapper in
   [`xmos-environment-setup`](./skills/xmos-environment-setup/SKILL.md).
4. **Always use a Python virtual environment** for any Python tooling in an XMOS sandbox (dependency
   management, build scripts, CI helpers). Never install Python packages into the system/global
   interpreter. See [`xmos-project-structure`](./skills/xmos-project-structure/SKILL.md).
5. **`xsim` is not real-time.** The simulator is cycle-accurate but runs slower than real hardware.
   Do not use it for timing/performance validation — use real hardware (`xrun`) for that. See
   [`xmos-run-and-simulate`](./skills/xmos-run-and-simulate/SKILL.md).
6. **Prefer xSCOPE over JTAG `--io` for logging.** `xrun --io` halts all logical cores on a tile per
   transfer and has no buffering; `xrun --xscope` does not. See
   [`xmos-debugging-profiling`](./skills/xmos-debugging-profiling/SKILL.md).
7. **Cite the source.** When giving XMOS-specific guidance, prefer information verified in the XTC
   Tools 15.3 documentation or the XS3 architecture manual over general embedded knowledge. If
   something cannot be verified from a skill or the docs, say so rather than guessing.

## Skills index

Skills are loaded on demand by keyword match against their `description`. You do not need to read
all of them up front — the list below is so you know what exists.

| Skill | Use when... |
|---|---|
| [`xmos-environment-setup`](./skills/xmos-environment-setup/SKILL.md) | Read before running any XTC Tools command or XCommon CMake build: activating the environment (one-command `scripts/xtc.ps1` wrapper for PowerShell), or diagnosing "command not found" for `xcc`/`xrun`/`xsim`. |
| [`xmos-toolchain-paths`](./skills/xmos-toolchain-paths/SKILL.md) | Locating XMOS headers, libraries, or the CMake build system on disk; resolving `#include` errors for `xcore/*.h`, `xs1.h`, `platform.h`. |
| [`xmos-build-system`](./skills/xmos-build-system/SKILL.md) | Building an XMOS application from the command line, with XCommon CMake or with `xcc` directly. |
| [`xmos-run-and-simulate`](./skills/xmos-run-and-simulate/SKILL.md) | Running a `.xe` on hardware with `xrun`, or in the simulator with `xsim`; understanding simulation speed and tracing. |
| [`xmos-flashing`](./skills/xmos-flashing/SKILL.md) | Writing a `.xe` to non-volatile flash with `xflash` so it boots standalone; factory/upgrade images; choosing `xrun` (RAM, temporary) vs `xflash` (flash, persistent). |
| [`xmos-debugging-profiling`](./skills/xmos-debugging-profiling/SKILL.md) | Debugging with `xgdb`, profiling with `xgprof`/`xsim --gprof`, or fast "printf debugging" with xSCOPE. |
| [`xmos-vscode-extension`](./skills/xmos-vscode-extension/SKILL.md) | Using the XMOS XTC Tools VS Code extension (build/run/debug/flash buttons, tasks.json, launch.json, IntelliSense). |
| [`xmos-xs3-architecture`](./skills/xmos-xs3-architecture/SKILL.md) | Reasoning about XS3 hardware concepts: tiles, hardware threads, channels, ports, timers, locks, events/interrupts, memory model. |
| [`xmos-c-programming`](./skills/xmos-c-programming/SKILL.md) | Writing multicore XMOS C code with `lib_xcore`: parallel tasks, channels, ports, timers, `select`. |
| [`xmos-multi-tile-architecture`](./skills/xmos-multi-tile-architecture/SKILL.md) | Structuring a multi-tile application: placing entry-points on `tile[N]`, passing chanends between tiles, writing the top-level multi-tile XC file, `.xn` hardware targets. |
| [`xmos-clock-domains`](./skills/xmos-clock-domains/SKILL.md) | Understanding xcore.ai clock domains (System/Secondary PLL, reference/switch/tile clocks), changing frequencies via the XN file or PLL registers, or diagnosing timing measurements after a clock change. |
| [`xmos-embedded-c-practices`](./skills/xmos-embedded-c-practices/SKILL.md) | Writing or reviewing embedded C for correctness/safety: no malloc, stack sizing, no unbounded recursion. |
| [`xmos-project-structure`](./skills/xmos-project-structure/SKILL.md) | Setting up or navigating an XMOS sandbox/repo layout; setting up a Python venv for tooling. |
| [`xmos-library-repo-style`](./skills/xmos-library-repo-style/SKILL.md) | Creating/editing files in an XMOS library-style repo (`lib_*`): copyright headers, LICENSE, `settings.yml`, README.rst structure/metadata, CHANGELOG.rst format, version consistency, `doc/rst/` structure, dependency version pinning. |
| [`xmos-internal-repo-checks`](./skills/xmos-internal-repo-checks/SKILL.md) | Diagnosing and fixing `test_repo_checks` failures using XMOS internal `infr_apps` scripts; requires access to that repository and its Python tooling. |
| [`xmos-skill-authoring`](./skills/xmos-skill-authoring/SKILL.md) | Adding a new skill or instruction to this repository, e.g. after learning something new from XMOS docs. |

## Repository layout

```text
xskills/
├─ AGENTS.md                          # this file
├─ README.rst                         # what this is, how to adopt it in another repo
├─ CLAUDE.md                          # pointer to this file, for Claude
├─ .github/copilot-instructions.md    # pointer to this file, for Copilot
├─ .cursor/rules/xmos.mdc             # pointer to this file, for Cursor
└─ skills/
   └─ <name>/SKILL.md                 # on-demand workflow skills (see index above)
```
