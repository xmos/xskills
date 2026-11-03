---
name: xmos-xs3-architecture
description: Use when reasoning about XS3 hardware concepts such as tiles, hardware threads/logical cores, the switch/interconnect, channels, ports, hardware timers, locks, the event/interrupt/exception model, the XS3 memory model, the vector unit, or floating point; or when deciding how many parallel tasks a tile can run, what exception a fault corresponds to, or how resources are allocated. Covers the XS3 architecture (XCORE.AI and other XS3-based devices).
---

# XS3 architecture

XS3 is the CPU architecture used by XCORE.AI and other current XMOS devices. It supports general
purpose code, DSP algorithms, AI algorithms, and hard real-time code, side by side.

**Terminology:** XMOS uses **logical core** to mean a **hardware thread**. This guidance
generally uses "thread" for that hardware execution context. A task or job is software
executed on a thread, not another name for the hardware resource. Other execution
models may schedule multiple software tasks on one thread.

**Full reference**: *The XMOS XS3 Architecture* (XM-014007-PS), published as browsable HTML at
<https://www.xmos.com/documentation/XM-014007-PS/html/doc/rst/xs3-arch-inst.html>. It is the
authoritative source for exact instruction encodings, the full ~250-instruction reference
(alphabetical), exception/lane tables, and device-specific resource counts. Fetch it directly when
instruction-level, encoding-level, or exhaustive-list detail is needed — this skill is a curated
summary of the concepts and the facts most useful for writing and reasoning about XS3 software, not a
replacement for it. If the page can't be fetched (network restrictions, URL changed, etc.), say so
explicitly rather than guessing at instruction-level/encoding-level detail, and give the user the URL
to consult directly themselves.

## Core building block: the tile

At its simplest, XS3 comprises an execution unit (scalar ALU for floating point/integer, plus a
vector unit for integer SIMD), a register file, and internal SRAM. Special instructions operate on
**resources** — hardware units (ports, timers, locks, synchronisers) that execute independently of
the instruction stream and can dispatch single-cycle events, which in many cases avoids the cost of
interrupts.

A tile packages memory, one execution unit, resources, and **multiple hardware threads**
together. Each thread has its own complete register file (general registers,
program counter, stack pointer, etc.), so the execution unit can switch between threads with zero
overhead. A tile can be thought of as a symmetric shared-memory multiprocessor: its threads share
the tile's memory, execution unit, and resources, and synchronise via locks/synchronisers. The
exact number of threads, tiles, and resources on a given device is specified in that device's own
datasheet — do not assume a fixed count.

> For the *application-level* mechanics of placing code on specific tiles and passing chanends
> between them, see [`xmos-multi-tile-architecture`](../xmos-multi-tile-architecture/SKILL.md).

## Interconnect: channels, tiles, and the switch

Threads communicate by allocating a **channel-end** resource and creating a **channel** between two
ends. Communication is carried over a **switch** fabric: within a tile the fabric is local, and it
extends off-tile via an **xCONNECT switch**, which can connect to other tiles on the same die or to
other XCORE devices entirely (over **XLINKs**). This is deliberately location-transparent: the same
channel-based code works whether the other end is on the same tile, a different tile, or a
different chip.

XLINKs carry **control tokens** and **data tokens**. Control tokens are grouped by numeric range:
- **0–127 (Application tokens)** — for use by compilers/applications to implement streamed,
  packetised, and synchronised communication (this is where `END`/`PAUSE`, described below, live).
- **128–191 (Special tokens)** — architecturally defined, standard encodings of common data types.
- **192–223 (Privileged tokens)** — system functions (resource sharing, control, debugging);
  transferring one to/from unprivileged software raises an exception.
- **224–255 (Hardware tokens)** — used only by hardware to control the physical link (e.g. credit
  tokens, `HELLO`); software cannot output these.

## Threads and the scheduler

Each XCORE tile provides: per-thread registers, a thread scheduler, synchronisers, channels, ports,
timers, clock generators, and hardware locks. Threads round-robin through a **short pipeline with no
forwarding and no branch prediction/speculation** — this is what makes XS3 timing deterministic and
predictable, unlike a general-purpose out-of-order CPU.

