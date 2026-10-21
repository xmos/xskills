---
name: xmos-run-and-simulate
description: Use when running a built .xe file on real XMOS hardware with xrun, running it in the xsim simulator, choosing between real hardware and simulation, listing connected xtag adapters, or asking why xsim is slower than real hardware. Covers xrun/xsim from XTC Tools 15.3.1.
---

# Running and simulating XMOS applications

Requires the XTC Tools environment to be active — see
[`xmos-environment-setup`](../xmos-environment-setup/SKILL.md) — and a built `.xe` file — see
[`xmos-build-system`](../xmos-build-system/SKILL.md).

Both `xrun` and `xsim` run a program without making it persist on the device — see
[`xmos-flashing`](../xmos-flashing/SKILL.md) (`xflash`) for writing an application to non-volatile
flash so it boots standalone, without a host or debug adapter attached.

## `xrun`: running on real hardware

`xrun` loads and runs a `.xe` file on real XMOS hardware via a USB xtag debug adapter. It is
actually a wrapper around [`xgdb`](../xmos-debugging-profiling/SKILL.md); everything `xrun` does
can also be done with `xgdb` directly, but not vice versa.

```sh
xrun a.xe                    # load and run, return control once loaded (async)
xrun --list-devices          # or -l: list connected xtag adapters
xrun --adapter-id <serial> a.xe   # select a specific adapter when more than one is connected
```

### `--io` vs `--xscope` for host communication

If your program needs to communicate with the host (e.g. `printf`, file I/O), you must pick one of:

- **`--xscope`** (recommended in almost all cases): fast I/O over the xtag's dedicated xSCOPE
  xLINK channel, buffered on the adapter. Does not interrupt program execution.
- **`--io`**: system calls delivered over JTAG. This is **slow** and **pauses every logical core on
  the tile** for each transfer, which will likely break any real-time guarantees in the
  application. Only use `--io` for quick throwaway examples, or on platforms where the xSCOPE xLINK
  wiring isn't present.

```sh
xrun --xscope --xscope-file xscope.vcd a.xe
```

See [`xmos-debugging-profiling`](../xmos-debugging-profiling/SKILL.md) for using xSCOPE for
"printf-style" debugging and data probes.

### `--io`/`--xscope` block until the program exits — a problem for long-running device apps

Both `--io` and `--xscope` keep `xrun` attached and **waiting for the target program to
terminate** before returning control (this is what makes them useful for capturing output at all).
For a program that runs to completion this is fine, but many real XMOS applications — e.g. a USB
audio device reference design — are designed to run **indefinitely**, streaming/servicing the host
forever under normal operation. Run one of those with `--io`/`--xscope` and `xrun` will simply never
return, which will hang a script, an agent's synchronous tool call, or a terminal waiting for the
prompt back — this is a workflow/expectation problem, not a hardware fault, and no error will be
printed since nothing has actually gone wrong.

- If you don't need host I/O at all, use plain `xrun a.xe` (no `--io`/`--xscope`) — it loads,
  starts the program, and returns immediately, leaving the device running.
- If you do need I/O from a program you expect to run indefinitely, launch `xrun` in the
  background/a separate async process rather than waiting on it synchronously, and stop it
  explicitly (e.g. `Ctrl-C`, or killing the process) once you've captured what you need, rather
  than waiting for it to exit on its own.

Other useful `xrun` options: `--jtag-speed <n>` (JTAG clock divider, default 0, max 70; clock =
25/(n+2) MHz), `--noreset` (don't reset devices before loading), `--attach` (attach to an already
running program), `--dump-state` (dump core/register/stack state of all tiles).

### Troubleshooting hardware connection errors

Always run `xrun --list-devices` first when hardware isn't behaving — it's the fastest way to tell
"no adapter/board detected" apart from "adapter detected but something else is wrong".

