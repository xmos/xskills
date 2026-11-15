# XMOS Agent Guidance

This file provides shared guidance for AI coding agents working on XMOS embedded
software. Task-specific instructions live in [`skills/`](./skills/); use the index
below to identify relevant guidance. The maintenance section applies when changing
xskills itself.

## Scope and audience

This guidance targets **XMOS XS3-based devices**, including XCORE.AI. Determine the
required XTC Tools version from the project's documentation and build configuration.
Do not assume that the latest installed toolchain is the required version.

The guidance is intended for both XMOS engineers and external customers. It does
not assume a particular coding agent, editor or skill-loading mechanism. Apply the
embedded-development principles only to XMOS software tasks, even when this file
is loaded globally.

## Project requirements and compatibility

Before making changes, read the project's agent instructions and README, then the
documentation, examples and build configuration relevant to the task. Establish
its supported architectures, devices, toolchains and verification requirements.

Repository-specific hardware, compatibility and legacy requirements take
precedence over general recommendations here. Preserve existing APIs, supported
targets and conventions unless migration is requested. Apply language and
architecture recommendations to new development within the stated compatibility
scope; environment setup and verification requirements also apply to maintenance.

Do not assume that internal XMOS repositories, tools or documentation are
accessible. Report material access limitations rather than presenting unverified
assumptions as established facts.

## Core principles

1. **C over XC.** Write new code in C using `lib_xcore`, not the XC language,
   unless the task requires an XC-only feature. See
   [`xmos-c-programming`](./skills/xmos-c-programming/SKILL.md).
2. **No dynamic memory.** Do not use `malloc`/`free`/`new` in embedded application
   code. Use static or stack allocation with tool-calculated stack sizes. See
   [`xmos-embedded-c-practices`](./skills/xmos-embedded-c-practices/SKILL.md).
3. **Activate the XTC Tools environment before building, running or debugging.**
   Check the selected toolchain in the executing shell; environment persistence
   between agent calls depends on the harness. Activate it when absent. On
   Windows, use the `scripts/xtc.ps1` wrapper in
   [`xmos-environment-setup`](./skills/xmos-environment-setup/SKILL.md).
4. **Use a Python virtual environment** for Python tooling in an XMOS sandbox,
   including dependency management, build scripts and CI helpers. Never install
   packages into the system/global interpreter. See
   [`xmos-project-structure`](./skills/xmos-project-structure/SKILL.md).
5. **Distinguish simulated cycles from host elapsed time.** `xsim` is near
   cycle-accurate and supports instruction/cycle analysis; its wall-clock runtime
   is not target execution time. Validate real peripheral timing and end-to-end
   hardware behaviour on hardware (`xrun`). See
   [`xmos-run-and-simulate`](./skills/xmos-run-and-simulate/SKILL.md).
6. **Prefer configured xSCOPE I/O over JTAG `--io` for logging.** JTAG debug
   transfers halt all hardware threads (logical cores) on a tile. The configured
   xSCOPE write path avoids those tile-wide halts, but still has overhead and
   bandwidth limits. See
   [`xmos-printing-logging`](./skills/xmos-printing-logging/SKILL.md).
7. **Cite the source.** Prefer authoritative XMOS documentation appropriate to
   the project's architecture and toolchain version over general embedded
   knowledge. If something cannot be verified, say so rather than guessing.

## Discovering and accessing guidance

Use the skills index below, or the descriptions of installed skills, to identify
relevant instructions. Read their `SKILL.md` files and required supporting
references before applying them. Load only guidance relevant to the task, not
every available skill.

Look for existing XMOS libraries and examples before implementing equivalent
functionality. Use
[`xmos-capability-discovery`](./skills/xmos-capability-discovery/SKILL.md) to find
and verify candidates. Prefer supported implementations for new development;
only recommend a successor when confirmed.

**Native skill installation is optional.** Use the agent's native skill-loading
mechanism when available, or read the same `SKILL.md` files directly from an
accessible local checkout or the GitHub repository. Supporting references,
examples and scripts remain part of the guidance in either case. Read the actual
contents; seeing a link, name or description is not equivalent to consulting them.

