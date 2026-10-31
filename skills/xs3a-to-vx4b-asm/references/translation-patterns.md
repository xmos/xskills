# Candidate translation patterns

These are illustrative before/after snippets supplied by a contributor, not independently
verified instruction specifications or guaranteed speedups. Confirm syntax, equivalence, and
performance on the target toolchain before incorporating them into production code.

## Zero-stack leaf function

When the function is a leaf, does not need a stack frame, and its return path permits `ret`,
remove the zero-sized stack entry/exit but keep the stack resource annotation:

```asm
/* Before */
#define NSTACKWORDS 0
...
xm.entsp NSTACKWORDS * 4
...
xm.retsp NSTACKWORDS * 4
...
.resource_const FUNCTION_NAME, "stack_frame_bytes", NSTACKWORDS * 4

/* After */
...
ret
...
.resource_const FUNCTION_NAME, "stack_frame_bytes", 0
```

Do not remove an entry/exit that saves state or supports a call. Review any dual-issue
bundling at the return site separately.

## Signed floating-point mantissa

One proposed conversion from explicit sign handling and magnitude to a signed mantissa is:

```asm
/* Before: 32-bit mantissa in the low word, high word zero */
xm.brff sign, .not_neg
neg mant, mant
.not_neg:
xm.fmake res, sign, exp, zero, mant

/* After: signed mantissa in the high word */
add exp, exp, -32
xm.fmakes res, exp, mant, zero
```

The exponent adjustment is part of the change in mantissa placement, not an optional
optimisation. Verify equivalence for both signs, zero, and extreme mantissas.

If the extracted sign is used only to negate the unsigned mantissa, another proposed
replacement is:

```asm
/* Before */
xm.fsexp sign, exp, input
xm.fmant input, input
xm.brff sign, .not_neg
neg input, input
.not_neg:
...

/* After */
xm.fsexp x0, exp, input
xm.fmants input, input
...
```

Do not discard `sign` if anything else reads it. The VX4B `lib_xcore_math` implementation
of `f32_unpack_s32` uses `xm.fsexp` followed by `xm.fmants`, and `s32_to_f32` uses
`xm.fmakes`; consult their full functions to check the exponent and word ordering in
context.

## Fixed-offset byte and halfword memory access

For a fixed, encodable offset, a scalar byte/halfword load or store with an immediate
may avoid loading a separate offset register. Consider signed/unsigned loads and stores
individually: `lh`, `lhu`, `lb`, `lbu`, `sh`, `sb` are candidate forms, not blanket
replacements for `xm.ld16s`, `xm.ld8u`, `xm.st16`, or `xm.st8`.

One worked example uses a signed halfword load:

```asm
/* Before */
#define PARAM_shift 0
...
li t3, PARAM_shift
xm.ld16s res, t3(params)

/* After */
#define PARAM_shift 0
...
lh res, PARAM_shift * 2 (params)
```

The immediate is a byte offset; confirm the old instruction's offset units and the
resulting address, required alignment, and the immediate's range. This example uses zero
only to illustrate the form; verify a nonzero offset before generalising it. Other
load/store forms need their own before/after examples.

## Avoid an unnecessary move for `xm.vldr`

When the move exists solely to supply `xm.vldr`, try using the original pointer register:

```asm
/* Before */
mv t3, a2
xm.vldr t3

/* After */
xm.vldr a2
```

Check that the operand is accepted by the assembler and that eliminating the move
does not change later uses of `t3` or `a2`. This example does not establish the
complete register-encoding rules for `xm.vldr`.
