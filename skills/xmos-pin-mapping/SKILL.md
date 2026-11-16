---
name: xmos-pin-mapping
description: Use when designing the system around an XCORE, in particular working out which IO pins to use for different interfaces, and which package to select.
---

# Pin mapping on XMOS XCORE devices

This skill is for how to select which GPIO to use for a system
design and the trade-offs made. Use it when the design uses GPIO and the
prompt does not specify which GPIO to use. The skill can also be used to
verify the correct use GPIO that has been specified. When designing GPIO
use, always verify that the GPIO is fit for purpose, there may be physical
aspects that are outside the scope of this skill.

## Pins, ports, the Portmap, and the XN file

There are three documents to refer to:

- *AN02039: Pins, Ports, and the XN file* (XM-015276-AN), published as browsable HTML at
  <https://www.xmos.com/documentation/XM-015276-AN/html/doc/rst/an02039.html>.
  This contains an extended description of this skill.

- *xcore.ai Package port map* (XM-014394-PC), published as an excel spreadsheet on
  <https://www.xmos.com/download/xcore_ai-Package-port-map.xls?version=latest>. This is

  called the port-map, and shows which packages bring out which ports on
  which pins.

- *xcore.ai datasheet* (XM-015129-PC), published as browsable HTML at
  <https://www.xmos.com/documentation/XM-015129-PC/html/rst/XU316-1024.html>.
  Sections of particular importance are:

  - **Pin Configuration** that contains contains graphical representations
    of the packages available;

  - **Signal Description and GPIO** that lists the signal names and their
    functions in terms of ports, links, and also their IO voltage domain

The **portmap** is the mapping of IO functions to physical pins of the
package. This goes through three indirections:

- All IO signals are represented by *ports* in the architecture, where a
  port is 1, 4, 8, 16, or 32 bits wide. Ports can serialise and deserialise
  signals (see [`xmos-xs3-architecture`](../xmos-xs3-architecture/SKILL.md)).
  Given a system requirement of, say, Quad-SPI that
  requires one 4-bit signal and two 1-bit signals the software would be
  most efficiently written using one 4-bit port and two 1-bit ports. When
  using the standard XMOS libraries, it will specify what port-widths are
  required for each interface instance. Some libraries may have multiple
  options, for example I2C using a single 4-bit port or two 1-bit ports.

- Ports are multiplexed through a mux in the tile onto 64 signals The mux is
  shown in all three documents above.

- These 64 signals are then multiplexed onto IO pins with interfaces such as
  LPDDR, or XLINKs. IO pins have names (XnDmm where n is the tile number
  and mm is a value between 0 and 63), and a pin-number which is either a
  serial counter clockwise number 1, 2, 3, ... or a grid value A1, A2, A3,
  ..., B1, B2, etc

## Process for designing a port-map

1. Identify the interfaces that are required

2. Check with the libraries implementing these interfaces what options are
   available for ports. Sometimes there is a trade-off between mulitple
   narrow ports or fewer wider ports.

3. Check which packages are plausible based on the number of GPIO required.
   Pick one package where it fits for sure, and one package where it may
   just fit. Discard packages where it cannot fit.

4. Work out which interfaces should be on the same tile based on a
   plausible software architecture

5. Assign interfaces to ports, keeping in mind the port multiplexing, the
   presence of any USB/MIPI/boot flash interfaces, XSCOPE links, and
   port sharing. You may need to iterate this and the previous step

6. If there is freedom to shuffle ports around (because ports are
   interchangeable) then move them to a good phsyical location based on the
   physical pin locations.

7. Create the outputs

## Restrictions on multi-bit ports and port-sharing

As a rule do not mix input and output on a single multi-bit port. When
software outputs to an N-bit port *all* N bits will be driven. When
software inputs on an N-bit port *all* N bits will go hi-Z.

A multi-bit port can be used to collect a set of disparate interfaces. For
example, a 4-bit port may be used to sample four buttons, or an 8-bit potrt
may be used to drive five leds and three reset signals of external
components. However, a multi-bit port can only be used by one thread at a
time, so in a situation where two independent threads require two signals
each, it is better to use two four bit ports (wasting a few signals), or
four 1-bit ports. If a port must be used in two threads, then it should be
protected by some form of synchronisation between the threads (lock,
channel, synchroniser); a port that is used within a few clock cycles in two
different threads triggers an **ET_RESOURCE_DEP** exception.

Ports can generally not be shared between interfaces. Sometimes one may
share a port, for example a clock input may be shared between two
interfaces that happen to use the same clock. This requires that clock to
be always driven, and be set-up outside the software that implements the
interface.

## Restrictions of packages

A package may be specified as part of the prompt, otherwise ask whether a
package should be specified as part of the design. When selecting a
package, smaller packages are generally cheaper than bigger packages, and
use less area on the PCB and are hence preferable. However, smaller
packages may not have enough pins to satisfy the requirements. Always
confirm the package choice because future extensions may be difficult when
most GPIO of a package are used.

