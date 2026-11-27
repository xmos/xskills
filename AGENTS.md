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

## Ownership and licensing

Do not determine legal ownership. Preserve existing copyright, attribution and licence
notices, including third-party notices; do not judge their legitimacy. Do not infer
ownership from repository naming, target hardware, organisation membership, the user's
employer, commit history or licence choice.

Apply new or changed notices only under explicit project instructions supplying the
notice text or template and the files it applies to. The same rule applies to licence
and vendor metadata; do not select these yourself. Without such instructions, add no
new attribution and leave existing legal metadata unchanged. Continue ordinary coding
without investigating ownership or asking ownership questions. Ask only when the
requested task requires a legal-metadata edit and the necessary instructions are missing
or conflicting. Existing project instructions need no separate ownership verification.

## Core principles

1. **C or XC.** Choose C, XC, or a combination according to the problem and
   project requirements; neither language is preferred by default. For C using
   `lib_xcore`, see
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

## Running verifiers

Verifiers are boolean claims about the code that must stay true. Each is a
`.md` file with an `id`, a `scope` (file globs, relative to the root of the
repository being changed), a `severity` (`error`, `warn` or `off`) and a claim
with pass/fail conditions. Verifiers cover rules that need judgement; rules a
script can check belong in the repository's tests.

The verifiers that apply to a repository are the generic ones in this
repository's [`verifiers/`](./verifiers/) plus those in the repository's own
`verifiers/` directory, if it has one. A repository with no `verifiers/`
directory still runs the generic ones. A local verifier with the same `id` as a
generic one replaces it; `severity: off` disables it.

Run them before finishing a change you made, and when reviewing a change
someone else made:

1. List the files in the change.
2. Find every applicable verifier whose `scope` matches any of them. Skip
   verifiers with `severity: off`.
3. For each, judge the change against the claim: the lines added or modified,
   read in the context of their files. Do not fail a verifier for existing
   code the change did not touch; mention it as a note instead. Ignore
   anything the verifier lists as an exception.
4. Give evidence for every result, with `file:line` references. On PASS, name
   what you checked (for example the new define and where it is guarded). On
   FAIL, quote the offending lines and say which condition they break.

What happens next depends on whether the change is yours.

**If you made the change:** fix every `error` failure and judge it again.
Leave `warn` failures unless asked. Report each verifier id as PASS, FIXED
(it failed and you fixed it: say what you changed) or FAIL (say why it
remains). If a verifier seems wrong, say so; don't edit or delete it, or
change correct code, to make it pass.

**If you are reviewing a change you did not make:** do not modify anything.
Report each verifier id as PASS or FAIL.

Give a verifier's severity only when it fails, as `FAIL (error)` or
`FAIL (warn)`. Do not show severity on a PASS or FIXED result.

In both cases, say so if no verifier matched, and report it as a verification
gap if the generic verifiers could not be read.

To audit a whole repository against a verifier, for example after adding or
tightening one, judge every file in its `scope` instead of only the change.
Do this only when asked, and report without fixing.

## Generic verifiers

`verifiers/` holds verifiers that apply to every XMOS repo whose AGENTS.md
points here. Changes to them affect all those repos, so:

- Only add a verifier here if it holds for XMOS repos generally. Anything
  specific to one repo belongs in that repo's own `verifiers/`.
- Write a verifier only for a rule a compiler warning, linter or test cannot
  check. If one can, add that check to the repository's tests instead. If a
  verifier's rule later becomes checkable by a test, add the test and delete
  the verifier.
- Each verifier is one `.md` file with frontmatter: `id` (prefixed `xmos-`,
  unique), `scope` (file globs), `severity` (`error`, `warn` or `off`). The
  body has a **Claim**,
  **Pass if**, **Fail if**, **Exceptions** (legitimate cases that look like
  violations, such as the words appearing in comments) and **Evidence** (what
  to quote on failure).
- One claim per verifier. If you need "and", split it.
- Keep scopes narrow so verifiers only run on relevant files.
- Before committing a verifier, try it on a change that should pass, one that
  should fail, and one that hits an exception.
- New verifiers start at `severity: warn`; raise to `error` only once they've
  run cleanly on real changes.
- Don't rename an `id`: repos override generic verifiers by id, and a rename
  silently breaks their overrides.

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
| [`xmos-real-time-programming`](./skills/xmos-real-time-programming/SKILL.md) | Understanding timers, port-clocks, real-time concurrency, and combining multiple real-time tasks. |
| [`xmos-embedded-c-practices`](./skills/xmos-embedded-c-practices/SKILL.md) | Writing or reviewing embedded C for correctness/safety: no malloc, stack sizing, no unbounded recursion, VPU copies/fills. |
| [`xmos-numeric-programming`](./skills/xmos-numeric-programming/SKILL.md) | Writing or optimising numerical/DSP code: fixed-point vs floating point, `double` and 64-bit division in real-time loops, selecting `lib_xcore_math` operations. |
| [`xmos-system-architecture`](./skills/xmos-system-architecture/SKILL.md) | Designing how an application maps onto XCORE: splitting compute/IO/control tasks across hardware threads and tiles, port-to-tile planning, choosing channels vs shared memory, bare metal vs RTOS. |
| [`xmos-testing`](./skills/xmos-testing/SKILL.md) | Writing or reviewing tests: `lib_unity` C unit tests, `test_support`/Pyxsim simulator testbenches, choosing host/simulator/hardware, pass/fail criteria. |
| [`xmos-project-structure`](./skills/xmos-project-structure/SKILL.md) | Setting up or navigating an XMOS sandbox/repo layout; setting up a Python venv for tooling. |
| [`xmos-library-repo-style`](./skills/xmos-library-repo-style/SKILL.md) | Maintaining adopted library conventions (`lib_*`): source notices, LICENSE, metadata, changelog, versions, docs and dependencies, without assuming ownership, licence or vendor. |
| [`xmos-internal-repo-checks`](./skills/xmos-internal-repo-checks/SKILL.md) | Diagnosing and fixing applicable `test_repo_checks` failures using internal `infr_apps` scripts; requires access and explicit project authorisation for legal-metadata updates. |
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
