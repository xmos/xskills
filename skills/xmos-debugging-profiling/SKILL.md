---
name: xmos-debugging-profiling
description: Use when debugging an XMOS application with xgdb (breakpoints, stepping, inspecting a specific tile/core), interpreting a runtime exception like "Program received signal ET_ECALL"/ET_ARITHMETIC/etc. from xrun or xgdb, profiling with xgprof or xsim --gprof, measuring elapsed time for a code span with a hardware timer (hwtimer_get_time), or adding fast "printf-style" debugging/data logging with xSCOPE. Covers XTC Tools 15.3.1 xgdb/xSCOPE.
---

# Debugging and profiling XMOS applications

Requires the XTC Tools environment active (see
[`xmos-environment-setup`](../xmos-environment-setup/SKILL.md)) and a `.xe` built with `-g` (see
[`xmos-build-system`](../xmos-build-system/SKILL.md)) — without `-g`, source-level debugging will
not work well.

## `xgdb`: source-level, multi-tile debugging

`xgdb` extends GDB with awareness of multiple XCORE tiles and hardware threads (also
called logical cores). `xrun` is actually a
wrapper around `xgdb` for common cases; use `xgdb` directly for interactive/advanced debugging.

Typical interactive session:

```text
xgdb a.xe
(gdb) connect              # connect to the target (hardware or, after `connect -s`, the simulator)
(gdb) load                 # load the program
(gdb) tile 0                # focus a specific tile (repeat to switch focus)
(gdb) break file.c:16       # sets a breakpoint on every tile running that source line
(gdb) break file.c:16 inferior 1   # restrict the breakpoint to one tile/inferior instead
(gdb) info inferiors        # list tiles known to the session
(gdb) info breakpoints
(gdb) info threads          # shows tile[n] core[m]; the focused one is marked
(gdb) continue
```

`xgdb` can also be scripted non-interactively:

```sh
xgdb --batch -x cmds.txt a.xe
# or, equivalently, with one -ex per command instead of a command file:
xgdb --batch -ex "connect" -ex "load" -ex "break main" -ex "continue" -ex "quit" a.xe
```

where `cmds.txt` is a plain GDB command file.

If more than one xtag adapter is connected, select which one to use the same way as `xrun`/`xflash`
— pass `--adapter-id <serial>` (or `--adapter-index <n>`) as an argument to `connect` itself (these
are `xgdbserver` options, forwarded through `connect`), e.g. `connect --adapter-id BW736KUU`. Use
`connect --list-devices` to see available adapters/serials from within `xgdb` (same info as `xrun
--list-devices`).

To debug in the simulator instead of on hardware, run `connect -s` instead of `connect`.

Tip: `(gdb) start` is shorthand for `load` + `break main` + `continue` in a single command, for the
common case of wanting to stop at the very beginning of `main`.

**`quit` on a still-running/attached target prompts for confirmation and exits non-zero.** If the
target program is still executing when `quit` runs (e.g. right after a breakpoint like `break
main` + `continue` stops it, as opposed to running to program exit), `xgdb` prints `A debugging
session is active. ... Quit anyway? (y or n)`; in `--batch` mode this is auto-answered `y`
(inferiors are killed), but the process still exits with code **1**, not 0. Don't treat that exit
code as a script/build failure — check the printed output for the expected breakpoint-hit message
instead of relying on the exit code when scripting a `--batch` session that quits out of a live
target.

## Interpreting a runtime exception from `xrun`/`xgdb`

If `xrun` (or `xgdb`) stops with output like:

```text
xrun: Program received signal ET_ECALL, Application exception.
      0x00080d14 in xk_evk_xu316_AudioHwInit (config=...) at .../xk_evk_xu316_board.xc:128
```

this is a real application-level exception, not a connection/tooling problem — execution reached
the reported file/line and the hardware raised the named exception. The signal name is one of the
`ET_*` exception types (see the table in [`xmos-xs3-architecture`](../xmos-xs3-architecture/SKILL.md)); the
most common one to see this way is `ET_ECALL`, raised by any `__builtin_trap()` call — not just a
failed `assert(...)`, but also `lib_xassert`'s `fail(...)` and `unreachable(...)` (confirmed by
running `lib_xassert`'s `app_assert`/`app_fail`/`app_unreachable` examples on real hardware — all
three raise `ET_ECALL` identically).