Use guidance and supporting resources from the same xskills revision. Resolve
relative links against that checkout or Git revision. If an installed skill lacks
a linked resource, retrieve it from the matching revision rather than silently
using a different version. Do not run a referenced script unless it is available
and its execution requirements are satisfied.

If relevant guidance is inaccessible, use available project documentation and
report the limitation and any material verification gaps. Do not claim that
unavailable instructions were followed or tests were run.

See [`README.rst`](./README.rst) for setup and installation options.

## Reporting guidance and verification

In the final task summary, briefly identify:

- The xskills guidance actually consulted, using file paths or skill names, and
  the revision when known.
- Which guidance was read directly and which native skills were explicitly
  invoked. Do not describe an ordinary file read as a native skill invocation.
- Verification actually performed, its results, and any material checks or
  guidance that were unavailable.

Do not claim to have consulted guidance when only its name or description was
available. This summary is self-reported provenance, not an independent audit
trail or proof that particular instructions influenced the result.

## Repository integration

Keep each consuming repository's `AGENTS.md` limited to a reference to this file,
repository-specific instructions and a short fallback for inaccessible central
guidance. Maintain shared discovery, compatibility and reporting rules here
rather than duplicating them across repositories.

Customer-facing links to `main` require approved guidance to be available there.
Do not silently substitute an unapproved development branch when a referenced
version is unavailable.

## Maintaining xskills

- Follow [`xmos-skill-authoring`](./skills/xmos-skill-authoring/SKILL.md) when
  changing skills. Keep detailed workflows in skills and shared instructions
  concise.
- Keep the README and skills index consistent when adding, removing or renaming
  skills. Preserve working links and usability through both native skill loading
  and direct file access.
- Run the repository validation suite described in [`README.rst`](./README.rst).
  Verify changed commands, examples and scripts as appropriate, and report what
  was actually checked. Use a Python virtual environment for repository tooling.
- Do not include confidential or customer-specific content. State access
  requirements for workflows that use internal resources.

## Skills index