**Instruction fetch:** each XS3 thread has a **256-bit instruction buffer**, holding
sixteen 16-bit or eight 32-bit instructions. Instruction fetches share the pipeline's
memory-access stage with data accesses. Instructions that do not need a data access
can use that stage to fetch instructions; if the buffer is empty when a thread should
issue, a **fetch no-op** refills it, costing an extra thread cycle. Long sequences of
loads/stores can therefore incur fetch overhead; interspersing suitable ALU operations
can provide fetch opportunities. Consult
[Scheduler Implementation](https://www.xmos.com/documentation/XM-014007-PS/html/doc/rst/xs3-arch-inst.html#scheduler-implementation)
for the full rules, including branch-target fetching, rather than assuming every
instruction sequence sustains the same issue rate.

Keep **instruction-buffer width** separate from **memory-interface width**. The XS3
Architecture v2.1.0, **Instruction Issue and Execution**, describes 128-bit-wide memory,
whereas the XU316 datasheet v2.2.0,
[SRAM](https://www.xmos.com/documentation/XM-014035-PC/html/rst/XU316-1024-FB265.html#sram),
describes 256-bit-wide internal memory. These published descriptions disagree; do not
silently reconcile them or infer instruction throughput from either width. Resolve
the applicable interface definition before relying on it in a bandwidth calculation.

**Performance model**: account for the pipeline's minimum issue interval as well as
the number of active threads. One runnable thread does not receive the whole tile's
issue rate. Use the exact device datasheet's **Logical cores** and **xTIME Scheduler**
sections and the architecture manual's priority/fast-mode rules when budgeting work.
For example, the
[XU316 datasheet](https://www.xmos.com/documentation/XM-014035-PC/html/rst/XU316-1024-FB265.html#cores)
documents a one-fifth allocation with up to five active cores and at least `1/n`
above that; priority scheduling changes the guarantees. Keep issue opportunities,
dual-issued instructions and elapsed time distinct. Do not extrapolate an unconditional
`1/n` throughput guarantee to every thread count or scheduling mode.

**Single vs dual issue**: an XS3 pipeline has two lanes — a **memory lane** (memory ops, branches,
basic arithmetic) and a **resource lane** (resource ops, basic arithmetic). A thread running in
**dual-issue** mode executes one 16-bit instruction per lane (or one 32-bit instruction) per thread
cycle (an issue opportunity for that thread) instead of one instruction per cycle; this is controlled by the `DI` bit in the status
register and toggled per-function via `DUALENTSP`/`ENTSP`. This is why compiler output and stack
size reports (see [`xmos-build-system`](../xmos-build-system/SKILL.md) `-report`) sometimes refer to
"lanes" — see the manual's *XCore XS3 Lanes* chapter for which instructions require which lane(s).

**Instruction timing:** use thread cycles as the ordinary instruction-issue model,
accounting for dual issue rather than equating instruction count with tile-clock cycles.
Divider operations can require multiple thread cycles, resource instructions may pause,
and instruction-buffer refills can add fetch cycles. Before estimating execution time,
consult the manual's
[Instruction Issue and Execution](https://www.xmos.com/documentation/XM-014007-PS/html/doc/rst/xs3-arch-inst.html#instruction-issue-and-execution)
section and the relevant instruction entries for execution and pause behaviour.

## Registers

- **Operand registers** `r0`–`r11` — used by arithmetic/logical ops, data access, subroutine calls.
- **Access registers**: `cp` (constant pool pointer), `dp` (data pointer), `sp` (stack pointer),
  `lr` (link register).
- **Control registers**: `pc` (program counter), `sr` (status register).
- **Per-thread special registers**: `spc`/`ssr` (saved pc/status on interrupt/exception), `et`/`ed`
  (exception type/data), `sed` (saved exception data), `kep` (kernel entry point), `ksp` (kernel
  stack pointer).
- **Status register (`sr`) bits worth knowing**: `eeble` (events enabled), `ieble` (interrupts
  enabled), `inenb` (in an event-enabling sequence), `inint` (in interrupt handler), `ink` (kernel
  mode), `waiting` (paused waiting for an event), `fast` (fast I/O mode), `di` (dual-issue mode),
  `kedi` (switch to dual-issue on kernel entry), `hipri` (high-priority thread).

## Resources: allocation and control

Resources (`THREAD`, `SYNC` synchronisers, `CHANEND` channel ends, `TIMER`, `LOCK`) are obtained at
runtime from a pool via a `GETR`-style "get resource" operation and returned via a "free resource"
operation — this is a hard runtime limit, not something checked at compile time, so exhausting a
resource pool is a real failure mode to consider (see
[`xmos-c-programming`](../xmos-c-programming/SKILL.md) for the C wrappers: `hwtimer_alloc`,
`chan_alloc`, etc.). Resources have control **modes** set via a `SETC`-style operation, with common
mode families: `OFF`/`ON` (in-use), `START`/`STOP` (active), `EVENT`/`INTERRUPT` (how the resource
notifies software of a state change).

## Communication (channels)

Channel ends carry data tokens and control tokens; a connection is established on the first output
and terminated by a special **`END`** control token, after which the same channel end can establish
a new route. **`PAUSE`** is a control token used to break up long messages/streams without ending
the connection, letting the interconnect be shared fairly. Channels are full-duplex and buffered
(at least one word); output blocks if the channel is too full, input blocks if not enough data has
arrived yet — this is the hardware-level rendezvous behind the blocking channel API described in
[`xmos-c-programming`](../xmos-c-programming/SKILL.md). Channel ends can also be allocated to one of
several independent logical **networks**, so (for example) short control messages and long data
transfers don't contend with each other.

## Locks

A **lock** resource is claimed with a blocking input and released with an output; a thread that
tries to claim an already-held lock is queued and unblocked in order once it's released. This is
the primitive behind mutual exclusion on XS3 when threads must share a resource that isn't itself
safely divisible between them.

## Timers

Each tile has a 100 MHz free-running **reference clock** and a set of programmable **timers** that
threads can read (current time) or block on (wait until a given time is reached). Ports can also be
driven by one of several **programmable clocks** (rather than the reference clock), with an 8-bit
clock divider, which is how synchronous I/O interfaces (e.g. an external audio clock) are supported
independently of the CPU's own instruction timing.

> 100 MHz is the typical/default reference-clock frequency, not a fixed constant — it is derived
> from the system PLL via a configurable divider and can be changed by the application (XN file or
> PLL registers). See [`xmos-clock-domains`](../xmos-clock-domains/SKILL.md) before assuming a tick
> rate for timing calculations.

## Ports (physical I/O)

Ports connect threads to physical pins. Key concepts:
- A port can be **unbuffered** (transfers synchronised 1:1 with instruction execution) or
  **buffered** (a shift register converts between the port's physical width and a wider software
  transfer width — see `SETTW`/`SETPSC` in the manual for partial-word handling).
- **Ready signalling**: `NOREADY` (no handshake), `STROBED` (one ready signal), `HANDSHAKEN` (both
  directions signal readiness) — plus `MASTER`/`SLAVE` roles.
- A port has an associated **condition** (`NONE`, `EQ`, `NEQ` against a comparison value) that can
  delay input until the pin value satisfies it, with the satisfying value **timestamped** — this
  underlies precise, jitter-free capture of external signals.
- A **port timer** can schedule exactly when the next output/input transition happens, in port-clock
  edges (`SETPT`), useful for precisely timed protocols.

## Memory model

XS3 supports up to three kinds of memory in a single linear address space (exact ranges are
implementation/datasheet-specific): **internal RAM** (code/data, zero-latency access; typically
program low, stack high, data/heap-equivalent in between — though XMOS code should avoid a heap, see
[`xmos-embedded-c-practices`](../xmos-embedded-c-practices/SKILL.md)), **internal ROM** (boot/debug, fixed
entry points), and optionally **external memory** and/or **software-defined memory** (both served
through a small cache — external memory maps a physical external chip; software-defined memory lets
software satisfy cache misses itself, e.g. to execute-from-flash or map data from a remote tile).
External/software-defined memory access is markedly slower than internal RAM, especially under
contention from multiple threads — avoid relying on it for real-time-critical paths.

Spreading an application's data across more than one of these memories (or simply exceeding 256KB
of static data on a tile) has compiler implications too — see the `-mcmodel` memory-model flag in
[`xmos-c-programming`](../xmos-c-programming/SKILL.md).

## Events, interrupts, and exceptions

- **Events**: a thread enables events on chosen resources (`SETV` sets the handler address,
  optionally `SETEV` sets an environment pointer) then waits (`WAITEU`/`WAITET`/`WAITEF`). On an
  event, thread state is fully valid (nothing was mid-instruction), so handling can be very fast and
  resume the same handler immediately — this is the hardware basis for the C `select` idiom in
  [`xmos-c-programming`](../xmos-c-programming/SKILL.md). Disable all of a thread's events at once
  with `CLRE`.
- **Interrupts**: unlike events, can occur *between* any two instructions; `pc`/`sr` are saved to
  `spc`/`ssr` automatically and the processor enters kernel mode.
- **Exceptions**: hardware-detected errors (or software-forced via `ECALLT`/`ECALLF`/`ELATE`)
  transfer control to a fixed offset from the thread's **kernel entry point** (`kep`), setting `et`
  (exception type) and `ed` (exception data). Useful exception types to recognise when debugging
  a trap (`et` value in parentheses): `ET_LINK_ERROR` (1, bad channel use), `ET_ILLEGAL_PC` (2,
  unaligned/invalid PC), `ET_ILLEGAL_INSTRUCTION` (3), `ET_ILLEGAL_RESOURCE` (4, bad/unowned
  resource), `ET_LOAD_STORE` (5, misaligned memory access), `ET_ILLEGAL_PS` (6), `ET_ARITHMETIC` (7,
  e.g. divide-by-zero or FP NaN/infinity trap), `ET_ECALL` (8, failed assertion), `ET_RESOURCE_DEP`
  (9, resource illegally shared between threads), `ET_KCALL` (15, explicit kernel call). `ET_IOLANE`
  (16) is OR'd into any of the above to indicate the fault was in the resource lane.
- **`ET_ECALL` is raised by any `__builtin_trap()` call, not just a failed `assert(...)`** —
  confirmed by building and running `lib_xassert`'s three purpose-built example apps
  (`app_assert`, `app_fail`, `app_unreachable`) on real XK-EVK-XU316 hardware: `assert(...)`,
  `fail(...)`, and `unreachable(...)` (when assertions are enabled for that `XASSERT_UNIT`) all
  compile to `__builtin_trap()` and all three raised `ET_ECALL` identically, both as
  `xrun: Program received signal ET_ECALL, Application exception.` and as xgdb's
  `Catchpoint -1 (XCore Exception ET_ECALL)`. Note `fail(...)` is unconditional — unlike
  `assert(...)`/`unreachable(...)`, it is not gated by `XASSERT_ENABLE_ASSERTIONS` and always traps.

## Specialised instructions

- **Long/extended arithmetic**: multi-word add/subtract with carry/borrow (`LADD`/`LSUB`),
  multiply-accumulate (`MACCU`/`MACCS`, `LMUL`, `LDIVU`), saturation (`LSATS`), and bit
  extract/insert across a register pair (`LEXTRACT`/`LINSERT`) — useful for implementing wider
  arithmetic or fixed-point DSP kernels in C.
- **CRC**: hardware cyclic redundancy check instructions (`CRC`, `CRC8`, `CRCN`, `CRC32_INC`) for
  efficient checksums over byte/word streams.
- **Floating point**: `FADD`/`FSUB`/`FMUL`/`FMACC` (IEEE 754, `roundTiesToEven`), plus
  `FSPEC`/`FENAN`/`FMANT`/`FSEXP`/`FMAKE` for dissecting/reassembling a float and `FGT`/`FLT`/`FEQ`/
  `FUN` for exception-free comparisons. `FMANT`/`FSEXP` trap (`ET_ARITHMETIC`) on NaN/infinity input,
  so check with `FSPEC` first if the value could be a special case.
- **Vector unit**: three vector registers `vC` (coefficients), `vD` (data), `vR` (result/output),
  plus a control/status register `vCTRL` (element type — 8/16/32-bit signed integer — and headroom
  tracking). The vector width (`bpv`) is implementation-defined; on XS3/XCORE.AI it is 256 bits, but
  always confirm against the target device's datasheet before relying on this value in a
  calculation. It is optimised for convolution/FIR, complex multiplication, and FFTs
  (dedicated decimate-in-time/frequency instructions), with built-in saturation and rounding on
  every arithmetic op. This is the hardware DSP/ML acceleration referenced by "AI algorithms" in the
  architecture's stated purpose — relevant when a task involves audio/ML kernels that might benefit
  from vectorised C libraries rather than hand-written scalar loops (see
  [`xmos-numeric-programming`](../xmos-numeric-programming/SKILL.md)).
  - Confirmed against `lib_xcore_math` v2.4.0 (the library that directly wraps this unit):
    `XS3_VPU_VREG_WIDTH_BITS` is literally defined as `256` in its `xmath/xs3/vpu_info.h`, with
    per-vector element counts `VPU_INT8_EPV=32`, `VPU_INT16_EPV=16` (and `VPU_INT32_EPV=8`) matching
    256 bits / element-width exactly — the 256-bit figure above is accurate, not just a rule of
    thumb. Built and ran `app_bfp_demo`/`app_vect_demo` (block-floating-point and vector/array APIs)
    plus the library's own `vect_tests` Unity suite (182/182 passing) on real XK-EVK-XU316 hardware,
    validating the mantissa/exponent (BFP) model these vector ops are built on top of end-to-end.

## Debug and initialisation

Debugging is entered via `DCALL`, a triggered watchpoint/breakpoint, or an external debug signal;
only thread 0 runs the debug handler while all other threads freeze,
and `DRET` resumes everything.
This hardware-level mechanism is what `xgdb` drives — see
[`xmos-debugging-profiling`](../xmos-debugging-profiling/SKILL.md) for the practical, tool-level
workflow (breakpoints, multi-tile inspection, profiling) rather than the raw instructions.

## When to fetch the full manual

Fetch the HTML manual
(<https://www.xmos.com/documentation/XM-014007-PS/html/doc/rst/xs3-arch-inst.html>) directly rather
than guessing when you need: the exact encoding/operands of a specific instruction, the complete
alphabetical instruction reference (~250 instructions), the full exception table with which
instructions can raise which exception, or the lane classification of a specific instruction for
dual-issue reasoning.
