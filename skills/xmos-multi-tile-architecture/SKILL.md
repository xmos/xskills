---
name: xmos-multi-tile-architecture
description: Use when structuring a multi-tile XMOS application -- placing task entry-points on specific tiles (tile[N]), passing chanends between tiles, choosing/writing a top-level multi-tile XC file, or understanding why C alone cannot express tile placement. Also use when a project needs an .xn hardware-description file for a multi-tile target. Covers XTC Tools 15.3.1.
---

# Multi-tile application structure

An XS3 device with more than one tile (e.g. XCORE.AI, XK-EVK-XU316) requires a **top-level,
multi-tile XC file** to specify which entry-point function runs on which tile, and to declare any
channels connecting them. **This is the one place XC remains required** even though C is otherwise
preferred (see [`xmos-c-programming`](../xmos-c-programming/SKILL.md)): tiles are independent
processors, and **it is not possible to express tile placement in the C language** — only XC's
declarative `on tile[N]:`/`par` syntax can do it. Keep this file minimal (placement + channel
declarations only) and put all real logic in plain C functions it calls into.

## Minimal multi-tile file

```c
// multitile.xc
#include <platform.h>

extern "C" {
    void main_tile0();
    void main_tile1();
}

int main(void)
{
    par {
        on tile[0]: main_tile0();
        on tile[1]: main_tile1();
    }
    return 0;
}
```

```c
// main.c
#include <stdio.h>

void main_tile0(void) { printf("Hello from tile 0\n"); }
void main_tile1(void) { printf("Hello from tile 1\n"); }
```

Build and run like any other application (see
[`xmos-build-system`](../xmos-build-system/SKILL.md), [`xmos-run-and-simulate`](../xmos-run-and-simulate/SKILL.md)):

```sh
xcc -target=XK-EVK-XU316 multitile.xc main.c
xrun --io a.xe
```

The `extern "C"` block forward-declares the C entry points so the XC file can reference them; the
functions themselves are ordinary C, compiled and reasoned about like anything else in
[`xmos-c-programming`](../xmos-c-programming/SKILL.md).

## Declaring a channel between tiles

Add a `chan` in the multi-tile file and pass it to each tile-level entry point; the tools
automatically allocate one chanend per entry-point that uses it and route it over the interconnect
(see [`xs3-architecture`](../xs3-architecture/SKILL.md) for the switch/xCONNECT/XLINK concepts this
relies on):

```c
// multitile.xc
#include <platform.h>

typedef chanend chanend_t;

extern "C" {
    void main_tile0(chanend_t);
    void main_tile1(chanend_t);
}

int main(void)
{
    chan c;
    par {
        on tile[0]: main_tile0(c);
        on tile[1]: main_tile1(c);
    }
    return 0;
}
```

```c
// main.c
#include <xcore/channel.h>

void main_tile0(chanend_t c)
{
    chan_out_word(c, 123);
}

void main_tile1(chanend_t c)
{
    int v = chan_in_word(c);
}
```

The `chanend` type declared in the XC file is ABI-compatible at link time with lib_xcore's
`chanend_t`, so the C side uses the normal `chan_out_word`/`chan_in_word`/`select` APIs from
[`xmos-c-programming`](../xmos-c-programming/SKILL.md) — nothing tile-crossing-specific is needed
once the chanend is in hand.

## Hardware targets and `.xn` files

`-target=<board-name>` (e.g. `XK-EVK-XU316`) selects a known board's tile/pin topology. For a custom
board, or when the target should be pinned explicitly and reproducibly, pass an `.xn` hardware
description file as a build input instead — see
[`xmos-build-system`](../xmos-build-system/SKILL.md) for the CMake `APP_HW_TARGET` variable and
`xcc` invocation.

## Board-init pattern: a peripheral bus is owned by one tile

Board-support libraries commonly wire a shared peripheral bus (e.g. the on-board I2C bus used to
configure an audio codec/PLL) to pins on only **one** tile. Any code running on a *different* tile
that needs to use that bus cannot access it directly — the board-support library instead splits
into a **remote server task** (runs on the tile that owns the bus, e.g. `..._AudioHwRemote(c)`) and
**client calls** the other tile makes over a chanend (e.g. `..._AudioHwInit(&cfg)`,
`..._AudioHwConfig(...)`), with the server relaying the actual I2C transactions. Two consequences to
get right in application code:

- Start the remote server task *before* any client tile calls into the library, and don't forget the
  channel connecting them — same rules as any other cross-tile call (see above).
- The server task normally loops forever servicing requests, so the client must send an explicit
  "exit" command over the same chanend (e.g. `chan_out_word(c, AUDIOHW_CMD_EXIT)`) once done, or the
  server tile's entry function will never return and the `par` will hang waiting for it.

This pattern was confirmed working end-to-end on real hardware via `lib_board_support`'s
`app_evk_316_simple_c` example (tile 0 runs the I2C remote server, tile 1 initialises/configures the
board's audio hardware then sends the exit command) — the same shape applies to any board-support
library that centralises a shared bus on one tile.

## When this doesn't apply

A **single-tile** application needs no multi-tile XC file at all — a plain C `main()` is sufficient
(see [`xmos-c-programming`](../xmos-c-programming/SKILL.md) for structuring parallel tasks *within*
one tile via `PAR_JOBS`). Only reach for a multi-tile XC file when entry points must run on more
than one tile.
