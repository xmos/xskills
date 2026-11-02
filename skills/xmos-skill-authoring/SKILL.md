---
name: xmos-skill-authoring
description: Use when adding a new skill to this repository, updating an existing SKILL.md, or deciding whether new information belongs in a skill vs AGENTS.md. Also use whenever XMOS documentation reveals something that would have been useful to know in advance.
---

# Authoring skills in this repository

Meta-skill for maintaining `xskills` itself.

## Deciding where new information belongs

| Situation | Put it in |
|---|---|
| Deep guidance needed only for specific tasks (e.g. "how do I profile with xgprof") | A skill (`skills/<name>/SKILL.md`) |
| A principle that must be applied in every coding task in this repository (e.g. target XS3, use C) — if in doubt, prefer a skill instead | [`AGENTS.md`](../../AGENTS.md) core principles (keep this list short) |

Prefer a skill over expanding `AGENTS.md` whenever the content is long or only occasionally
relevant — `AGENTS.md` is always loaded, so it must stay concise.

## Writing a new `SKILL.md`

1. Create `skills/xmos-<kebab-case-name>/SKILL.md`. Prefix every skill name with `xmos-`
   so XMOS skills are easy to recognise and group in skills lists. The `name` in frontmatter
   must match the folder name.
2. Write a `description` using the "Use when..." pattern, listing concrete triggers (symptoms,
   commands, file types) an agent might encounter — this is what drives discovery, so make it
   keyword-rich rather than vague.
3. Only state facts that are verifiable against XMOS's own documentation (a link on 
   `https://www.xmos.com/`, the XTC Tools docs at
   `https://www.xmos.com/documentation/XM-014363-PC/html/` for 15.3.1, an XMOS application note, or
   the XS3 architecture manual) — or against this repository's own other skills. If something can't
   be verified, say so explicitly in the skill rather than presenting it as fact (see the Mac/Linux
   environment-activation caveat in
   [`xmos-environment-setup`](../xmos-environment-setup/SKILL.md) and the `xgprof` caveat in
   [`xmos-debugging-profiling`](../xmos-debugging-profiling/SKILL.md) as examples of this pattern).
4. Cross-link related skills rather than duplicating their content.
5. Reference authoritative documentation rather than reproducing it, including device datasheets,
   applicable errata, XTC Tools documentation, application notes and architecture manuals. Explain
   when to consult each source, which sections matter and how to apply them. Keep only the
   conceptual context needed to guide that investigation. Do not duplicate register tables,
   operating limits, formulas or programming sequences maintained in those sources: copied details
   can become stale. Identify the relevant device, document revision or toolchain version where
   applicability matters, and state when the source cannot be accessed or verified.
6. Use a `references/` subfolder for skill-specific supporting material that would make `SKILL.md`
   unwieldy, and link to it from the skill. Do not use it to store copies or rewritten versions of
   existing documentation; moving duplicated information out of `SKILL.md` does not prevent drift.
7. Add entries to the skills indexes in [`AGENTS.md`](../../AGENTS.md) and
   [`README.rst`](../../README.rst).
8. Keep resources a skill needs (scripts, references) inside its own directory and link them
   relatively. Links to other skills and repository-root files are navigation aids that may be
   missing when a skill is installed on its own; don't make them essential to completing the task.

## Updating an existing skill

If you discover a fact that contradicts or refines something already written (e.g. you confirm the
exact Mac/Linux environment-activation command, or the `xgprof` post-processing workflow), update
the skill in place and remove the caveat rather than leaving stale/uncertain text next to newly
confirmed facts.

## Deleting a skill

If a skill becomes fully obsolete or is entirely superseded by another one, delete its folder,
remove its entries from the skills indexes in [`AGENTS.md`](../../AGENTS.md) and
[`README.rst`](../../README.rst), and update any
cross-links in other skills that referenced it — don't leave a dangling entry or a broken relative
link behind.

## When you learn something new from the docs

Whenever using this repository's skills alongside the real XMOS documentation surfaces something
that would have been useful to know in advance and isn't captured anywhere yet, add it — as a new
skill if it's substantial and self-contained, or as an addition to an existing skill if it's a
natural extension. This repository is meant to be self-extending over time.
