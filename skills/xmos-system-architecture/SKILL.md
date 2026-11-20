---
name: xmos-system-architecture
description: Use when designing or reviewing the architecture of an XCORE application -- deciding how to map a design onto hardware threads and tiles, splitting a system into compute/IO/control tasks, deciding whether a task needs its own hardware thread or can be a function call or share a thread, planning the IO/port-to-tile map, choosing channels vs shared memory (ping-pong buffers) between tasks, or choosing bare metal vs RTOS.
---

# Mapping a design onto the XCORE

A design-method skill: how to turn system requirements into tasks, hardware threads and tiles.
It is heuristic guidance from XMOS engineering experience, **not a verified specification**; check
resource limits against the device datasheet and the XS3 architecture manual
(see [`xmos-xs3-architecture`](../xmos-xs3-architecture/SKILL.md)). The XCORE sits between an MCU
and an FPGA, so several valid architectures usually exist.

## Step 1: Identify functional blocks

- **Compute**: usually isochronous (e.g. a DSP pipeline) with a hard deadline, sometimes bursty
  (e.g. compression). Record the **period** of every task; in a DSP pipeline it is often common.
- **IO**: which peripherals talk to the outside world. Mostly hard real-time. Classify each as
  *slave* (reacts to the outside world; usually its own task) or *master* (drives the transaction;
  can sometimes be an in-line function call).
- **Control**: orchestration, from low-level control loops to high-level application, including
  low-rate GPIO such as buttons and LEDs.

## Step 2: Map onto XCORE resources

Start with the toughest constraints and work downwards ("big rocks first"). A hardware thread
(logical core) is a bucket of MIPS.

**Compute**
- Fits in one hardware thread: map directly.
- Uses a fraction of a thread: pack several tasks into one thread (call in sequence, a simple
  scheduler, or an RTOS).
- Thread priority/scheduling settings influence the MIPS each thread receives.
- Needs more than one thread to meet its deadline: manually split into a pipeline or parallel
  units. This is the classic multiprocessing problem and can be costly; do it only when needed.

**IO**
- Split by master/slave and by timing. Separate the **data plane** (high throughput, often
  continuous) from the **control plane** (low rate, sparse).
- Low-MIPS but always-responsive slaves (e.g. I2C slave) normally get their own thread.
- Periodic, low-MIPS interfaces (e.g. I2S) normally get their own thread; spare time is often
  used for same-rate DSP or control inside its callbacks.
- Low-speed master IO can often be a function call. Unlike on an MCU, a blocking port output (e.g.
  a UART byte) does not return until the last transition completes; account for this in timing.

**Control**
- Give it its own thread (with a `select` loop or periodic scheduler), weave it into other tasks,
  or preferably use an RTOS. In XC, combinable tasks flatten several `while(1) select` tasks into
  one thread; `lib_xcore` has no equivalent (see
  [`xmos-c-programming`](../xmos-c-programming/SKILL.md)).

## Step 3: Plan IO-to-port/tile mapping early

Port allocation fixes IO functions to tiles, so do it early against the *complete* requirements
and keep data sources and sinks close to their producers/consumers. Late changes lead to
workarounds. See [`xmos-pin-mapping`](../xmos-pin-mapping/SKILL.md).

If producer and consumer are on different tiles, a channel is the only communication path
(without looping IO pins back). Inter-tile circuits are limited in number (check the datasheet
for the device), so consider bandwidth, timing and the maximum tolerable back-pressure on each
side. Streaming channels suit high-bandwidth, low-back-pressure flows (switch buffering helps
decouple); regular packet channels (circuit set up and torn down per transfer) suit control data.
See [`xmos-multi-tile-architecture`](../xmos-multi-tile-architecture/SKILL.md).

## Step 4: Choose inter-task communication

Decouple time-critical IO from its consumer where possible.

| Mechanism | Trade-off |
|---|---|
| Pure channels | Easy to reason about; blocking can cause timing problems. |
| Shared memory with flags/buffers | Needs polling instead of events, which is less energy efficient. |
| RTOS primitives | Convenient; can be limiting for frequent sample-by-sample transfers (block-based transfers are less frequent and suit it better). |
| Channel passing a pointer to a shared buffer pool (bare metal) | Efficient and robust; use non-blocking channel primitives (within limits) and normally a double (ping-pong) buffer. |

Across tiles only channels can be used, which may need proxy/decoupler tasks.

## Language and execution model

- New code is rarely written in XC; use `lib_xcore` from C, accepting that it is lower level and
  cannot combine `select` statements. Tile placement still needs a small XC top-level file.
- Bare metal, RTOS and hybrid each have pros and cons and there is no single company-wide
  preference; choose pragmatically for the application and state the reason.

## Checklist before committing to an architecture

1. Every task has a stated period/deadline and a thread (or packing) assignment.
2. Total thread count fits the tile, with margin for MIPS-sensitive tasks.
3. Every port is assigned to a tile and every cross-tile flow has a channel with known bandwidth
   and back-pressure behaviour.
4. Each inter-task link has a chosen mechanism and a justification.
