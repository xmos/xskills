# XMOS Agent Guidance

This file provides core guidance for AI coding agents working on XMOS embedded software.
Task-specific guidance lives in [`skills/`](./skills/). Read the relevant `SKILL.md` files
and supporting references as needed; see the index below. Compatible coding tools can
discover installed skills and load their instructions on demand. The maintenance
instructions apply when modifying xskills itself.

## Scope and audience

This guidance targets **XMOS XTC Tools 15.3.1** and the **XS3 architecture** (XCORE.AI and other
XS3-based devices). It is written for use both inside XMOS and by external customers, and is
intentionally tool-neutral: it does not assume VS Code, Copilot, or any specific editor.

Apply the embedded-development principles only to XMOS software tasks, even when this file
is loaded globally. Language and architecture recommendations apply to new development within
the stated compatibility scope. When maintaining existing implementations, preserve established
APIs, supported targets and legacy conventions unless migration is requested. Environment setup
and verification requirements also apply to maintenance work.

## Core principles

1. **C over XC.** New code should be written in C using `lib_xcore`, not the XC language, unless a
   task specifically requires an XC-only feature. See
   [`xmos-c-programming`](./skills/xmos-c-programming/SKILL.md).
2. **No dynamic memory.** Do not use `malloc`/`free`/`new` in embedded application code. Use static
   or stack allocation with tool-calculated stack sizes. See
   [`xmos-embedded-c-practices`](./skills/xmos-embedded-c-practices/SKILL.md).
3. **Ensure the XTC Tools environment is active before building, running or debugging.** Check
   the selected toolchain in the executing shell; environment persistence between agent calls
   depends on the harness. Activate it when absent. On Windows, use the `scripts/xtc.ps1` wrapper in
   [`xmos-environment-setup`](./skills/xmos-environment-setup/SKILL.md).
4. **Always use a Python virtual environment** for any Python tooling in an XMOS sandbox (dependency
   management, build scripts, CI helpers). Never install Python packages into the system/global
   interpreter. See [`xmos-project-structure`](./skills/xmos-project-structure/SKILL.md).
5. **Distinguish simulated cycles from host elapsed time.** `xsim` is near cycle-accurate and
   supports instruction/cycle analysis; its wall-clock runtime is not target execution time.
   Validate real peripheral timing and end-to-end hardware behaviour on hardware (`xrun`). See
   [`xmos-run-and-simulate`](./skills/xmos-run-and-simulate/SKILL.md).
6. **Prefer xSCOPE over JTAG `--io` for logging.** `xrun --io` halts all logical cores on a tile per
   transfer and has no buffering; `xrun --xscope` does not. See
   [`xmos-debugging-profiling`](./skills/xmos-debugging-profiling/SKILL.md).
7. **Cite the source.** When giving XMOS-specific guidance, prefer information verified in the XTC
   Tools 15.3 documentation or the XS3 architecture manual over general embedded knowledge. If
   something cannot be verified from a skill or the docs, say so rather than guessing.

## Using the guidance

- Identify relevant skills from their descriptions and read their `SKILL.md` instructions and
  supporting references as needed. Discovery and installation behaviour varies by coding tool.
- Check the project's README, documentation, examples and build configuration for supported
  architectures, devices and toolchain versions before applying a recommendation.
- Look for existing XMOS libraries and examples before implementing equivalent functionality.
  Use [capability discovery](./skills/xmos-capability-discovery/SKILL.md) to find and verify candidates.
  Prefer supported implementations for new development; only recommend a successor when confirmed.
- Repository-specific hardware, compatibility and legacy requirements take precedence over general
  recommendations here. Do not assume internal XMOS repositories or tools are accessible.

## Repository integration

Library repositories can reference this central guidance from their own `AGENTS.md` files.
Use `main` for the latest approved xskills release, or an immutable release tag to pin a baseline.
The first approved release must be available there before rolling out those references to customers.

A link alone does not install or load skills. Use an accessible installed copy, or retrieve
the central instructions and relevant skill resources from the referenced release. State when
guidance cannot be accessed and continue using the project's own documentation.

## Maintaining xskills

- Follow [`xmos-skill-authoring`](./skills/xmos-skill-authoring/SKILL.md) when changing skills.
  Keep detailed workflows in skills and core instructions concise.
- Keep the README and skill index consistent when adding, removing or renaming skills.
- Run the repository validation suite described in [`README.rst`](./README.rst); verify changed
  commands, examples and scripts as appropriate, and state what was actually checked.
- Use a Python virtual environment for repository tooling. Do not include confidential or
  customer-specific content; state access requirements for workflows using internal resources.

## Skills index

Use the descriptions below to identify relevant skills. You do not need to read every
skill before beginning work. Automatic discovery and loading depend on your coding tool
and installation.

| Skill | Use when... |
|---|---|
| [`xmos-capability-discovery`](./skills/xmos-capability-discovery/SKILL.md) | Finding existing XMOS libraries, reference applications and examples; verifying capability, version and device compatibility through accessible official sources. |
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
