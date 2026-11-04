---
name: xmos-real-time-programming
description: Use when writing or reviewing real-time code for XMOS/XCORE for general correctness and safety -- timers, port-clocks, avoiding skidding, decoupling xcore-timing and I/O timing, avoiding blocking threads, maximising concurrency.
---

# Real-time programming for XMOS

General real-time programming, specialized for why it matters on XS3/XCORE specifically. See
[`xmos-c-programming`](../xmos-c-programming/SKILL.md) for the XMOS-specific `lib_xcore` APIs these
practices apply to.

## The wall-clock

XMOS provides hardware-timers that give the program a time with a 100 MHz
clock measured in 32-bit timers that wrap every 40 seconds. A thread can
wait for a timer to be *after* a specific time by setting the trigger
`hwtimer_set_trigger(tmr, time)` and subsequently inputting from the timer.
Using a select construct enables the program to implement time-outs.

The waiting after enables to wait up to 2^31 timer ticks into the future;
the 2^31 timer ticks in the past are assumed 'after'. If a program needs to
wait for more than 2^31 timer ticks then it should be cut into slices of 20
seconds or less.

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
early, the program will be clocked until the data can be output. It is
possible to perform other tasks between outputs as long as the output is
just in time; a few core-clocks before the data must go out onto the wire.

This practice of using port-clocks decouples software speed from IO speed.
As long as the software is fast enough the system will operate faultless.
Software can be artificially slowed down (by adding more tasks, or by
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
the case above, all cases should be able to cope with 600 issue slots
delay. In general, each case has a contract with an maximum required issue
rate and a maximally acceptable latency that should be met.

