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

### Prefer `--xscope` for host output; `--io` is a fallback

Prefer `xrun --xscope a.xe` whenever the application and board can support it. Use
`xrun --io a.xe` only when xSCOPE cannot be used. Select the command to match the build
configuration and board wiring; see
[`xmos-printing-logging`](../xmos-printing-logging/SKILL.md#prefer-xscope-for-host-text-output)
for the transport tradeoffs and text-I/O setup.

For structured xSCOPE probes, see
[`xmos-debugging-profiling`](../xmos-debugging-profiling/SKILL.md#xscope-data-probes).

```sh
xrun --xscope a.xe
```

Add `--xscope-file xscope.vcd` when capturing probe data to a file.

### `--io`/`--xscope` block until the program exits — a problem for long-running device apps

Both `--io` and `--xscope` keep `xrun` attached and **waiting for the target program to
terminate** before returning control (this is what makes them useful for capturing output at all).
For a program that runs to completion this is fine, but many real XMOS applications — e.g. a USB
audio device reference design — are designed to run **indefinitely**, streaming/servicing the host
forever under normal operation. Run one of those with `--io`/`--xscope` and `xrun` will simply never
return, which will hang a script, an agent's synchronous tool call, or a terminal waiting for the
prompt back. This can be expected, but does not establish correct execution: a deadlock
or unexpected wait can look the same. Define a progress marker, expected output/state
or other task-specific observation before treating the run as successful.

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
| `xrun --io`/`--xscope` command produces no output and never returns control | May be expected for an indefinite application, but is not proof of correct execution. Check expected progress, I/O configuration and whether tasks are blocked; see the lifetime discussion above. |


## `xsim`: simulating without hardware

`xsim` provides a near cycle-accurate software model of one or more XCORE devices — useful when no
board is available, for deterministic/reproducible test runs, or for generating traces the
simulator alone can produce.

```sh
xsim a.xe
```

**Simulator wall-clock runtime is not target execution time.** A simulation can run much slower
than hardware while still providing useful simulated cycle and instruction traces. The
[XTC 15.3 xsim manual](https://www.xmos.com/documentation/XM-014363-PC/html/tools-guide/tools-ref/cmd-line-tools/xsim-manual/xsim-manual.html)
describes a **near cycle-accurate** model, instruction/machine-state tracing and peripheral
loopbacks. Use those facilities for analysis within the configured model; do not treat the host's
elapsed time as a target performance measurement or assume unmodelled peripherals are validated.
Use hardware (`xrun`) to validate real peripheral timing and end-to-end system behaviour.

Source verified against the installed XTC Tools 15.3.1 manual at
`doc/html/tools-guide/tools-ref/cmd-line-tools/xsim-manual/xsim-manual.html`.

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

### Output and buffering in simulator tests

Hardware host-I/O runs use `xrun --xscope a.xe` (preferred when configured) or
`xrun --io a.xe` (fallback). For ordinary simulated standard I/O, use `xsim a.xe`
without those hardware I/O flags. To exercise xSCOPE in simulation, use the simulator's
own `--xscope` syntax, for example `xsim --xscope "-offline xscope.vcd" a.xe`. Consult the
[XSIM tutorial](https://www.xmos.com/documentation/XM-014363-PC/html/tools-guide/tutorials/using-xsim.html)
for simulated host I/O and xSCOPE options.

For API selection and buffering, use
[`xmos-printing-logging`](../xmos-printing-logging/SKILL.md), rather than selecting a printing
API as a workaround for a simulator run limit.

For an output-based test, define the expected text and arrange for it to be emitted within the
simulated interval. Missing output alone does not establish that a code path was not reached;
check logging enablement, buffering, the selected I/O path and whether the task made progress.
Conversely, reaching a cycle limit does not prove progress or freedom from deadlock. No printing
API guarantees that output will be delivered before an external stop.

### Bound runs of indefinite applications

`xsim` does not impose a default cycle limit. An application designed to run indefinitely
needs an explicit stopping condition in an automated test; lack of termination alone does not
distinguish a healthy service loop from a deadlock.

- Before running an unfamiliar/indefinite example under `xsim`, always pass `--max-cycles <n>` (see
  below) to guarantee it returns.
- When scripting/automating `xsim` runs (e.g. from an agent's synchronous tool call), also apply an
  independent process-level timeout as a second line of defense in case the app happens to be
  bounded by something other than cycle count.

Useful options:

- `--max-cycles <n>` — exit when `n` simulated system cycles is reached, as described in the
  [XSIM manual](https://www.xmos.com/documentation/XM-014363-PC/html/tools-guide/tools-ref/cmd-line-tools/xsim-manual/xsim-manual.html#cmdoption-xsim-max-cycles).
  Treat reaching the bound as a run limit, not by itself a functional pass or failure.
  Check the exit status and diagnostics, distinguish a limit from an exception, and evaluate
  the test's required observations. If completion was required and did not occur, the run
  has not passed.
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
  as GTKWave. For global and per-tile options, consult the
  [XSIM tracing reference](https://www.xmos.com/documentation/XM-014363-PC/html/tools-guide/tools-ref/cmd-line-tools/xsim-manual/xsim-manual.html#cmdoption-xsim-vcd-tracing).
  - Example: `xsim --vcd-tracing "-o trace.vcd -tile tile[1] -ports -cycles" a.xe`.
    Use the tile name from the selected XN file. Quote the tracing arguments as one string.
  - Use `-start-disabled` with `_traceStart()` / `_traceStop()` to restrict tracing to the
    interval of interest and reduce trace volume.
  - Read the generated VCD's `$timescale` to interpret timestamps; do not hard-code a time
    unit or confuse VCD timestamp units with tile cycles. For cycle-to-time conversion, use
    the configured tile clock; see [`xmos-clock-domains`](../xmos-clock-domains/SKILL.md).
  - A bounded or interrupted trace is partial evidence. Check that the file loads and covers
    the required interval; do not assume every early stop leaves a complete, valid VCD file.
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
| Real peripheral timing / end-to-end hardware validation | Hardware (`xrun`) |
| Simulated cycle/instruction analysis within the model | Simulator (`xsim`), then hardware where required |
| No board available / CI | Simulator (`xsim`) |
| Deterministic, repeatable test runs | Simulator (`xsim`) |
| Fast host I/O / logging | `xrun --xscope` (hardware) |
| Instruction/signal-level tracing | `xsim --trace` / `--vcd-tracing` |
