---
name: xmos-skill-authoring
description: Use when adding, updating, splitting, merging or deleting a skill in this repository, deciding whether new information belongs in a skill or AGENTS.md, or proposing an update after XMOS documentation reveals something useful to know in advance.
---

# Authoring skills in this repository

Meta-skill for maintaining `xskills` itself.

## Deciding where new information belongs

| Situation | Put it in |
|---|---|
| Deep guidance needed only for specific tasks (e.g. "how do I profile with xgprof") | A skill (`skills/<name>/SKILL.md`) |
| A principle that must be applied in every coding task in this repository (e.g. target XS3) — if in doubt, prefer a skill instead | [`AGENTS.md`](../../AGENTS.md) core principles (keep this list short) |

Prefer a skill over expanding `AGENTS.md` whenever the content is long or only occasionally
relevant. Core instructions may be loaded for every task in their scope, so keep them concise.

## Writing a new `SKILL.md`

1. Create `skills/xmos-<kebab-case-name>/SKILL.md`. Prefix every skill name with `xmos-`
   so XMOS skills are easy to recognise and group in skills lists. The `name` in frontmatter
   must match the folder name.
2. Write a `description` using the "Use when..." pattern, listing concrete triggers (symptoms,
   commands, file types) an agent might encounter — this is what drives discovery, so make it
   keyword-rich rather than vague. Keep the triggers representative of the whole capability;
   a short list of examples can make a general skill look narrower than it is.
3. Verify technical claims against applicable official documentation (on `https://www.xmos.com/`,
   the XTC Tools docs at `https://www.xmos.com/documentation/XM-014363-PC/html/` for 15.3.1, an
   XMOS application note or datasheet, or the XS3 architecture manual), versioned headers or
   source, or a reproducible check. Other skills are for navigation, not independent proof. If
   something can't be verified, say so explicitly rather than presenting it as fact.
4. Cross-link related skills rather than duplicating their content.
5. Reference authoritative documentation rather than reproducing it, including device datasheets,
   applicable errata, XTC Tools documentation, application notes and architecture manuals. Keep
   the conceptual model, decision rules and minimal examples needed to act correctly, and explain
   when to consult each source and which sections matter. Reference the documentation for
   exhaustive interfaces, numerical limits and detailed procedures; avoid maintaining a parallel
   reference manual, since copied details can become stale. Identify the relevant device, document
   revision or toolchain version where applicability matters, and state when the source cannot be
   accessed or verified.
6. Use a `references/` subfolder for skill-specific supporting material that would make `SKILL.md`
   unwieldy, and link to it from the skill. Do not use it to store copies or rewritten versions of
   existing documentation; moving duplicated information out of `SKILL.md` does not prevent drift.
7. Add entries to the skills indexes in [`AGENTS.md`](../../AGENTS.md) and
   [`README.rst`](../../README.rst).
8. Keep resources a skill needs (scripts, references) inside its own directory and link them
   relatively. Links to other skills and repository-root files may be missing when a skill is
   installed on its own; the README explains how to resolve them from an installed copy or the
   same release. Write each skill so it remains usable if a related skill is not installed.
9. Do not give agents an ownership-determination task. Preserve existing notices and use
   only project-supplied notice text or templates and explicitly stated scope; provide
   no default header, holder or licence. Without instructions, add no new attribution
   and continue ordinary coding without ownership questions. Ask only when a requested
   legal-metadata edit lacks necessary instructions. This applies to scripted updates
   and vendor metadata too, regardless of repository name, hardware, employer or licence.

## Updating an existing skill

If you discover a fact that contradicts or refines something already written, update the skill in
place and remove the caveat rather than leaving stale/uncertain text next to newly confirmed facts.

## Splitting, merging or reorganising skills

Account for every existing recommendation, constraint and caveat. Move substantive guidance to a
clear owner, replace duplicates with pointers, and call out any deliberate removal or policy change
separately from the reorganisation.

## Deleting a skill

If a skill becomes fully obsolete or is entirely superseded by another one, delete its folder,
remove its entries from the skills indexes in [`AGENTS.md`](../../AGENTS.md) and
[`README.rst`](../../README.rst), and update any
cross-links in other skills that referenced it — don't leave a dangling entry or a broken relative
link behind.

## Verifying changes

Run the repository validation suite described in [`README.rst`](../../README.rst). Check changed
commands, examples and scripts as appropriate. When changing a description or removing
substantive guidance, try representative tasks to confirm agents still find and apply it. Report
what was actually checked: passing structural tests does not verify technical behaviour.

## When you learn something new from the docs

When working with these skills alongside XMOS documentation surfaces something that would have been
useful to know in advance and isn't captured anywhere yet, propose adding it — as a new skill if
it's substantial and self-contained, or as an addition to an existing skill if it's a natural
extension. Make the change when it's requested or within the current maintenance task, rather than
expanding scope unprompted.
