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

**`xsim` is not real-time — it runs slower than real hardware.** Use it for functional testing,
determinism, and tracing, not for validating real-time/timing behavior; use real hardware (`xrun`)
for that.

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
- `--trace` / `-t` — full instruction trace to stdout (or `--trace-to <file>`); e.g. grepping the
  trace can show exactly which tile executed a given syscall.
- `--vcd-tracing "-o file.vcd -tile tile[0] -ports|-cycles|-clock-blocks|-cores|-instructions"` —
  signal-level tracing to a VCD file, viewable in a waveform viewer such as GTKWave.
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