If the exception occurs in board or hardware-initialisation code, check that the connected board
matches the `APP_HW_TARGET`/`.xn` file the `.xe` was built for (see
[`xmos-build-system`](../xmos-build-system/SKILL.md)) before assuming a wiring fault or software bug.

Read the reported file/line and any `msg(...)` text first; it's usually specific enough to identify
the faulty component/assumption without further stepping. To inspect state at the point of the
exception interactively instead of just reading the one-line report, run the same command under
`xgdb` (`connect` → `load` → `continue`) and use `info threads`/`bt` once it stops.

## Profiling with `xgprof`

Profiling captures *sampled* execution data per tile/thread via `xgdb`, separate from
`xsim --gprof` (the simulator's own function/statement/address-level profiling of a `.xe` run in
`xsim`, mentioned below). The `xgprof` workflow below targets real hardware via `xgdb`.

### 1. Capture sample data via `xgdb`

Start `xgdb`, connecting with the `--gprof` option:

```sh
xgdb -ex "connect --gprof" -ex load -ex continue CircularBuffer.xe
```

Leave `xgdb` running for the period you want to profile, then interrupt with <kbd>Ctrl-C</kbd> and
exit with `quit`. On exit, one `.gprof` file per tile/thread is written to the current
working directory (the filename encodes which tile and thread it covers, e.g.
`tile[0]_core0.gprof`).

To profile a program that is already running, having booted from flash, attach instead of loading:

```sh
xgdb -ex "attach --gprof" -ex "continue" test.xe
```

(where `test.xe` is the same `.xe` used to build the flash/upgrade image). Capture and exit the same
way as above.

### 2. Split the `.xe` into per-tile ELF images

```sh
xobjdump -s CircularBuffer.xe
```

This produces one ELF file per tile per boot stage, e.g. `image_n0c0_2.elf` for tile 0,
`image_n0c1_2.elf` for tile 1, and so on. **Use only the `_2`-suffixed images** — the others are
bootstrap images used for system initialization and are not what you want to analyse.

### 3. Generate a report with `xgprof`

Pair each tile's ELF file with the matching `.gprof` file from step 1. Useful report levels:

```sh
# Flat summary report
xgprof -b image_n0c0_2.elf tile[0]_core0.gprof

# Source-line-level detail
xgprof -l -b image_n0c0_2.elf tile[0]_core0.gprof

# Address-level detail with hit counts
xgprof -C -l -b image_n0c0_2.elf tile[0]_core0.gprof
```

Start with the flat summary, then drill into `-l`/`-C -l` for the tiles/functions that matter.

### Simulator-only alternative: `xsim --gprof`

`xsim a.xe --gprof` profiles a program at the function/statement/address level while it runs in the
simulator, writing profile data to a file. Use this when hardware isn't available or when you want
a deterministic, simulator-based profile run; use the `xgdb`-based workflow above when profiling on
real hardware.

## Manual timing with a hardware timer

For a quick, low-overhead measurement of how long a specific span of code takes — without setting
up `xgprof` — read a hardware timer (`xcore/hwtimer.h`, see
[`xmos-c-programming`](../xmos-c-programming/SKILL.md)) before and after the code of interest:

```c
#include <xcore/hwtimer.h>
#include <stdint.h>

// Within a function returning an error code:
hwtimer_t tmr = hwtimer_alloc();
if (tmr == 0) {
    return 1;
}

uint32_t t0 = hwtimer_get_time(tmr);
// ... code being measured ...
uint32_t t1 = hwtimer_get_time(tmr);

uint32_t elapsed = t1 - t0;   // reference-clock ticks; convert using the actual frequency
hwtimer_free(tmr);
// Consume/report elapsed and the measured result outside the timed interval.
```

- Declaring `t0` and `t1` volatile would preserve their stores and the order of those
  volatile accesses, but would not guarantee that unrelated non-volatile computation
  stays between the timer reads. The XTC 15.3.1 implementation of `hwtimer_get_time()`
  already uses volatile assembly for the reads; see
  `<XMOS_TOOL_PATH>/target/include/xcore/_support/xcore_hwtimer_impl.h`.
  Keep measured results observable and inspect optimised generated code when precise
  measurement boundaries matter. Use documented compiler-ordering mechanisms where
  needed rather than treating volatile timestamp storage as a general compiler barrier.
