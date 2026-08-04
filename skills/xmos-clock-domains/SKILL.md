---
name: xmos-clock-domains
description: Use when reasoning about xcore.ai clock domains -- the System/Core PLL, the Secondary/Application PLL, the reference clock, switch clock, and tile clock -- when changing clock frequencies via the XN file or PLL registers, or when a hardware-timer/port-timing measurement looks wrong after a clock change. Covers AN02022 (xcore.ai Clock Frequency Control).
---

# xcore.ai clock domains

**Source**: AN02022 *xcore.ai Clock Frequency Control*, publicly available at
<https://www.xmos.com/documentation/XM-014200-AN/html/doc/rst/an02022.html>. Fetch it directly for
exact PLL register bit layouts, additional worked frequency examples, or the Secondary PLL
fractional-divider math — this skill summarizes the concepts and the facts most likely to bite an
agent, not the full register reference.

## The clock tree

An input clock/crystal on `XIN` (8–30 MHz) drives the **System PLL** (aka Core/Primary PLL), which
produces a high-frequency **system clock**. Dividers then derive, from that system clock:

- the **xcore tile clock(s)** — the clock each tile's execution unit runs at,
- the **xCONNECT switch clock**, and
- the **reference clock** — which drives **hardware timers, ports, and clock blocks** (see
  [`xs3-architecture`](../xs3-architecture/SKILL.md)).

A separate **Secondary PLL** (aka Application PLL) can independently generate one more frequency,
typically for external devices/peripherals (e.g. an audio codec, LPDDR, MIPI) rather than for the
tiles themselves.

At reset/boot the System PLL defaults to values that support an 8–30 MHz `XIN` and produce a
133–500 MHz tile clock and (by default) a **100 MHz reference clock**. Applications very commonly
reprogram the PLL on boot to run tiles faster (e.g. 600/800 MHz) — **do not assume the reset
defaults hold**; check the project's XN file or PLL-configuration code.

## ⚠️ The reference clock drives hardware timers — and it is configurable

Hardware timers (`hwtimer_get_time`, see
[`xmos-c-programming`](../xmos-c-programming/SKILL.md)/[`xmos-debugging-profiling`](../xmos-debugging-profiling/SKILL.md))
and port/clock-block timing all run off the **reference clock**, not directly off the tile clock.
The 100 MHz figure quoted elsewhere in this repo is the **default/typical** value — it is a
configurable divider (`REFDIV`) off the system clock, and application code (or an XN file) may
change it. Concretely:

- If a project's XN file sets a non-default `ReferenceFrequency`, or code writes
  `XS1_SSWITCH_REF_CLK_DIVIDER_NUM` directly (e.g. AN02022's "Fast Reference Clock" recipe, which
  halves `REFDIV` to double the reference frequency), then **every hardware-timer tick duration
  changes** — a manual `t1 - t0` elapsed-tick measurement (see
  [`xmos-debugging-profiling`](../xmos-debugging-profiling/SKILL.md)) no longer equals
  `elapsed / 100` microseconds unless the reference clock is still 100 MHz.
- Before trusting an elapsed-tick-to-time conversion, confirm the actual configured reference
  frequency for the target (XN file `ReferenceFrequency` attribute, or the value last written to
  the reference-clock divider) rather than assuming 100 MHz.
- Changing the reference clock affects **all** timers/ports/clock-blocks on that tile — not just
  the one being measured.

## Configuring clocks: prefer the XN file

For the vast majority of applications, set the desired frequencies declaratively in the project's
**XN file** (see [`xmos-multi-tile-architecture`](../xmos-multi-tile-architecture/SKILL.md) for XN
files in general) rather than reprogramming PLL registers by hand:

```xml
<Node Id="0" InPackageId="0" Type="XS3-L16A-1024"
      SystemFrequency="500MHz" ReferenceFrequency="100MHz" Oscillator="20MHz">
```

- `Oscillator` — the input frequency on `XIN`. Must be given for `SystemFrequency`/
  `ReferenceFrequency`/`SecondaryFrequency` to take effect.
- `SystemFrequency`, `ReferenceFrequency`, `SecondaryFrequency` — desired output frequencies; the
  tools compute PLL divider values and, for `xflash`, bake the reprogramming sequence into the boot
  code automatically. `xrun`/`xgdb` reprogram the PLL live via JTAG on `connect`.
- If a requested frequency can't be hit exactly, the tools pick the closest achievable value and
  warn (`xflash`/`xgdb` always; `xrun` only with `--verbose`).

## Configuring clocks manually (registers)

Only needed when the XN file's static model isn't enough (e.g. changing frequency at runtime). From
C (`xs1.h`): `write_sswitch_reg`/`read_sswitch_reg` for system-wide PLL/switch/reference registers,
`write_pswitch_reg`/`read_pswitch_reg` for per-tile registers.

