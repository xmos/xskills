---
name: xmos-clock-domains
description: Use when reasoning about xcore.ai clock domains, changing frequencies through XN configuration or PLL registers, diagnosing timing after a clock change, or choosing between clock generation and tracking an external reference. Consult device-specific datasheets and errata, AN02022 and the applicable XTC Tools documentation.
---

# xcore.ai clock domains

Use this workflow to identify the right clock and configuration method. Obtain exact
limits, register definitions and programming sequences from the applicable documentation
rather than treating examples or remembered values as device-independent guarantees.

## Establish the target and sources

Identify the exact device/part, silicon revision where relevant, board, XTC version
and required clock behaviour. Read the board's clock wiring, oscillator information,
project XN file, boot configuration and any runtime clock changes.

Consult these sources for their distinct purposes:

- **The exact device's datasheet and applicable errata:** clock tree, supported clock
  sources and routing, operating conditions, frequency/PLL limits, register definitions
  and revision-specific restrictions. Obtain these from the device's official product
  page or documentation downloads on [xmos.com](https://www.xmos.com/), or an identified
  official local copy. A shared architecture does not imply identical device limits.
- **[AN02022: xcore.ai Clock Frequency Control](https://www.xmos.com/documentation/XM-014200-AN/html/doc/rst/an02022.html):**
  clock relationships, configuration approaches and worked examples. Check its scope
  against the target; examples do not override the device's datasheet or errata.
- **[XTC Tools 15.3 documentation](https://www.xmos.com/documentation/XM-014363-PC/html/):**
  XN clock attributes and how the selected tools configure clocks when loading,
  debugging or booting an image. Use documentation matching the project's toolchain.
- **Board documentation:** the actual fitted clock sources and connections, which
  can differ from the device's available clocking options.

Record document revisions and relevant sections for recommendations. If online sources
are inaccessible, use accessible official copies and identify their versions. If essential
evidence is unavailable, explain the gap; do not invent numerical limits or register recipes.
If references disagree, identify the discrepancy and verify which applies to the selected
device and toolchain before recommending a setting; do not silently merge conflicting recipes.

## Keep the clock domains distinct

- Distinguish System/Core PLL, tile execution clocks, xCONNECT switch clock and reference
  clock; changing one is not necessarily equivalent to changing the others.
- Hardware-timer tick conversion depends on the configured reference clock, not the tile
  execution rate. Check the actual configuration rather than assuming the usual 100 MHz.
  A changed reference frequency requires reviewing timing constants and affected consumers.
- For port or clock-block timing, identify the selected clock source and divider rather
  than assuming every peripheral is clocked directly from the reference clock.
- Distinguish Secondary/Application PLL clock generation from synchronisation to an external
  reference. For tracking, investigate an existing implementation such as
  [lib_sw_pll](https://github.com/xmos/lib_sw_pll), verifying the selected version's
  documentation and device compatibility before recommending it.

## Choose and verify the configuration method

Prefer XN configuration for static clock requirements where supported. Check the documented
meaning and prerequisites of `Oscillator`, `SystemFrequency`, `ReferenceFrequency` and
`SecondaryFrequency`, including whether the tools can achieve the requested frequency.
Do not assume a requested value is the actual value. See
[multi-tile architecture](../xmos-multi-tile-architecture/SKILL.md) for XN context.

For runtime register changes, first consult the applicable programming sequence and errata.
Verify field encodings and enable controls individually, settling/lock requirements,
reset effects, and system-wide versus per-tile scope. Do not generalise one divider's
encoding to all fields or reuse a workaround without checking its device/revision scope.
For multi-tile changes, establish affected tiles and documented reset/reconfiguration order.

Check the proposed configuration against the device's operating conditions and the
requirements of every affected consumer, including communications and externally clocked
components. Preserve required relationships between domains during transitions as well
as in the final state. Distinguish reset defaults from boot, loader and runtime settings.

Explain the chosen source, resulting clocks, applicable limits and timing implications
with references. Verify actual hardware/peripheral behaviour on hardware; simulator
wall-clock runtime is not target execution time. See
[debugging/profiling](../xmos-debugging-profiling/SKILL.md) for measurements and
[run/simulate](../xmos-run-and-simulate/SKILL.md) for execution.
