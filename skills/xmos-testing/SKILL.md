---
name: xmos-testing
description: Use when writing, extending or reviewing tests for XMOS software -- C unit tests with lib_unity, Python/pytest simulator testbenches with test_support (Pyxsim), choosing between host, simulator and hardware testing, defining pass/fail criteria for concurrent or indefinitely-running code, or testing timing and numerical behaviour.
---

# Writing tests for XMOS software

To find and run a repository's existing tests, see
[test workflow discovery](../xmos-project-structure/SKILL.md#identify-the-test-workflow-before-running-tests).
This skill covers designing and writing them.

## Use the XMOS test infrastructure

When maintaining a repository, follow its existing framework, fixtures and dependency versions;
do not migrate established tests unnecessarily. For new tests:

- **[`lib_unity`](https://github.com/xmos/lib_unity)** — C unit tests. It adapts the Unity
  framework for XCommon CMake: add it to `APP_DEPENDENT_MODULES` and write tests with Unity's
  assertions (`TEST_ASSERT_*`), optionally using its fixture extras (`TEST_GROUP`/`RUN_TEST_CASE`).
  Its `LIB_UNITY_AUTO_TEST_RUNNER` option generates a runner per build configuration (one `test_*`
  source per configuration; requires Ruby).
- **[`test_support`](https://github.com/xmos/test_support)** — Python/pytest infrastructure for
  simulation. Its `Pyxsim` package runs `xsim` from pytest, drives and samples simulated ports
  through simulator threads (`Pyxsim.SimThread`), compares output against expected files, reads XE
  metadata and processes trace-based coverage.

They are complementary: target code built with `lib_unity` or ordinary applications can be run and
checked by pytest using `test_support`. Pin the versions used (for `test_support`, in the test
`requirements.txt`) and run Python tooling in a virtual environment. Consult the selected
versions' README, documentation and `examples/` for setup and APIs rather than guessing them; the
`lib_unity` `examples/` and an existing library's `tests/` directory are good templates.

**Prefer running Pyxsim tests through pytest**, using the repository's fixtures and configuration,
and select a specific test file, test or parametrised case where possible (for example
`python -m pytest tests/test_example.py -v`). Use a standalone script only when the repository
documents it as the intended entry point.

## Python testbenches for hardware interfaces

Pyxsim lets Python drive and sample the simulated XCORE's I/O, so a test can model the external
device on the other side of an interface. This is especially useful when implementing hardware
interfaces: the testbench can deliberately produce timing boundaries, unusual sequences and error
conditions that rarely occur on real hardware, and check the application's response.

- The Python testbench controls the simulator, advancing it through XSI.
- **Simulator threads** (`Pyxsim.SimThread`) describe stimulus and checks. They yield until a time
  or I/O condition is met (for example `wait_for_port_pins_change()`, `wait_until()`) and drive or
  sample pins through `self.xsi`, rather than advancing the simulator themselves.
- **Plugins** registered with the simulator receive a `clock(xsi)` callback each time it advances.

When modelling shared or open-drain lines, read the guide's XSI port-sampling warning and use its
resolved bus model rather than reasoning about pin state ad hoc. References, for the version the
project uses:

- [`test_support` guide](https://github.com/xmos/test_support/blob/develop/doc/rst/test_support.rst)
  — pytest usage, simulator threads, pin access, bus model and tracing.
- [`examples/pyxsim`](https://github.com/xmos/test_support/tree/develop/examples/pyxsim) — a
  testbench reacting to and driving port changes.
- [`Pyxsim/pyxsim.py`](https://github.com/xmos/test_support/blob/develop/Pyxsim/pyxsim.py) — plugin
  and simulator-thread scheduling, which the guide covers less fully.

## Choose where each test runs

| Level | Use for |
|---|---|
| Host (native build or Python) | Portable logic, reference models and numerical comparison |
| Simulator (`xsim`, `test_support`) | XCORE APIs, resources, threads and channels; protocols driven through simulated ports |
| Hardware | Physical peripherals, real timing and end-to-end behaviour |

Simulator wall-clock time is not target time, and unmodelled peripherals are not validated by
simulation; see [`xmos-run-and-simulate`](../xmos-run-and-simulate/SKILL.md). Keep simulator tests
small, since simulation is much slower than hardware.

## Make results observable and bounded

- Define explicit pass/fail criteria: assertions, an expected-output comparison or checked state. A
  successful build, silence, or reaching a cycle limit is not a pass.
- Bound every run (for example `--max-cycles` plus a process timeout) and make finite tests
  terminate. For code that normally runs indefinitely, check a defined observation within the
  bound rather than waiting for exit.
- For concurrent code, start every channel peer and fixture the test depends on, so a missing
  participant shows up as a failure rather than a hang.

## Choose meaningful cases

Test behaviour, not the implementation: boundaries, invalid inputs, protocol sequences, error
handling and resource cleanup where relevant. Parametrise across configurations the code supports
(for example architectures or speeds, as `pytest.mark.parametrize` is used in existing libraries).
For numerical code, compare against a reference within a stated error bound; see
[`xmos-numeric-programming`](../xmos-numeric-programming/SKILL.md).

Keep functional and timing tests separate. A timing test must state the clock configuration, the
other threads running and the measurement method; see
[`xmos-debugging-profiling`](../xmos-debugging-profiling/SKILL.md) for hardware-timer measurement
and [`xmos-clock-domains`](../xmos-clock-domains/SKILL.md) for the reference clock.

Record the target, toolchain and dependency versions a test was verified with.
