---
name: xmos-multi-tile-architecture
description: Use when structuring a multi-tile XMOS application -- placing task entry-points on specific tiles (tile[N]), passing chanends between tiles, choosing/writing a top-level multi-tile XC file, accessing I/O owned by another tile, choosing regular or streaming channels between tiles, or understanding why C alone cannot express tile placement. Covers XTC Tools 15.3.1.
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

`par` waits for all its tasks to return. Service tasks that loop forever are normal in embedded
applications and keep the application running indefinitely.

Tile placement must match the hardware topology described by the project's selected target or XN
file. Use the existing project target; see [`xmos-build-system`](../xmos-build-system/SKILL.md) for
target selection.

## Declaring a channel between tiles

Add a `chan` in the multi-tile file and pass it to each tile-level entry point; the tools
automatically allocate one chanend per entry-point that uses it and route it over the interconnect
(see [`xmos-xs3-architecture`](../xmos-xs3-architecture/SKILL.md) for the switch/xCONNECT/XLINK concepts this
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

**Each tile has its own local RAM.** Tasks on the same tile can share that memory with appropriate
synchronisation and lifetime management. Passing a pointer through a channel does not make one
tile's local RAM directly accessible from another tile: transfer the required data through
channels, or use an explicitly supported remote-memory mechanism (see the memory model in
[`xmos-xs3-architecture`](../xmos-xs3-architecture/SKILL.md)).

## Regular vs streaming channels between tiles

- **Regular channels** (`chan_*`) handshake with control tokens on each transfer, which ends the
  route through the interconnect between transfers.
- **Streaming channels** (`s_chan_*`) omit that per-transfer handshake and hold their route open
  until freed, so they consume interconnect routing capacity that other cross-tile traffic may need.
- Both can block when the other end isn't ready; streaming is not asynchronous or unlimited
  buffering. Both ends must use the same channel type and protocol.

See [`xmos-c-programming`](../xmos-c-programming/SKILL.md) for the APIs and the
[architecture manual](https://www.xmos.com/documentation/XM-014007-PS/html/doc/rst/xs3-arch-inst.html)
for interconnect routing.

## Accessing I/O on another tile

Hardware ports belong to a specific tile. A task cannot directly operate a port on another tile by
passing its port identifier across tiles.

Place the I/O-owning task on the tile with the required ports. Tasks on other tiles communicate
requests and results with that task through channels, or through an XC interface where the existing
application uses one. For new C/lib_xcore code, use channels between the tile-local tasks, with the
top-level XC placement code connecting their endpoints. Launch the tasks concurrently in the same
`par`, and follow the communication protocol's synchronisation and ownership rules.

## When this doesn't apply

A **single-tile** application needs no multi-tile XC file at all — a plain C `main()` is sufficient
(see [`xmos-c-programming`](../xmos-c-programming/SKILL.md) for structuring parallel tasks *within*
one tile via `PAR_JOBS`). Only reach for a multi-tile XC file when entry points must run on more
than one tile.
