---
name: xmos-embedded-c-practices
description: Use when writing or reviewing embedded C for XMOS/XCORE for general correctness and safety -- avoiding dynamic allocation, sizing stacks, avoiding unbounded recursion, choosing numeric representations, profiling real-time arithmetic and selecting compatible lib_xcore_math operations. Complements xmos-c-programming for lib_xcore-specific APIs.
---

# Embedded C practices for XMOS

General embedded-C discipline, specialized for why it matters on XS3/XCORE specifically. See
[`xmos-c-programming`](../xmos-c-programming/SKILL.md) for the XMOS-specific `lib_xcore` APIs these
practices apply to.

## No dynamic memory allocation

Do not use `malloc`/`free`/`calloc`/`realloc`/C++ `new`/`delete` in XMOS application code; use
static allocation (globals, `static` locals) or bounded stack allocation instead.
Check the selected implementation of library calls when hidden allocation matters;
do not infer allocation behaviour from a function name alone.

This is a determinism and memory-budgeting policy, not a claim that the toolchain
cannot compile heap-using code or calculate its call-stack requirements. Heap usage
and stack analysis are separate concerns. If a dependency cannot meet the policy,
identify that incompatibility rather than silently making an exception. A dedicated
thread does not isolate heap or memory-corruption consequences: threads on a tile
share memory. Any explicitly requested exception needs tile-wide memory, timing and
concurrency analysis. Prefer a fixed maximum size where possible.

## Bounded stacks: avoid unbounded/indirect recursion

Recursion whose depth the compiler cannot bound at compile time defeats static stack-size
calculation. Prefer iteration. A programmer-known recursion bound does not itself
prove that automatic analysis can establish it. Avoid variable-length arrays and
`alloca` in automatically sized tasks. Follow the
[XTC C guide](https://www.xmos.com/documentation/XM-014363-PC/html/prog-guide/quick-start/c-programming-guide/index.html)
when an explicit worst-case stack requirement is unavoidable, accounting for callees
and launched jobs. Review `-report` results and distinguish calculated from manually
asserted bounds; see [`xmos-c-programming`](../xmos-c-programming/SKILL.md).

## Function pointers

Indirect calls through function pointers also defeat static stack-size calculation unless
annotated. If used, mark both the pointer type and every possible target function with
`__attribute__((fptrgroup("name")))` — see
[`xmos-c-programming`](../xmos-c-programming/SKILL.md) for detail. Prefer avoiding indirect calls
where a direct call is possible.

## Prefer event-driven waiting over polling

Busy-wait loops consume a hardware thread's execution slots rather than allowing other
threads to use them, and are not necessary given XS3's hardware event model. Use `select`
(`xcore/select.h`) or blocking channel/port operations to wait for events instead of spinning — see
[`xmos-c-programming`](../xmos-c-programming/SKILL.md) and
[`xmos-xs3-architecture`](../xmos-xs3-architecture/SKILL.md).

## Fixed-point vs floating point

XS3 includes floating-point support, but many XMOS DSP/audio codebases still prefer fixed-point
arithmetic for performance-critical inner loops. Default rule: **if the surrounding codebase or
library has an established convention (fixed-point or floating-point), follow it. If there is no
established convention, or it is mixed/inconsistent, default to fixed-point for
performance-critical paths and note that choice inline.**

- **Prefer 32-bit fixed-point (Q-format `int32_t`) arithmetic** for real-time/hot-path DSP code over
  floating point, in line with the above.
- **Avoid `double` in real-time loops.** XS3's hardware floating-point unit is single-precision (see
  [`xmos-xs3-architecture`](../xmos-xs3-architecture/SKILL.md)) — `double` arithmetic is not natively
  accelerated and is comparatively slow. `double` is fine for one-off, non-time-critical code (e.g.
  startup/init-time calculations) where performance doesn't matter, but should not appear inside a
  real-time processing loop; use `float` or fixed-point instead.
- **Avoid raw 64-bit-by-32-bit division** (`int64_t`/`int32_t` or similar) in real-time code — like
  `double`, it is not a native single-instruction operation on XS3 and is comparatively expensive.
  Profile before replacing it. Reciprocal multiplication can change rounding,
  precision, overflow and zero-input behaviour; verify the numeric contract first.
- **Investigate `lib_xcore_math` before implementing equivalent math.** Use the version
  selected by the project and consult that version's documentation and headers for
  available operations, types and constraints. For a new dependency, select a compatible
  official release; do not upgrade an existing dependency merely to match a skill example.
  See [capability discovery](../xmos-capability-discovery/SKILL.md) for finding official
  sources. Do not guess API names or treat library operations as drop-in `libm`
  replacements. Verify numeric representations rather than assuming a floating-point
  type is C `float`, and check input ranges, headroom, scaling, saturation, rounding
  and required error bounds before substitution.

## Bulk memory moves and fills

Profile first, then consult the project's selected `lib_xcore_math` version for
available copy/fill operations and their contracts. Verify alignment, overlap
restrictions, lengths, boundary behaviour and return type before replacing a standard
library call; do not assume helper names or constraints are identical across versions.

A typed element fill is not generally equivalent to the byte
pattern written by `memset()`. Check element counts versus byte counts and the intended
values. Measure the actual workload rather than assuming a universal speedup; see
[`xmos-debugging-profiling`](../xmos-debugging-profiling/SKILL.md).

## General real-time hygiene

- Keep individual tasks' work per iteration bounded and predictable; avoid operations with
  unpredictable timing (e.g. unbounded loops driven by external input) inside time-critical loops.
- Prefer the compiler/tooling's own facilities for checking resource and stack usage
  (`xcc -report` — see [`xmos-build-system`](../xmos-build-system/SKILL.md)) over manual estimation.
- Use hardware (`xrun`) to validate real peripheral timing and end-to-end system behaviour.
  Simulated cycles can support instruction/timing analysis within the simulator's model, but
  host wall-clock runtime is not target execution time — see
  [`xmos-run-and-simulate`](../xmos-run-and-simulate/SKILL.md).
