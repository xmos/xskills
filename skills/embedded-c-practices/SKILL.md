---
name: embedded-c-practices
description: Use when writing or reviewing embedded C for XMOS/XCORE for general correctness and safety -- avoiding malloc/dynamic allocation, sizing stacks, avoiding unbounded recursion, fixed-point vs floating point, avoiding double/64-bit division in real-time loops, using lib_xcore_math for optimized fixed-point/vector math, replacing memcpy/memset with vpu_memcpy/vect_s32_set, and general real-time/interrupt-safety practices. Complements xmos-c-programming for lib_xcore-specific APIs.
---

# Embedded C practices for XMOS

General embedded-C discipline, specialized for why it matters on XS3/XCORE specifically. See
[`xmos-c-programming`](../xmos-c-programming/SKILL.md) for the XMOS-specific `lib_xcore` APIs these
practices apply to.

## No dynamic memory allocation

Do not use `malloc`/`free`/`calloc`/`realloc`/C++ `new`/`delete` in XMOS application code; use
static allocation (globals, `static` locals) or stack allocation instead, including for anything
that would otherwise call a standard-library function that allocates internally (e.g.
`printf`/`sprintf` formatting `%f`, `strtod`, some `libc` string functions).

If a required third-party library allocates internally and can't be avoided or replaced, isolate its use to a
dedicated logical core and explicitly document the exception (why it's needed, and that it breaks
the static stack/memory guarantees below for that core only).

This is not just a general embedded-systems preference on XCORE — it is a **hard requirement of the
build model**: XTC Tools statically calculate each logical core's stack size at compile time (see
[`xmos-c-programming`](../xmos-c-programming/SKILL.md)), and a heap undermines the guarantees that
calculation depends on (fragmentation, allocation failure, non-deterministic timing). If a task
seems to need dynamic sizing, prefer a fixed maximum size chosen at compile time instead.

## Bounded stacks: avoid unbounded/indirect recursion

Recursion whose depth the compiler cannot bound at compile time defeats static stack-size
calculation, the same way dynamic allocation does. Prefer iteration. If recursion is unavoidable,
ensure its maximum depth is a compile-time-known bound, and verify actual stack usage via
`xcc -report` (see [`xmos-build-system`](../xmos-build-system/SKILL.md)) rather than assuming it is
safe.

## Function pointers

Indirect calls through function pointers also defeat static stack-size calculation unless
annotated. If used, mark both the pointer type and every possible target function with
`__attribute__((fptrgroup("name")))` — see
[`xmos-c-programming`](../xmos-c-programming/SKILL.md) for detail. Prefer avoiding indirect calls
where a direct call is possible.

## Prefer event-driven waiting over polling

Busy-wait loops waste a logical core's execution slot that could otherwise be used by other
threads on the tile, and are not necessary given XS3's hardware event model. Use `select`
(`xcore/select.h`) or blocking channel/port operations to wait for events instead of spinning — see
[`xmos-c-programming`](../xmos-c-programming/SKILL.md) and
[`xs3-architecture`](../xs3-architecture/SKILL.md).

## Fixed-point vs floating point

XS3 includes floating-point support, but many XMOS DSP/audio codebases still prefer fixed-point
arithmetic for performance-critical inner loops. Default rule: **if the surrounding codebase or
library has an established convention (fixed-point or floating-point), follow it. If there is no
established convention, or it is mixed/inconsistent, default to fixed-point for
performance-critical paths and note that choice inline.**

- **Prefer 32-bit fixed-point (Q-format `int32_t`) arithmetic** for real-time/hot-path DSP code over
  floating point, in line with the above.
- **Avoid `double` in real-time loops.** XS3's hardware floating-point unit is single-precision (see
  [`xs3-architecture`](../xs3-architecture/SKILL.md)) — `double` arithmetic is not natively
  accelerated and is comparatively slow. `double` is fine for one-off, non-time-critical code (e.g.
  startup/init-time calculations) where performance doesn't matter, but should not appear inside a
  real-time processing loop; use `float` or fixed-point instead.
