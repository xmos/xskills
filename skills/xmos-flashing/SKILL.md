---
name: xmos-flashing
description: Use when writing a built .xe to an XMOS board's non-volatile flash with xflash, choosing between xrun (temporary, RAM-only) and xflash (persistent, boots standalone without a host attached), creating factory/upgrade flash images, or diagnosing xflash errors (no flash device found, JTAG vs xSCOPE programming, interactive confirmation prompts). Covers XTC Tools 15.3.1 xflash.
---

# Flashing XMOS applications with `xflash`

Requires the XTC Tools environment active (see
[`xmos-environment-setup`](../xmos-environment-setup/SKILL.md)) and a built `.xe` file (see
[`xmos-build-system`](../xmos-build-system/SKILL.md)).

## `xflash` vs `xrun`/`xsim`

- **`xrun`** (see [`xmos-run-and-simulate`](../xmos-run-and-simulate/SKILL.md)) loads a program into
  the device's **RAM** over JTAG and runs it — nothing persists once the device is reset/powered
  off, and a host + debug adapter must remain available for `--io`/`--xscope` I/O.
- **`xflash`** writes a program into the device's **non-volatile flash**, so it boots and runs
  standalone the next time the device is reset/powered on, with no host or debug adapter attached.
  Use this for anything that needs to run independently of a development machine (production
  firmware, a demo left running unattended, testing real boot behavior).

## Basic usage

```sh
xflash a.xe
```

This converts `a.xe` into the XTC flash image format, generates a matching flash loader for the
target's flash device, transfers both to the target over JTAG (via `xgdb` machinery under the
hood), programs the flash, then resets the device — which then boots from flash on its own via the
boot-source pins (ROM chain-loads the flash loader, which chain-loads the application).

By default `xflash` will prompt for interactive confirmation before programming; pass `--force`/
`-f` to skip this (e.g. in a script/CI job).

## Factory and upgrade images

For applications that support field upgrades, the flash can hold one **factory** image plus one or
more **upgrade** images, each with its own version number; the flash loader boots whichever valid
image has the highest version:

```sh
xflash --factory a.xe --upgrade 1 a_v2.xe --upgrade 2 a_v3.xe
```

- `--factory <xe-file> [size]` — at most one; `size` pads the space reserved for it (e.g. `256k`).
- `--upgrade <id> <xe-file> [size]` — `id` must be a unique number greater than 0; multiple
  `--upgrade` entries are inserted in the order given.
- If no `--factory` image is given, a single `--upgrade` image may instead be written straight to a
  file with `-o` (see below) rather than programmed directly.
- `--boot-partition-size <n>` overrides the default (whole-device) boot partition size.

## Selecting the target device

Same adapter-selection model as `xrun`/`xgdb`:

```sh
xflash --list-devices          # or -l: list connected adapters + devices, same as xrun --list-devices
xflash --id <id> a.xe          # select by the ID shown in --list-devices
xflash --adapter-id <serial> a.xe   # select by adapter serial number
```

`xflash` needs to know the flash device's properties (page/sector size, capacity). If not given
explicitly as attributes on the flash device in the target's XN file, `xflash` runs a "device
inquirer" program on the target to detect them automatically (via SFDP) — this requires a working
JTAG connection to the target, same as `xrun`.

## JTAG vs xSCOPE for programming speed

- **`--force-jtag`** (default): programs over JTAG only. Slower, but the most broadly compatible.
- **`--force-xscope`**: uses the faster xSCOPE link instead — significantly quicker flashing, but
  more prone to signal-integrity issues on some hardware, so prefer JTAG unless flash programming
  time specifically matters (e.g. in a production test fixture).

## Producing a flash image without programming

```sh
xflash a.xe -o output.bin      # write the generated flash image to a file instead of programming
xflash a.xe --make-exec prog.xe   # produce an .xe that performs the flash operation when run
```

`--make-exec` is useful for deploying flashing itself as a step runnable later via `xrun` (e.g. a
factory-programming station that doesn't have the original build environment).

## Raw flash read/write/erase

For backing up flash contents or writing an externally-generated image, `xflash` also exposes
generic operations that skip the XE→flash-image conversion (a target XN file is still required, to
know which ports talk to the SPI flash device):

```sh
xflash --target-file target.xn --erase-all
xflash --target-file target.xn --read-all -o backup.bin
xflash --target-file target.xn --write-all image.bin
```

## Other useful options

- `--no-verify-on-write` — skip the default read-back verification of each page after writing
  (slightly faster, less safe).
- `--no-reset-on-write` — leave the device halted/unreset after programming instead of resetting it
  into the newly-flashed application.
- `--analyze <file>` — inspect/print the structure of an existing flash binary or a raw flash dump,
  useful when debugging a boot failure.
- `--jtag-speed <n>` — same JTAG clock divider convention as `xrun`/`xgdb` (`25/(n+2)` MHz).

## Troubleshooting

Since `xflash` connects to the target the same way `xrun`/`xgdb` do, the same connection-error
signatures apply (`No available XTAGs`, `No XMOS devices found in JTAG chain`, etc.) — see
[`xmos-run-and-simulate`](../xmos-run-and-simulate/SKILL.md)'s troubleshooting table and confirm
with `xflash --list-devices`/`xrun --list-devices` first. A flash-specific failure to watch for is
the device inquirer being unable to identify the flash device — check the flash device's attributes
in the XN file, or pass `--noinq` and specify them explicitly if auto-detection isn't working.
