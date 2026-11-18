---
name: xmos-c-programming
description: Use when writing or reviewing multicore C code for XMOS/XCORE using lib_xcore -- parallel tasks (PAR_JOBS/DECLARE_JOB), channels, streaming channels, ports, hardware timers, or select/event handling; choosing/diagnosing a -mcmodel=small|large|hybrid linker error; or when deciding whether C or XC is appropriate. Covers XTC Tools 15.3.1 lib_xcore C APIs.
---

# XMOS C programming (lib_xcore)

**Terminology:** XMOS uses **logical core** to mean a **hardware thread**. This guidance
generally uses "thread" for that hardware execution context. A task or job is software
that executes on a thread, not the hardware resource itself; other execution models
may schedule multiple software tasks on a thread.

**xcore can be programmed in C or XC.** This skill covers C using `lib_xcore`.

All of the APIs below are declared in headers under `xcore/` (installed at
`<XMOS_TOOL_PATH>/target/include/xcore/` — see
[`xmos-toolchain-paths`](../xmos-toolchain-paths/SKILL.md)), and rely on the XS3 concepts described
in [`xmos-xs3-architecture`](../xmos-xs3-architecture/SKILL.md) (threads, channels, ports, timers).

For DSP/numeric code, investigate compatible `lib_xcore_math` operations before
writing equivalent implementations; see
[`xmos-numeric-programming`](../xmos-numeric-programming/SKILL.md).

Everything below applies **within a single tile**. For multi-tile applications, including the
required XC `main()` placement layer, see
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

- Each `PJOB` runs on its own thread of the **current tile**.
- The number of jobs is hard-limited by the number of available threads on that tile; if there
  aren't enough, this is a **runtime trap**, not a compile error — don't over-subscribe a tile.
- Jobs return `void`; communicate through channels or pass disjoint output storage
  whose lifetime extends until the jobs join, then read the results after `PAR_JOBS` returns.
- The threads in a `PAR_JOBS` are implicitly created with a **synchroniser** that implements
  barrier synchronisation. If the algorithm requires the threads to
  go through a barrier, for example in a loop, then an extra parameter
  `PAR_SYNC` must be passed to each thread. It is of type `synchronizer_t`
  and the barrier is passed by each thread calling
  `par_jobs_synchronize(...)` on the synchroniser.

## Channels: `xcore/channel.h`

```c
#include <xcore/channel.h>
#include <xcore/parallel.h>
#include <stdint.h>

DECLARE_JOB(sender, (chanend_t));
DECLARE_JOB(receiver, (chanend_t, uint32_t *));

void sender(chanend_t c) {
    chan_out_word(c, 42);
}

void receiver(chanend_t c, uint32_t *result) {
    *result = chan_in_word(c);
}

int main(void) {
    channel_t c = chan_alloc();
    if (c.end_a == 0) {
        return 1;   // allocation failed; both endpoints are zero
    }
    uint32_t result = 0;
    PAR_JOBS(
        PJOB(sender, (c.end_a)),
        PJOB(receiver, (c.end_b, &result))
    );
    chan_free(c);   // both jobs have returned
    return result == 42 ? 0 : 1;
}
```

- Standard channels are **blocking/handshaking**: both ends must transact for a transfer to
  complete. Run the sender and receiver concurrently; a send followed by a receive
  on the same thread can deadlock before reaching the receive.
- `xcore/channel_streaming.h` provides `s_chan_*` equivalents with no handshake, for higher
  throughput and less synchronisation.
  Free streaming channels as soon as possible — they hold switch routing capacity open,
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

// Within a function returning an error code:
hwtimer_t t = hwtimer_alloc();
if (t == 0) {
    return 1;
}
hwtimer_delay(t, 1000);            // delay in reference-clock ticks
uint32_t now = hwtimer_get_time(t);
hwtimer_free(t);
```

Use hardware timers for delays and timed I/O instead of busy-loops. See
[`xmos-real-time-programming`](../xmos-real-time-programming/SKILL.md) for deadline scheduling, and
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

`select` lets one thread wait on channels, ports, and timers simultaneously and react to
a ready event — this is the idiomatic alternative to polling on XS3. Use
`CASE_GUARD_THEN` to make a case conditional on a runtime guard expression.

This example shows dispatch structure only. Each handler must perform the appropriate
resource operation: consume channel input, or read the port and update its trigger
condition as required. Selecting an event does not perform those operations automatically.

If multiple events are ready, `SELECT_RES` does not guarantee which is selected
(`SELECT_RES_ORDERED` provides priority ordering at extra cost). Keep handlers bounded;
blocking or lengthy work delays other events serviced by the same thread (see
[`xmos-real-time-programming`](../xmos-real-time-programming/SKILL.md) for event-loop budgets). See the
[lib_xcore select documentation](https://www.xmos.com/documentation/XM-014363-PC/html/tools-guide/tools-ref/libraries/lib-xcore-api/lib-xcore-api.html#c.SELECT_RES)
for complete examples and ordering options.

## Stack size is statically calculated — implications for how you write C

The tools calculate stack requirements at build time where stack frames and callee
requirements are calculable (visible via `xcc -report`, per
[`xmos-build-system`](../xmos-build-system/SKILL.md)). See the
[XTC C guide's stack guidance](https://www.xmos.com/documentation/XM-014363-PC/html/prog-guide/quick-start/c-programming-guide/index.html)
for the analysis and manual-bound mechanisms.

- **Keep stack frames bounded and analysable.** Variable-length arrays and other
  runtime-sized frames can prevent automatic bounds. Heap policy is a separate issue;
  see [`xmos-embedded-c-practices`](../xmos-embedded-c-practices/SKILL.md).
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
  see [`xmos-xs3-architecture`](../xmos-xs3-architecture/SKILL.md) on dual-issue). Generates the most
  efficient code; if either assumption doesn't hold, the **linker** reports an error (not a compile
  error) — that's the signal to switch models, not something to pre-guess.
- **`large`** — data can be spread across multiple/non-contiguous memories (e.g. internal RAM,
  external DDR, software-defined memory — see the memory model in
  [`xmos-xs3-architecture`](../xmos-xs3-architecture/SKILL.md)), and functions anywhere in memory can be
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