- **Avoid raw 64-bit-by-32-bit division** (`int64_t`/`int32_t` or similar) in real-time code — like
  `double`, it is not a native single-instruction operation on XS3 and is comparatively expensive.
  **Note**: `lib_xcore_math` v2.4.0 does **not** ship a ready-made `s32_divide_s64_s32`-style
  saturating-divide helper (checked directly against its installed API headers under
  `api/xmath/scalar/` — no such function exists in that or any other file). Don't assume the name of
  a convenience function without checking the actual installed headers first. What it does provide
  for avoiding a raw division: `s32_inverse()` (`api/xmath/scalar/s32.h`, computes a mantissa/exponent
  reciprocal you then multiply by, rather than dividing directly), `float_s32_div()`
  (`api/xmath/scalar/float_s32.h`, single-precision float divide), and vector-wide equivalents
  `vect_s32_inverse()`/`vect_s16_inverse()` (with matching `..._prepare()` headroom helpers). Prefer
  computing a reciprocal via `s32_inverse()`/`vect_s32_inverse()` and multiplying, or restructuring
  the calculation to use one of the library's `s32.h`/`bfp_s32.h` operations, over hand-rolling a
  64-bit division.
- **Prefer `lib_xcore_math` over hand-rolled math or plain `libm` calls** for anything beyond basic
  arithmetic (square root, inverse, trig, exponential/logistic, vectorized/SIMD operations, etc.).
  It provides both a scalar fixed-point API (e.g. `s32_sqrt`, `s32_inverse`, `s32_mul`, `q24_sin`/
  `q24_cos`/`q24_tan`, `q24_logistic`) and vector APIs that target XS3's VPU (see the vector unit in
  [`xs3-architecture`](../xs3-architecture/SKILL.md)) — these are written and tuned for XS3, unlike
  generic `libm`/hand-written implementations of the same functions. Confirmed present (v2.4.0):
  `s32_sqrt`, `s32_inverse`, `q24_sin`, `q24_cos`, `q24_tan`, `q24_logistic`/`q24_logistic_fast` all
  exist verbatim in `api/xmath/scalar/s32.h`; `chunk_q30_exp_small()` (a chunked/vectorized form) is
  the actual name for the exponential helper, not a scalar `q30_exp_small()`.

## Bulk memory moves and fills

For contiguous copies and fills in hot paths, use lib_xcore_math's vector-unit helpers rather than
the C library or a hand-written word-at-a-time loop, in plain C code as well as alongside assembly:

- **`vpu_memcpy(void *dst, const void *src, unsigned bytes)`** (`xmath/util.h`) is a drop-in
  replacement for `memcpy()` with two extra constraints: `dst` and `src` must both be word-aligned,
  and `src` must not sit at the very end of RAM. It moves 32 bytes per iteration through the VPU
  (`vldd`/`vstd`) with a masked tail, so it is roughly an order of magnitude faster than a
  word-at-a-time C loop.
- **`vect_s32_set(int32_t a[], int32_t b, unsigned length)`** fills an `int32_t` buffer with a
  constant, including zero, instead of `memset()`. Measured on XS3 at 600 MHz, clearing 512 words
  took about 125 reference clock ticks with `vect_s32_set()` against about 323 with `memset()`.

Both are contiguous only. To find which code is worth optimising in the first place, profile
first — see [`xmos-debugging-profiling`](../xmos-debugging-profiling/SKILL.md).

## General real-time hygiene

- Keep individual tasks' work per iteration bounded and predictable; avoid operations with
  unpredictable timing (e.g. unbounded loops driven by external input) inside time-critical loops.
- Prefer the compiler/tooling's own facilities for checking resource and stack usage
  (`xcc -report` — see [`xmos-build-system`](../xmos-build-system/SKILL.md)) over manual estimation.
- When something needs verifying against real timing, use hardware (`xrun`) rather than the
  simulator, which is not real-time — see
  [`xmos-run-and-simulate`](../xmos-run-and-simulate/SKILL.md).