- The timer ticks at the 100 MHz reference clock (see
  [`xmos-xs3-architecture`](../xmos-xs3-architecture/SKILL.md)): divide `elapsed` by 100 for microseconds, or
  multiply by 10 for nanoseconds. **100 MHz is only the default** — if the project's XN file or PLL
  configuration changes the reference clock frequency, use the actual configured value instead; see
  [`xmos-clock-domains`](../xmos-clock-domains/SKILL.md).
- Unsigned subtraction handles a wrap provided the interval is shorter than one full
  32-bit timer period. It cannot count multiple wraps; at 100 MHz the full period is
  approximately 42.95 seconds. The reference frequency must also remain constant for
  a single fixed-frequency conversion to apply.
- Free the timer (`hwtimer_free(tmr)`) once done, like any other resource — see
  [`xmos-c-programming`](../xmos-c-programming/SKILL.md).
- This measures elapsed reference-clock ticks, not just instruction issue opportunities
  for the current hardware thread. Other runnable threads share
  the tile's execution unit, so their interleaved execution contributes to elapsed time;
  see the scheduler notes in [`xmos-xs3-architecture`](../xmos-xs3-architecture/SKILL.md). For statistically
  robust or multi-function profiling, prefer `xgprof`/`xsim --gprof` above instead of hand-rolled
  timing.

## xSCOPE: fast host communication and data probes

xSCOPE can carry text writes and structured probes without JTAG's tile-wide debug
halts. It still has instrumentation and bandwidth costs; lossless mode can stall the
transmitting core and lossy mode can drop packets. See the
[XTC fast-printf guide](https://www.xmos.com/documentation/XM-014363-PC/html/tools-guide/quick-start/fast-printf.html)
and [xSCOPE reference/FAQ](https://www.xmos.com/documentation/XM-014363-PC/html/tools-guide/tools-ref/xscope/index.html)
for the selected toolchain's setup and transport limits.

### Configure xSCOPE text I/O

1. Create an xSCOPE config file (conventionally `<name>.xscope`), e.g.:

   ```xml
   <xSCOPEconfig ioMode="basic" enabled="true"></xSCOPEconfig>
   ```

   Use `ioMode="timed"` instead of `"basic"` to add timestamps to output, reducing
   the amount of data that can be buffered.

2. Pass this config file to `xcc` as an input at **both compile and link** time (alongside your
   source files), or use `xcc -fxscope[=link]` to enable basic xSCOPE support without a separate
   config file.

3. Run with xSCOPE enabled:

   ```sh
   xrun --xscope a.xe
   ```

Seeing ordinary stdout under a host command does not prove the application was built
to send it over xSCOPE. Verify the build inputs and required board xLINK wiring;
do not infer the transport or its timing properties merely from printed text.
The documented xSCOPE `ioMode` accelerates **write** syscalls; other calls such as
`read` still use JTAG. See the FAQ before relying on file I/O semantics.

### Data probes

Beyond simple text output, xSCOPE supports named "probes" for streaming structured data (e.g. a
signal value over time) to a VCD file for viewing in a waveform viewer such as GTKWave:

```xml
<Probe name="MyProbe" type="CONTINUOUS" datatype="UINT" units="mV" enabled="true"/>
```

```c
#include <xscope.h>
xscope_int(MyProbe, value);
```

```sh
xrun --xscope --xscope-file xscope.vcd a.xe
```

## Choosing a debugging/profiling tool

| Need | Use |
|---|---|
| Step through code, inspect variables, set breakpoints | `xgdb` (or `xrun`/VS Code Debug for common cases) |
| Understand behavior across multiple tiles/cores simultaneously | `xgdb` `info inferiors` / `tile <n>` |
| Lower-impact text/log output, with bandwidth and overhead checked | Configured xSCOPE I/O (`xrun --xscope`) |
| Structured/waveform data logging | xSCOPE probes → VCD → GTKWave |
| Function/statement-level performance profiling on hardware | `xgdb -ex "connect --gprof" ...` → `xobjdump -s` → `xgprof` |
| Function/statement/address-level performance profiling in the simulator | `xsim a.xe --gprof` |
| Quick elapsed-time check for one code span, no profiler setup | `hwtimer_get_time` before/after (see above) |
| Full instruction or signal trace | `xsim --trace` / `--vcd-tracing` — see [`xmos-run-and-simulate`](../xmos-run-and-simulate/SKILL.md) |

If using VS Code, breakpoint debugging is also available through the editor's Debug button, backed
by `xgdb` — see [`xmos-vscode-extension`](../xmos-vscode-extension/SKILL.md).
