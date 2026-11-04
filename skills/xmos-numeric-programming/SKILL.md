---
name: xmos-numeric-programming
description: Use when writing, reviewing or optimising numerical or DSP code for XMOS/XCORE -- choosing fixed-point, block floating-point or floating-point representations, avoiding double and 64-bit division in real-time loops, replacing division with reciprocals, or selecting compatible lib_xcore_math operations and checking scaling, headroom, saturation, rounding and error bounds.
---

# Numeric and DSP programming for XMOS

Choosing numeric representations and operations for XS3 code. For the hardware arithmetic,
floating-point and vector-unit (VPU) instructions behind this, see
[`xmos-xs3-architecture`](../xmos-xs3-architecture/SKILL.md). For memory, stack and real-time
practices see [`xmos-embedded-c-practices`](../xmos-embedded-c-practices/SKILL.md).

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

## Using `lib_xcore_math`

**Investigate `lib_xcore_math` before implementing equivalent math.** Use the version
selected by the project and consult that version's documentation and headers for
available operations, types and constraints. For a new dependency, select a compatible
official release; do not upgrade an existing dependency merely to match a skill example.
See [capability discovery](../xmos-capability-discovery/SKILL.md) for finding official
sources. Do not guess API names or treat library operations as drop-in `libm`
replacements. Verify numeric representations rather than assuming a floating-point
type is C `float`, and check input ranges, headroom, scaling, saturation, rounding
and required error bounds before substitution.

For VPU-based copy and fill operations, see
[bulk memory moves and fills](../xmos-embedded-c-practices/SKILL.md#bulk-memory-moves-and-fills).

## Verify, then optimise

Check numerical correctness against the required precision and error bounds before profiling and
optimising; measure the actual workload rather than assuming a speedup (see
[`xmos-debugging-profiling`](../xmos-debugging-profiling/SKILL.md)).