| Symptom | Likely cause / fix |
|---|---|
| `xrun: No available XTAGs` + `xgdbserver failed to launch correctly, return code 1` | No XTAG adapter was found at all. Check: the board's XTAG USB cable is actually connected (not just the board's separate power/USB cable, if it has one); the XTAG's driver is installed; confirm with `xrun --list-devices` — it will print "No Available Devices Found" in this state. |
| `xrun --list-devices` shows "No Available Devices Found" | Same as above — nothing is enumerating over USB. Try a different USB port/cable, and check the OS recognizes the adapter (e.g. Device Manager on Windows) before re-running `xrun`. |
| `No XMOS devices found in JTAG chain` + `xrun: Cannot initialise debug device interface` | The XTAG adapter itself **is** detected (check with `xrun --list-devices` — it will list the adapter, e.g. `XMOS XTAG-4`, but show `Devices: None`), but it cannot see a target device on its JTAG chain. This means the adapter-to-board link is the problem, not the host-to-adapter USB link: check the XTAG's ribbon/ribbon-equivalent cable to the board's JTAG/XSYS connector is properly seated, and that the board itself is powered (many boards need a *separate* power connection in addition to the XTAG's USB cable). |
| Multiple adapters connected, wrong board gets programmed | Use `xrun --list-devices` to get each adapter's ID/serial, then target the right one explicitly with `--adapter-id <serial>`. |
| `xrun --list-devices` briefly reports "No Available Devices Found" for an adapter that was working moments earlier | Can be a transient USB re-enumeration, not necessarily a real disconnect. On Windows, check the adapter's PnP entry (`Get-PnpDevice`) — `ConfigManagerErrorCode`/`Problem` of `CM_PROB_PHANTOM` ("device is not connected", Code 45) means Windows still has a stale device record; simply retrying `xrun --list-devices` a little later often finds the adapter again once it re-enumerates, with no cable/driver action needed. |
| App loads and starts, but then raises an exception (e.g. `ET_ECALL`) during board/hardware init | The device *is* being programmed successfully, so this usually isn't an `xrun` problem at all — check the physically connected board actually matches the target the `.xe` was built for (`APP_HW_TARGET`/`.xn` file, see [`xmos-build-system`](../xmos-build-system/SKILL.md)); see [`xmos-debugging-profiling`](../xmos-debugging-profiling/SKILL.md) for interpreting the exception itself. |
| `xrun --io`/`--xscope` command produces no output and never returns control | Not an error — the device loaded and is running correctly, but `--io`/`--xscope` block until the program exits, and the program (e.g. a USB audio device) is designed to run indefinitely. See "`--io`/`--xscope` block until the program exits" above. |


## `xsim`: simulating without hardware

`xsim` provides a near cycle-accurate software model of one or more XCORE devices — useful when no
board is available, for deterministic/reproducible test runs, or for generating traces the
simulator alone can produce.

```sh
xsim a.xe
```

**`xsim` is not real-time — it runs many times slower than real hardware.** Use it for functional
testing, determinism, and tracing, not for validating real-time/timing behavior; use real hardware
(`xrun`) for that.

### Keep simulator runs to a minimum

Because a test suite that takes seconds on silicon can take tens of minutes in `xsim`, default to
`xrun` on an attached board for running tests, and treat `xsim` as the fallback:

- **Check how CI runs the test first.** Look at the repository's Jenkinsfile / test scripts: if
  Jenkins runs a test under `xsim`, it has been judged fast enough to simulate; if it only runs on
  hardware, expect it to be impractically slow in `xsim`.
- **Run only the test that answers the question**, not the whole suite, and reduce its iteration
  count before starting (many test suites have a build option for this) rather than waiting on a
  full-length run.
- **Prefer static evidence over another simulation** when it answers the same question — for
  example the generated code via `xobjdump -d`, or a trace already captured.
- **Give up on a run that hasn't answered in a few minutes.** Take whatever partial signal it gave
  (e.g. it no longer faults where it used to), kill it, and move on rather than polling it.
- **Write large traces to a fast local filesystem.** A `--trace-to` trace of a few seconds of
  simulated time runs to several GB; under WSL write it to the Linux filesystem, not a `/mnt/c`
  path, and search it from the end.

Unlike `xrun`, plain `xsim a.xe` needs **no `--io`/`--xscope`-equivalent flag** to surface a
program's `printf`/`debug_printf` output on stdout — it's shown by default (confirmed empirically:
`lib_logging`'s `app_debug_printf` printed all its lines under plain `xsim`, no extra flag needed).

### Plain C `printf` output can be lost entirely on a `--max-cycles`-bounded run of an indefinite program

Regular `<stdio.h>` `printf` output goes through a buffered stdio stream that is only flushed when
the buffer fills or the program exits normally — `--max-cycles` reaching its bound **kills the
simulation abruptly**, without giving the target a chance to flush. Confirmed empirically on
`lib_spdif`'s `app_spdif_loopback`: an early, unconditional `printf("Generating S/PDIF samples...")`
near the top of an indefinitely-running task produced **zero output** even at `--max-cycles
30000000`, even though the statement is definitely reached almost immediately after startup — the
output was simply never flushed before the simulator was killed. This differs from `debug_printf`
(`lib_logging`), which is written unbuffered/immediately (see
[`xmos-debugging-profiling`](../xmos-debugging-profiling/SKILL.md)) and always appears.

- Do **not** treat "no printed output" from a `--max-cycles`-bounded run as evidence a code path
  wasn't reached, or as a functional failure — for an indefinitely-running program, a bounded
  `xsim` run mainly proves "it started and didn't crash/hang within N cycles", not "expected output
  was produced". Only a program that terminates on its own (so stdio flushes at exit) gives a
  reliable printed-output check.
- If you need to confirm output specifically, prefer `debug_printf` (unbuffered) over plain `printf`
  when instrumenting code that will be smoke-tested with a bounded/indefinite `xsim` run.

### Plain `xsim a.xe` never returns for an indefinitely-running program

Unlike `xrun` (where only `--io`/`--xscope` block forever), **`xsim` has no default cycle limit at
all** — it just keeps simulating. Point it at an app designed to run forever (a loopback example, a
USB audio device, anything with a top-level `while (1)`/`select` loop and no exit condition) and
`xsim a.xe` will hang indefinitely with **no output and no error**, exactly like the `xrun`
indefinite-program trap above, but with no `--io`/`--xscope` flag to blame — plain `xsim a.xe` is
enough on its own. This is easy to hit when smoke-testing loopback/reference-design examples in a
simulator because there's no hardware to unplug and no timeout to notice.

- Before running an unfamiliar/indefinite example under `xsim`, always pass `--max-cycles <n>` (see
  below) to guarantee it returns.
- When scripting/automating `xsim` runs (e.g. from an agent's synchronous tool call), also apply an
  independent process-level timeout as a second line of defense in case the app happens to be
  bounded by something other than cycle count.

Useful options:

- `--max-cycles <n>` — stop after `n` simulated cycles (useful to bound a run in CI, e.g. to smoke-test
  an app that normally runs indefinitely). Reaching the bound prints `xsim: error: C51188: maximum
  cycles reached (n)` and **exits with a nonzero code** — this is the expected/intentional way a
  bounded run ends, not a functional failure; distinguish it from a real simulator/hardware exception
  by checking the message text, not just the exit code.
- `--trace` / `-t` — full instruction trace to stdout (or `--trace-to <file>` to write it to a file
  instead, recommended — the trace is large, e.g. tens of MB for well under a second of simulated
  time). Each line is annotated with the enclosing function name/offset (e.g.
  `(timer_aob_assert_time+ 82)`), so **a plain `xsim a.xe` crash report like `Unhandled exception:
  ECALL, data: 0x00000000` (which, unlike the `xrun`/`xgdb` case in
  [`xmos-debugging-profiling`](../xmos-debugging-profiling/SKILL.md), prints no file/line at all)
  can still be pinpointed without `xgdb`**: re-run with `--trace-to trace.txt`, then search the file
  for `TRAP` — the matching line (e.g. `TRAP ET: 8, SPC: 8000439e, ... (ECALL)`) and the
  instruction just above it (an `XM.ASSERT_s1r`/`ASSERTN_*` for a failed assert) give the exact
  function+offset where execution stopped; reading backwards from there through the same function's
  other trace lines reconstructs the register values (and hence the C-level condition, e.g. which
  branch of an `if`) that led to the trap, without needing a debug session at all. This also works
  for tracking down which of several call sites of a repeatedly-invoked function is the one that
  finally faulted — e.g. `grep "(some_func+ 4a)" trace.txt` to list every visit to one specific
  instruction/offset across the whole run.
- `--vcd-tracing 'args'` — signal-level tracing to a VCD file, viewable in a waveform viewer such
  as GTKWave. Verified syntax (`xsim --help`), arguments are one quoted string:
  `[global options] -tile <name> <trace options...> [-tile <name> <trace options...>]...`
  - Global: `-o <file>` (output path), `-start-disabled` (wait for a `_traceStart`/`_traceStop`
    syscall instead of tracing from cycle 0), `-pads` (trace device pad state).
  - `-tile <name>` — required for multi-tile programs, selects which tile the trace options that
    follow apply to (repeat the whole `-tile ... <options>` group per tile to trace more than one).
  - Per-tile trace options: `-ports`, `-ports-detailed`, `-cycles`, `-cores`, `-timers`,
    `-clock-blocks`, `-instructions`, `-functions`, `-usb`.
  - Example: `xsim --vcd-tracing "-o trace.vcd -tile tile[1] -ports -cycles" a.xe`.
  - Confirmed empirically: `$timescale` is always `1 ps`; a `-cycles` signal (named `*_CYCLES` in
    the VCD's `$comment`-embedded signal-hierarchy XML) increments by 1 every tick, and consecutive
    ticks are spaced by the tile's actual clock period in ps (e.g. 1666ps apart for a 600MHz
    `SystemFrequency` tile per the `.xn` file — see
    [`xmos-clock-domains`](../xmos-clock-domains/SKILL.md)) — use this to convert VCD timestamps to
    real time, or as a sanity check that the right clock rate is configured.
  - Confirmed empirically: killing the run early with `--max-cycles` (a nonzero-exit, abrupt stop —
    see above) still leaves a well-formed, loadable VCD file truncated at the last traced value
    change — unlike plain buffered `printf` output (above), VCD data is written incrementally, not
    lost. Safe to combine `--max-cycles` with `--vcd-tracing` to bound an otherwise-indefinite run.
- `--gprof` — enables function/statement/address-level profiling; see
  [`xmos-debugging-profiling`](../xmos-debugging-profiling/SKILL.md).
- `--xscope "-offline <file>"` or `--xscope "-realtime <host:port>"` — exercise xSCOPE code paths in
  simulation.
- `--plugin LoopbackPort.dll ...` — loop back two ports to model an external peripheral connection.
- `--stats` — prints per-core instruction counts and switch token counts on exit.

You can also launch the simulator from inside `xgdb` instead of connecting to real hardware, by
running `connect -s` at the `(gdb)` prompt, then loading the program as usual.

## Choosing hardware vs simulation

| Need | Use |
|---|---|
| Real-time/timing-sensitive validation | Hardware (`xrun`) |
| No board available / CI | Simulator (`xsim`) |
| Deterministic, repeatable test runs | Simulator (`xsim`) |
| Fast host I/O / logging | `xrun --xscope` (hardware) |
| Instruction/signal-level tracing | `xsim --trace` / `--vcd-tracing` |
