---
name: xmos-printing-logging
description: Use when adding or reviewing XMOS text output or diagnostic logging, choosing print.h vs lib_logging/debug_printf vs stdio.h/printf, configuring per-unit debug output, handling buffered or interleaved prints, or setting up xSCOPE text I/O instead of JTAG --io. Covers XTC Tools 15.3.1 printing and host-write transport.
---

# Printing and diagnostic logging

## Choosing a printing API

Choose the API for the output you need, rather than defaulting to full `printf`:

| Need | Use | Why |
|---|---|---|
| Basic string, character or integer printing | `<print.h>`: e.g. `printstrln()`, `printintln()` | Lightweight default for basic printing, with a smaller code footprint and less runtime overhead than full stdio formatting. |
| Configurable diagnostic logging, especially inside library code | `lib_logging`: `<debug_print.h>` and `debug_printf()` | Lightweight formatting plus compile-time enable/disable, including per-debug-unit control, so applications can select which library diagnostics to include. |
| Full `printf` formatting or other standard I/O facilities | `<stdio.h>` | Use when those features are needed; accept their additional code-size and runtime costs. |

For basic output, for example:

```c
#include <print.h>

void report_ready(void)
{
    printstrln("Ready");
}
```

For library diagnostics, define `DEBUG_UNIT` before including `<debug_print.h>` (or set it
in the library's build flags). Configure the corresponding `DEBUG_PRINT_ENABLE_<unit>` /
`DEBUG_PRINT_DISABLE_<unit>` macros through the application's debug configuration. Add
`lib_logging` as a dependency using the project's build conventions. Keep required functional
output separate from diagnostics that may be compiled out, and do not put side effects in
logging arguments. `debug_printf()` supports only a subset of `printf` formatting; consult the
selected library version before using format specifiers, widths or padding.

See the XTC guide's
[reduced-overhead print functions](https://www.xmos.com/documentation/XM-014363-PC/html/tools-guide/tutorials/working-with-targets/intro.html#reduced-overhead-print-functions)
and the [`lib_logging` documentation](https://github.com/xmos/lib_logging/blob/v3.3.2/doc/rst/lib_logging.rst)
and [API header](https://github.com/xmos/lib_logging/blob/v3.3.2/lib_logging/api/debug_print.h)
for the API and configuration contracts.

## Buffering and concurrent output

Standard I/O streams may buffer output. If output must be written before normal program
termination, explicitly flush it with `fflush(stdout)` and check for errors, or configure stream
buffering with `setvbuf()` before using the stream. Do not assume a newline flushes every stream
or that stopping a simulator or host process flushes target stdio. Choose the printing API for
its features, not as a workaround for a simulator run limit. No API guarantees delivery before
an external stop.

Multiple `<print.h>` calls making up one message can interleave with output from other tasks.
Do not rely on ordering between tasks or assume an arbitrarily long `debug_printf()` message is
one indivisible write; consult the selected implementation's buffering limits. For background
on message fragments, see
[AN00239's printing discussion](https://github.com/xmos/lib_logging/blob/v3.3.2/examples/AN00239/doc/rst/AN00239.rst#printh).

## Prefer xSCOPE for host text output

**API choice and transport choice are separate.** Prefer `xrun --xscope a.xe` when the
application is configured for xSCOPE text I/O and the target's xLINK is physically wired
through to the XTAG debugger. An XN entry and software configuration alone are not enough;
a working JTAG connection does not prove that the xSCOPE xLINK is connected.

XMOS development boards usually provide this connection. Very small boards and
production-oriented reference designs may omit it; check the board schematic, debug connector
and cabling rather than assuming it is present. Use `xrun --io a.xe` only as a fallback when
xSCOPE cannot be used. Merely adding `--xscope` to the run command does not configure the
application's text-write path or supply missing hardware wiring.

JTAG host transfers halt all hardware threads on the calling tile. Configured xSCOPE writes
avoid those tile-wide debug halts, but still have instrumentation and bandwidth costs: lossless
mode can stall the transmitting core and lossy mode can drop packets. None of the printing APIs
makes host output non-blocking or safe in a time-critical loop. Do not assume a universal speedup
or guaranteed delivery merely from the API or transport chosen.

See the
[XTC fast-printf guide](https://www.xmos.com/documentation/XM-014363-PC/html/tools-guide/quick-start/fast-printf.html)
and [xSCOPE reference/FAQ](https://www.xmos.com/documentation/XM-014363-PC/html/tools-guide/tools-ref/xscope/index.html)
for the selected toolchain's setup and transport limits. Despite the guide's name, configured
text I/O applies to host writes from the lightweight printing APIs as well as `printf`.

### Configure xSCOPE text I/O

Before building or running, activate the XTC Tools environment; see
[`xmos-environment-setup`](../xmos-environment-setup/SKILL.md).

1. Create an xSCOPE config file (for example `text.xscope`):

   ```xml
   <xSCOPEconfig ioMode="basic" enabled="true"></xSCOPEconfig>
   ```

   Use `ioMode="timed"` instead of `"basic"` to add timestamps to output, reducing
   the amount of data that can be buffered.

2. Include this config in the project's build at **both compile and link** time. For direct
   `xcc` invocations, pass it as an input alongside the source files. For XCommon CMake, use
   the project's xSCOPE config integration; see
   [`xmos-build-system`](../xmos-build-system/SKILL.md).

   `xcc -fxscope` alone is not a substitute for text-I/O configuration: per the
   [xcc manual](https://www.xmos.com/documentation/XM-014363-PC/html/tools-guide/tools-ref/cmd-line-tools/xcc-manual/xcc-manual.html#cmdoption-xcc-fxscope),
   it is equivalent to a config with `ioMode="none"`, enabling xSCOPE and its target library
   without redirecting text writes. Both require an xSCOPE link in the target's XN file.

3. Run on hardware with xSCOPE enabled:

   ```sh
   xrun --xscope a.xe
   ```

Verify the build inputs and the physical xLINK connection to the XTAG rather than inferring the
transport from visible stdout.
The documented xSCOPE `ioMode` accelerates **write** syscalls; other calls such as `read` still
use JTAG. Consult the FAQ before relying on file-I/O semantics.

For execution flags, simulator xSCOPE options and long-running applications, see
[`xmos-run-and-simulate`](../xmos-run-and-simulate/SKILL.md). For structured/waveform data rather
than formatted text, see the xSCOPE probes in
[`xmos-debugging-profiling`](../xmos-debugging-profiling/SKILL.md#xscope-data-probes).
