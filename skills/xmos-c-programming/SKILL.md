---
name: xmos-c-programming
description: Use when writing or reviewing multicore C code for XMOS/XCORE using lib_xcore -- parallel tasks (PAR_JOBS/DECLARE_JOB), channels, streaming channels, ports, hardware timers, or select/event handling; choosing/diagnosing a -mcmodel=small|large|hybrid linker error; or when deciding whether C or XC is appropriate. Covers XTC Tools 15.3.1 lib_xcore C APIs.
---

# XMOS C programming (lib_xcore)

XMOS is moving away from the XC language. **Write new code in C using `lib_xcore`**, not XC, unless
a task specifically requires an XC-only language feature (e.g. certain legacy interfaces). If XC is
required, keep it isolated and prefer C for everything else.

All of the APIs below are declared in headers under `xcore/` (installed at
`<XMOS_TOOL_PATH>/target/include/xcore/` — see
[`xmos-toolchain-paths`](../xmos-toolchain-paths/SKILL.md)), and rely on the XS3 concepts described
in [`xs3-architecture`](../xs3-architecture/SKILL.md) (logical cores, channels, ports, timers).

For DSP/numeric code (fixed-point arithmetic, saturating 64-to-32-bit division, trig/exp/sqrt, or
vectorized math targeting XS3's VPU) prefer `lib_xcore_math` over hand-rolled implementations — see
[`embedded-c-practices`](../embedded-c-practices/SKILL.md) for specifics.
Everything below applies **within a single tile**. To place entry-points on more than one tile or
pass a chanend between tiles, see
[`xmos-multi-tile-architecture`](../xmos-multi-tile-architecture/SKILL.md).
## Parallel tasks: `xcore/parallel.h`

```c
#include <xcore/parallel.h>

DECLARE_JOB(worker, (int, int));

void worker(int id, int iterations) { /* ... */ }

void run(void) {
    PAR_JOBS(
        PJOB(worker, (0, 100)),
        PJOB(worker, (1, 100))
    );
    // implicit join here: PAR_JOBS returns once every job has returned
}
```

- Each `PJOB` runs on its own logical core of the **current tile**.
- The number of jobs is hard-limited by the number of free logical cores on that tile; if there
  aren't enough, this is a **runtime trap**, not a compile error — don't over-subscribe a tile.
- Jobs return `void`; communicate results back via channels, not return values.

## Channels: `xcore/channel.h`

```c
#include <xcore/channel.h>

channel_t c = chan_alloc();
// c.end_a, c.end_b: give one end to each of two logical cores (e.g. via PJOB arguments)
chan_out_word(c.end_a, 42);
int v = chan_in_word(c.end_b);
chan_free(c);
```

- Standard channels are **blocking/handshaking**: both ends must transact for a transfer to
  complete.
- `xcore/channel_streaming.h` provides `s_chan_*` equivalents with no handshake, for higher
  throughput. Free streaming channels as soon as possible — they hold switch routing capacity open,
  which can starve other traffic if left allocated.

## Ports: `xcore/port.h`

Port handles come from `platform.h`/`xs1.h` (e.g. `XS1_PORT_4D`).

```c
#include <xcore/port.h>
#include <xs1.h>

port_t p = XS1_PORT_1A;
port_enable(p);
port_out(p, 1);
port_set_trigger_in_not_equal(p, 0);   // block until the pin changes from 0
port_in(p);
port_disable(p);
```

## Hardware timers: `xcore/hwtimer.h`

```c
#include <xcore/hwtimer.h>

hwtimer_t t = hwtimer_alloc();     // may return 0 on failure - check it
hwtimer_delay(t, 1000);            // delay in reference-clock ticks
uint32_t now = hwtimer_get_time(t);
hwtimer_free(t);
```

Use hardware timers for delays and timed I/O instead of busy-loops. See
[`xmos-debugging-profiling`](../xmos-debugging-profiling/SKILL.md) for using a hardware timer to
manually measure the elapsed time of a specific code span.

## Waiting on multiple resources: `xcore/select.h`

```c
#include <xcore/select.h>

SELECT_RES(
    CASE_THEN(c.end_a, on_channel),
    CASE_THEN(p,        on_port)
) {
on_channel:
    // handle channel event
    continue;   // go back to waiting
on_port:
    // handle port event
    break;      // exit the select block
}
```

`select` lets one logical core wait on channels, ports, and timers simultaneously and react to
whichever becomes ready first — this is the idiomatic alternative to polling on XS3. Use
`CASE_GUARD_THEN` to make a case conditional on a runtime guard expression.

## Stack size is statically calculated — implications for how you write C

The compiler calculates each logical core's stack size statically at build time (visible via
`xcc -report`, per [`xmos-build-system`](../xmos-build-system/SKILL.md)). This is only possible
when the call graph is fully known at compile time, which is why:

- **No dynamic allocation** (`malloc`/`free`) — see
  [`embedded-c-practices`](../embedded-c-practices/SKILL.md).
- **No unbounded/indirect recursion** — the compiler cannot bound stack usage for it.
- **Function pointers must be annotated** if used for indirect calls: mark both the pointer type and
  every candidate target function with `__attribute__((fptrgroup("name")))` so the compiler can
  account for the worst case in the group. Suppress related warnings only deliberately, with
  `-Wno-xcore-fptrgroup`, not by default.
- In rare cases requiring manual control, stack size can be set explicitly via an assembler symbol
  (`.set myfunc.nstackwords, <expr>`, supporting `+`, `*`, `$M` (max), `$A` (align-up) operators) —
  prefer letting the compiler calculate this automatically wherever possible.

## Memory models

`-mcmodel=small|large|hybrid` controls how `xcc` generates code to access data and call functions.
It's a **per-source-file (translation unit) setting**, not a whole-program one — though in practice
most applications compile every file under the same model. See
[`xmos-build-system`](../xmos-build-system/SKILL.md) for setting this via `APP_COMPILER_FLAGS`.

- **`small` (default)** — assumes all of a tile's statically-allocated data fits in one contiguous
  256KB region, and that branch targets are within 128KB (single-issue) or 256KB (dual-issue —
  see [`xs3-architecture`](../xs3-architecture/SKILL.md) on dual-issue). Generates the most
  efficient code; if either assumption doesn't hold, the **linker** reports an error (not a compile
  error) — that's the signal to switch models, not something to pre-guess.
- **`large`** — data can be spread across multiple/non-contiguous memories (e.g. internal RAM,
  external DDR, software-defined memory — see the memory model in
  [`xs3-architecture`](../xs3-architecture/SKILL.md)), and functions anywhere in memory can be
  called. Generates less efficient data-access and call code than `small`.
- **`hybrid`** — uses efficient small-model code for data accesses the compiler can prove are safe,
  falling back to large-model access otherwise; function calls always use large-model code. Lets
  one file efficiently access a contiguous area (typically internal RAM) while still reaching
  other memories, but the set of accesses eligible for the efficient path is limited — e.g. C
  `extern` variables always get large-model (less efficient) access even under `hybrid`.
- **Indirect access (via a pointer) always works under any model**, regardless of where the
  pointee lives — the contiguous-size restriction only applies to direct access to an object by
  name. This is why `small` is often still viable even when a small amount of data lives outside
  the 256KB region, as long as it's only ever reached through a pointer.

Prefer the `small` default; only move to `hybrid`/`large` when the linker actually reports a
size/range error, or the application deliberately spans multiple memory types (e.g. external RAM)
and needs to access them directly by name rather than through a pointer.