| Register | Controls | Key fields |
|---|---|---|
| `XS1_SSWITCH_PLL_CTL_NUM` | System PLL | `R` (input divider), `F` (multiplier stage), `OD` (output divider); `f_vco = (F+1)/2 * f_in/(R+1)`, `f_out = f_vco/(OD+1)` |
| `XS1_SSWITCH_CLK_DIVIDER_NUM` | xCONNECT switch clock divider (`SSDIV`) | reset default gives 500 MHz from a 500 MHz system clock |
| `XS1_SSWITCH_REF_CLK_DIVIDER_NUM` | Reference clock divider (`REFDIV`) | reset default (`4`) gives 100 MHz from a 500 MHz system clock; halving it doubles the reference frequency (max: half the system clock) |
| `XS1_PSWITCH_PLL_CLK_DIVIDER_NUM` (per tile) | Tile clock divider (`XCDIV`) | **does not take effect until enabled** with `setps(XS1_PS_XCORE_CTRL0, 0x10)` on that tile |
| `XS1_SSWITCH_SS_APP_PLL_CTL_NUM` | Secondary/Application PLL control (enable, `R`/`F`/`OD`) | see errata sequence below — confirmed in `lib_sw_pll`'s `sw_pll_app_pll_init()` |
| `XS1_SSWITCH_SS_APP_PLL_FRAC_N_DIVIDER_NUM` | Secondary/Application PLL fractional-N divider | top bit enables the frac-n block; this is what a software PLL (e.g. `lib_sw_pll`) steps at runtime to fine-tune the output frequency |
| `XS1_SSWITCH_SS_APP_CLK_DIVIDER_NUM` | Secondary/Application PLL output clock divider | top bit enables the divided output |

**Constraints that always apply**: `XIN` 8–30 MHz; PLL VCO 360–1800 MHz; PLL output <800 MHz;
comparator frequency 220 kHz–1800 MHz; tile frequency must not be less than the reference
frequency; and the device's own datasheet maximum operating frequency.

**Warning**: writing the System PLL control register can reset the xCORE tile. On a multi-tile
device, reset tile 0 last if resetting multiple tiles.

### Secondary/Application PLL: control-register write errata

Naively writing `XS1_SSWITCH_SS_APP_PLL_CTL_NUM` once to change the Secondary/Application PLL's
`R`/`F`/`OD` values live does not reliably apply them — there's a known chip erratum where the new
`F`/`OD` divider values are only captured correctly if the control register is written with the PLL
disabled, then re-enabled, **twice**: disable, enable (captures dividers on a running clock),
enable again (same value, forces the capture), then disable/enable once more to get the full ~5us
reset with the correct values, followed by a settling delay (`lib_sw_pll`'s
`sw_pll_app_pll_init()` waits 500us) before touching the fractional-N or output-divider registers.
Skipping this sequence (a single disable+enable) can silently leave the PLL running at stale
divider values. This is specific to the Secondary/Application PLL control register — the System
PLL recipes above don't need it.

## Common recipes (see AN02022 for full code)

| Goal | Approach |
|---|---|
| Run tiles faster/slower than boot default | Set `SystemFrequency`/`Oscillator` in the XN file (preferred) |
| Faster hardware-timer/port resolution | Reduce `REFDIV` ("Fast Reference Clock") — remember this changes the tick rate for *all* timers/ports on the tile |
| Lower dynamic power, single-tile app | Reduce the switch clock (`SSDIV`) once configuration is done — the switch is only needed for config on a single-tile app |
| Lower dynamic power, one tile doesn't need full speed | Reduce that tile's `XCDIV` **and** call `setps(XS1_PS_XCORE_CTRL0, 0x10)` |
| Very low power / USB suspend | Bypass the System PLL (feed `XIN` straight through) then drop `F` low |
| Clock an external device (codec, LPDDR, MIPI) | Configure the Secondary/Application PLL, routed via `X1D11`/port 1D on tile 1 for a generic application clock |
| Phase-lock a generated clock to an external reference | The Secondary/Application PLL alone is **not** phase-locked — it can't natively track an external reference. `lib_sw_pll` builds a hybrid software/hardware PLL on top of it: a PFD implemented with a port/clock-block edge count, a PI control loop, and a DCO that steps `XS1_SSWITCH_SS_APP_PLL_FRAC_N_DIVIDER_NUM` (LUT or sigma-delta variant) at runtime — confirmed working end-to-end on real `XK-EVK-XU316` hardware (`lib_sw_pll`'s `app_simple_lut`/`app_simple_sdm` examples). Reach for this pattern (or the library itself) instead of hand-rolling PLL-register writes when the goal is tracking, not just generating, a clock. |

## When to fetch the full appnote

Pull AN02022 directly when you need: exact PLL register bit offsets/values, the Secondary PLL's
fractional-divider math for a specific target frequency, jitter-minimization guidance, or the full
low-power bypass-mode sequence.