Another difference between packages are IO voltages. Smaller packages may
only support a single IO voltage, larger packages may be flexible with IO
voltages. The datasheet specifies this, and if flexible there are pins to
select the IO voltage for at most three of the banks. For example,
**LV_T_N** can be used to select the voltage on the top bank. The signal
table in the
datasheet specifies which GPIO are connected to each VDDIO bank. If IO
voltages are not specified confirm with the user what IO voltages are
required and explain the constraints if necessary.

Not all packages come in all operating speeds or temperature grades.
The operating speed is encoded in the final two digits of the product name:
24 means 600 MHz and 32 means 800 MHz. The temperature grades may be Commercial, Industrial,
or Automotive. In general, lower temperature grades and lower operating
speeds are cheaper. The operating speed dictates the maximum pipeline
throughput. If more MIPS is required than eight 75 MHz threads, then an 800
MHz package may be a solution.

## Multiplexing of ports and links onto pins

Be careful with multiple functions being mapped onto a single IO pins on
the package, or with ports being used by other on-chip elements such as
MIPI or USB.

* Ports are muxed, and narrow ports always have precendence over wider
  ports.

* Ports used by USB or MIPI are colored in the portmap. When a tile needs
  one of the PHYs (for example for a USB project), none of those ports
  should be used by anything else. Note that where 8-bit ports are being
  used by the USB PHY, the underlying pins can still be used by 4-bit
  ports because the mux prioritises narrow ports over wide ports. Note that
  on some packages 1-bit ports on a tile may not have been brought out on
  the assumption that USB may be used on that tile. So if USB is required
  it may be best on the tile that brings fewest of the conflicted 1-bit
  ports out.

* XLINKs also come out on GPIO. When an XLINK is used (for xscope or for
  connecting two die), they take priority over the ports. This mux is shown
  in the portmap

* Other digital interfaces, such as LPDDR are also multiplexed onto the GPIO
  pins. When enabled, they take precedence over the GPIO or any link. This
  mux is shown in the portmap and datasheet.

* The system may be required to boot over some sort of SPI interface.
  The pins for these interfaces are fixed and are listed in the datasheet
  (section **Boot Procedure**). The most common case is the use of QSPI
  flash, this is also listed in the port-map.

If you have a choice, avoid sharing two interfaces on a wide port, and
instead use two narrower ports for the two interfaces.

Not all pins of a port may be bonded out on a package. You can still use
the bonded out pins, it just means that on input the bits that were not
bonded out must be masked.

## Physical locations of pins

All N-bit ports are interchangeable with each other (apart from any
multiplexing into the pins). As such, it can be beneficial to locate pins
that are physically close together for a single interface.

The graphical representation in the datasheet or the pin number can be used
to determine which pins are close together. When using the pin number, keep
in mind that on QFP and TQFP packages the GPIO with the highest pin number
ise also be near pin 1. On a BGA package that uses a pin GRID pins are
two-dimensional, so they must be close in both dimensions. Also note that
some letters (I, O, S) are not used for row names.

## XSCOPE Usage

If unspecified, you must check whether XSCOPE (for fast debugging) is
required or not. If XSCOPE Is required you must reserve a 2-wire link (4
pins) for XSCOPE. If it is not required, check that the user understands
that they will debug over JTAG only.

## Multiple tiles

Each tile (see [`xmos-xs3-architecture`](../xmos-xs3-architecture/SKILL.md)).
has it's own set of ports. As a rule, interfaces that
require a multitude of GPIO signals need to have their ports co-located on
the same tile. The exception may be very slow interfaces (such as reset
signals) that may be driven from elsewhere.

Hence, you must consider three items simultaneously:

- how to best split software across tiles;

- what GPIO is available on each tile; and

- which package to use

You may have to run a few experiments. Also confirm with the user for future extensibility.

## Creating the outputs: a portmap, XN file, and table

You can show the end-result by using the graphical representation from the
datasheet, and annotating the pins with the signal names for each of the
interfaces. You should also add columns to the portmap spreadsheet; one per
interface. In the column place the signal name in the row associated with
the pin. You can hide rows that are not relevant to the chosen package, and
highlight rows that are unavailable due to the use of, for example, USB or
MIPI PHYs.

You must make a table showing the XnDmm name, the pin number, and the port
name/bit number for each element of the interface. One line per pin. The
table must list pins that are not connected.

You must make an XN file where in the appropriate `<Tile>` section
(there is one for each tile) you label each port that has been used with
the appropriate signal name like
`<Port Location="XS1_PORT_1L" Name="I2C_SCL"/>`. When creating an XN ile
make sure you use the correct package. More help on the XN file is in
*AN02039* linked earlier.