| Skill | Use when... |
|---|---|
| [`xmos-capability-discovery`](./skills/xmos-capability-discovery/SKILL.md) | Finding existing XMOS libraries, reference applications and examples; verifying capability, version and device compatibility through accessible official sources. |
| [`xmos-environment-setup`](./skills/xmos-environment-setup/SKILL.md) | Before running any XTC Tools command or XCommon CMake build: activating the environment (one-command `scripts/xtc.ps1` wrapper for PowerShell), or diagnosing "command not found" for `xcc`/`xrun`/`xsim`. |
| [`xmos-toolchain-paths`](./skills/xmos-toolchain-paths/SKILL.md) | Locating XMOS headers, libraries or the CMake build system on disk; resolving `#include` errors for `xcore/*.h`, `xs1.h`, `platform.h`. |
| [`xmos-build-system`](./skills/xmos-build-system/SKILL.md) | Building an XMOS application from the command line, with XCommon CMake or with `xcc` directly. |
| [`xmos-run-and-simulate`](./skills/xmos-run-and-simulate/SKILL.md) | Running a `.xe` on hardware with `xrun`, or in the simulator with `xsim`; understanding simulation speed and tracing. |
| [`xmos-flashing`](./skills/xmos-flashing/SKILL.md) | Writing a `.xe` to non-volatile flash with `xflash` so it boots standalone; factory/upgrade images; choosing `xrun` (RAM, temporary) vs `xflash` (flash, persistent). |
| [`xmos-debugging-profiling`](./skills/xmos-debugging-profiling/SKILL.md) | Debugging with `xgdb`, profiling with `xgprof`/`xsim --gprof`, measuring execution time or adding structured xSCOPE probes. |
| [`xmos-printing-logging`](./skills/xmos-printing-logging/SKILL.md) | Choosing `print.h` vs `lib_logging` vs `stdio.h`, configuring per-unit diagnostics, handling buffering/interleaving or setting up xSCOPE text I/O. |
| [`xmos-vscode-extension`](./skills/xmos-vscode-extension/SKILL.md) | Using the XMOS XTC Tools VS Code extension (build/run/debug/flash buttons, tasks.json, launch.json, IntelliSense). |
| [`xmos-xs3-architecture`](./skills/xmos-xs3-architecture/SKILL.md) | Reasoning about XS3 hardware concepts: tiles, hardware threads, channels, ports, timers, locks, events/interrupts, memory model. |
| [`xmos-c-programming`](./skills/xmos-c-programming/SKILL.md) | Writing multicore XMOS C code with `lib_xcore`: parallel tasks, channels, ports, timers, `select`. |
| [`xmos-multi-tile-architecture`](./skills/xmos-multi-tile-architecture/SKILL.md) | Structuring a multi-tile application: placing entry-points on `tile[N]`, passing chanends between tiles, writing the top-level multi-tile XC file, accessing I/O on another tile, regular vs streaming channels. |
| [`xmos-clock-domains`](./skills/xmos-clock-domains/SKILL.md) | Understanding xcore.ai clock domains (System/Secondary PLL, reference/switch/tile clocks), changing frequencies via the XN file or PLL registers, or diagnosing timing measurements after a clock change. |
| [`xmos-pin-mapping`](./skills/xmos-pin-mapping/SKILL.md) | Understanding selecting I/O pins and XCORE pacakges. |
| [`xmos-real-time-programming`](./skills/xmos-real-time-programming/SKILL.md) | Understanding timers, port-clocks, real-time concurrency and combining multiple real-time tasks. |
| [`xmos-embedded-c-practices`](./skills/xmos-embedded-c-practices/SKILL.md) | Writing or reviewing embedded C for correctness/safety: no malloc, stack sizing, no unbounded recursion, VPU copies/fills. |
| [`xmos-numeric-programming`](./skills/xmos-numeric-programming/SKILL.md) | Writing or optimising numerical/DSP code: fixed-point vs floating point, `double` and 64-bit division in real-time loops, selecting `lib_xcore_math` operations. |
| [`xmos-testing`](./skills/xmos-testing/SKILL.md) | Writing or reviewing tests: `lib_unity` C unit tests, `test_support`/Pyxsim simulator testbenches, choosing host/simulator/hardware, pass/fail criteria. |
| [`xmos-project-structure`](./skills/xmos-project-structure/SKILL.md) | Setting up or navigating an XMOS sandbox/repo layout; setting up a Python venv for tooling. |
| [`xmos-library-repo-style`](./skills/xmos-library-repo-style/SKILL.md) | Creating/editing files in an XMOS library-style repo (`lib_*`): copyright headers, LICENSE, `settings.yml`, README.rst structure/metadata, CHANGELOG.rst format, version consistency, `doc/rst/` structure, dependency version pinning. |
| [`xmos-internal-repo-checks`](./skills/xmos-internal-repo-checks/SKILL.md) | Diagnosing and fixing `test_repo_checks` failures using XMOS internal `infr_apps` scripts; requires access to that repository and its Python tooling. |
| [`xmos-skill-authoring`](./skills/xmos-skill-authoring/SKILL.md) | Adding a new skill or instruction to this repository, e.g. after learning something new from XMOS docs. |

## Repository layout

```text
xskills/
|-- AGENTS.md                         # Shared agent guidance and index
|-- README.rst                        # Setup and adoption instructions
|-- CLAUDE.md                         # Claude guidance entry point
|-- manifest.json                     # Instruction/skill integration
|-- Jenkinsfile                       # CI integration
|-- tests/                            # Repository validation
|-- .github/copilot-instructions.md   # Copilot guidance entry point
|-- .cursor/rules/xmos.mdc             # Cursor guidance entry point
`-- skills/
    `-- <name>/
        |-- SKILL.md                  # Task-specific guidance
        `-- scripts/                  # Optional supporting scripts
```
