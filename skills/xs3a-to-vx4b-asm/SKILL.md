---
name: xs3a-to-vx4b-asm
description: Use when translating or reviewing XS3A assembly for VX4B, especially zero-stack leaf returns, signed float construction/extraction, fixed-offset byte or halfword loads/stores, or xm.vldr register moves. Covers candidate optimisations during translation; does not yet cover VX4B short/long register encodings.
---

# XS3A to VX4B assembly translation

Treat translation as an opportunity to remove redundant instructions, not as a mechanical
instruction-for-instruction rewrite. The [worked candidate patterns](references/translation-patterns.md)
cover zero-stack leaf returns, signed floating-point mantissas, fixed-offset memory access,
and `xm.vldr` operands.

These examples were supplied as translation notes, **not verified instruction specifications**.
Check the assembled result and behavioural equivalence (including negative values and boundary
cases) before applying a pattern. Do not apply a transformation when its operands, offset units,
stack metadata, or register liveness differ from the example. Keep target-specific instruction
encodings and performance claims out of this skill until they have been verified against XMOS
documentation and the relevant toolchain.

This skill does **not** yet define VX4B architecture, short/long instruction encodings, register
classes, or which instructions accept `x0`. Do not infer these from XS3A's register model; ask for
VX4B-specific documentation or examples before advising on register pressure and encoding choices.
For XS3A background, see [xs3-architecture](../xs3-architecture/SKILL.md).
