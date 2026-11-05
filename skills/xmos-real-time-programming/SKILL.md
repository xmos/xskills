---
name: xmos-real-time-programming
description: Use when writing or reviewing real-time code for XMOS/XCORE for general correctness and safety -- timers, port-clocks, avoiding skidding, decoupling xcore-timing and I/O timing, avoiding unintended blocking in time-critical paths, maximising concurrency.
---

# Real-time programming for XMOS

General real-time programming, specialized for why it matters on XS3/XCORE specifically. This skill
owns timer scheduling and real-time design reasoning. Related skills cover the rest:

- [`xmos-c-programming`](../xmos-c-programming/SKILL.md) — timer, port and `select` APIs and
  handler behaviour.
- [`xmos-clock-domains`](../xmos-clock-domains/SKILL.md) — establishing the actual reference and
  port-clock sources and frequencies.
- [`xmos-xs3-architecture`](../xmos-xs3-architecture/SKILL.md) — thread issue rates, ports and
  memory/channel mechanisms.
- [`xmos-debugging-profiling`](../xmos-debugging-profiling/SKILL.md) — measuring execution time.
- [`xmos-testing`](../xmos-testing/SKILL.md) — validating deadlines and stressing interfaces.

## The wall-clock

Hardware timers count ticks of the reference clock (100 MHz by default; use the configured
frequency, see [`xmos-clock-domains`](../xmos-clock-domains/SKILL.md)) in a 32-bit counter, which
wraps every 2^32 ticks — approximately 42.95 seconds at 100 MHz. A thread can wait for a timer to be
*after* a specific time by setting the trigger `hwtimer_set_trigger(tmr, time)` and subsequently
inputting from the timer. Using a select construct enables the program to implement time-outs.

The "after" comparison only works within half that range: a deadline up to 2^31 ticks in the future
is waited for, and anything up to 2^31 ticks in the past counts as already passed. To wait longer
than 2^31 ticks (about 21.47 seconds at 100 MHz), split the wait into shorter slices. This is a
different limit from elapsed-time measurement, where unsigned subtraction handles counter rollover
provided the elapsed interval is strictly less than 2^32 ticks (see
[`xmos-debugging-profiling`](../xmos-debugging-profiling/SKILL.md)).

The 100 MHz timer is synchronous to the external clock supplied on XIN, and
hence multiple tiles or dies that run on the same external clock will have
synchronous timers with only an offset between them.

## Avoid skidding

FOr a program to run synchronous to the wall clock, always maintain a
variable with the next time that an event should happen, and add a precise
offset to that event. For example, to bit-bang a 1 MHz
signal add 50 to the timer, wait for the timer, and output a 1, then add 50
to the timer, wait for the timer and output a 0. It is tempting to
reinitialise the variable from the wall-clock, but this would deviate from
1 Mhz as errors would accumulate. Errors here never accumulate.

In case where the offset is a rational number, the
program should add a fractional value.

## Port clocks

Ports can be clocked from an external clock signal, or from a clock
generated internally. For example, one can output a signal on a port
relative to an external 24.576 MHz clock that is asynchronous to the clock
input into the XCORE on the XIN pin. By outputting signals on that clock,
the XCORE software has to be *fast enough* to meet the deadline. If it is
early, the output waits until the port can accept the data.

Port clocks decouple pin timing from software execution timing. Software must supply or consume
data before the relevant port/buffer deadline. Buffering can allow other work between transfers,
provided the interface's timing requirements remain satisfied. See the ports section of
[`xmos-xs3-architecture`](../xmos-xs3-architecture/SKILL.md) and the port/clock-block API
documentation for the detailed contracts. Software can be artificially slowed down (by adding more tasks, or by
lowering the clock speed of the processor) in order to save power or
increase functionality.

## Thread interaction

When a pipeline or more complex network of threads interact with real-time
inputs and outputs, ensure that they all run to the same beat, or you must
put an asynchronous handover in. 

If they all run to the same beat, make sure that all threads start busy,
and hence run in parallel. They go through a phase of compute, and then a
phase where data is handed across between them. Channels can be used to
communicate between the threads, or synchronisers can be used in
conjunction with shared memory if the threads are on the same tile.

If threads are asynchronous to each other, the program must implement some
sort of asynchronous hand-over. This can take many forms, including a
thread implementing a buffer with two channels to producer and consumer, or
an event-loop that accepts data from different sources. Each of these have
different jitter and bandwidth properties. 

## Combining tasks into a single event-loop

Multiple slow tasks can be ran into a single `while(1)` event loop that
events on different ports, channels, and hardware-timers. Each case in the
event loop has an associated run-time for that case, and an expected amount
of time that this case is used.

The system runs out of bandwidth when the sum or products of run-time and
rate for each case exceeds the amount of compute available in a single
thread. For example, if one case is used at at most 100 kHz and takes 100
issue slots to complete, and another case uses at most 500 issue slots at
10 kHz then the total bandwidth requirement is 10 million plus 5 million is
15 million issue slots per second; which is easily met with a 75 MIPS
thread. 

The system will miss events due to jitter if the total time of all events
that may happen exceeds the time in which an event should be dealt with. In
the case above, assuming each handler runs once, neither blocks, and no
further events arrive during servicing, both events complete within 600
issue slots. Check repeated arrivals and each event's deadline separately;
sufficient average processing capacity alone does not guarantee acceptable
latency. In general, each case has a contract with a maximum required issue
rate and a maximally acceptable latency that should be met. Convert issue
slots to elapsed time using the thread's issue rate (see
[`xmos-xs3-architecture`](../xmos-xs3-architecture/SKILL.md)).

