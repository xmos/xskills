---
name: xmos-library-repo-style
description: Use when creating or editing files in an XMOS library-style repository (lib_*, sc_*, fwk_*, sln_*, or similar) so that source headers, LICENSE, settings.yml, README.rst, CHANGELOG.rst and repository agent guidance follow XMOS conventions -- copyright headers, README metadata, changelog format, version consistency, doc/rst structure, dependency version pinning and preservation of legacy compatibility. Use alongside any repo-check/repo-linting tool that validates these conventions.
---

# XMOS library repository style

XMOS library-style repositories (`lib_*`, and legacy `sc_*`/`fwk_*`/`sln_*`) follow a standard set
of file conventions across source headers, packaging metadata, and documentation. Writing new files
to match these conventions from the start avoids a separate clean-up pass later. Repository *type*
(library vs. application-note vs. reference-design, etc.) is inferred from the repo's directory name
prefix — this skill focuses on **library** repos; note the differences called out below for
application-note (`an*`) repos where relevant.

## Repository agent guidance and legacy compatibility

Read and preserve the repository's existing `AGENTS.md`. Where it has shared guidance
followed by `## Repository-Specific Guidance`, keep the shared prefix intact and place
custom instructions after that heading. Do not overwrite existing project instructions
when adding or updating references to central guidance.

References to xskills should identify accessible guidance and follow the setup options
in its [`README.rst`](../../README.rst). A URL alone does not install or load skills;
do not assume a particular coding tool or local checkout path.

Repository-specific hardware, compatibility and legacy requirements take precedence
over general recommendations. Preserve existing APIs, supported targets, build systems
and coding conventions unless migration is requested; avoid unrelated modernisation
when maintaining older libraries.

Only describe a library as superseded when the replacement is confirmed. If documenting
that status, identify and link the successor in both repository-specific agent guidance
and the README, distinguishing the recommendation for new development from instructions
for maintaining the existing implementation.

## Copyright headers on every source file

Every source file (`.c`, `.h`, `.cpp`, `.cxx`, `.hpp`, `.s`, `.xc`, `.java`, `.py`) starts with a
copyright notice, using that language's comment syntax (`//` for C-like languages, `#` for Python),
placed **after** a shebang line if one is present. The exact wording depends on the repo's declared
license (see `settings.yml` below); the two most common are:

```c
// Copyright 2021-2026 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.
```

```c
// Copyright (c) 2018, XMOS Ltd, All rights reserved
// This software is available under the terms provided in LICENSE.txt.
```

- The year is a single year, or a `start-end` range, reflecting **git history** for that specific
  file (first commit year through most recent commit year) — not the repo's overall age, and not a
  fixed/hardcoded value. When editing an existing file in the current year, extend the end year if
  it doesn't already cover it.
- Use the exact wording for the repo's license type; don't paraphrase it.
- New files get the current year as a single year
- If git history is shallow or unreliable, preserve the existing start year; only extend the end year.
- Skip generated files, build output, and third-party/vendored directories.

## LICENSE file

Exactly one `LICENSE.<ext>` file at the repo root (e.g. `LICENSE.rst`), whose content matches the
standard template for the license type verbatim. Don't leave stray extra `LICENSE.*` files around
after changing license type. 

License files belonging to third-party code included in the repo are out of
scope: never remove or modify them. If unsure whether a license file is
third-party, do not touch it and flag it instead.

## `settings.yml`

- First line must be exactly:
  ```yaml
  # This file relates to internal XMOS infrastructure and should be ignored by external users
  ```
- `version:` — a semver string (`X.Y.Z`, optionally with a pre-release suffix); this must match the
  version used everywhere else (see "Version consistency" below). In practice, real repos do **not**
  carry a separate `license:` field in `settings.yml` — the license type is determined by the
  `LICENSE.*` file's actual content (see above), not by a `settings.yml` key.
- `documentation:` block:
  - `root_doc: doc/rst/<repo_name>.rst` — must point to a file that actually exists.
  - `cognidox_part_number` — ends `-UG` for a library's user guide (`-AN` for application notes).
  - `pdfs:` — one entry for the main doc, and one for `README.rst` whose `pdf_title` starts with
    `<repo_name>: ` and ends with `(README)`, with `pdf_short: true`.
  - `doxygen_projects.<repo_name>.doxyfile_path` (non-application-note repos) — pointing to a real
    Doxyfile whose `PROJECT_NAME` equals the repo name and `PROJECT_BRIEF` equals the README title
    text after `<repo_name>: `.
- `software:` block with `cognidox_part_number` ending `-SM` — required if the repo has any
  `app_*` directory, optional otherwise.

It's common to define a name field (`lib_name` for a library repo, or `sw_name` for an application
repo) plus `project`/`title` once near the top and reference them elsewhere via `{{placeholder}}`
substitution (e.g. `title: '{{lib_name}}: My Library'`, reused in both `documentation.pdfs` and
elsewhere) rather than repeating the repo name/title string throughout the file.

## `README.rst`

Structure, in order:

1. `:orphan:` as the very first (non-blank) line.
2. A title, over/underlined with `#` characters, of the exact form:
   ```rst
   ################################
   <repo_name>: <Descriptive Title>
   ################################
   ```
3. An RST field-list metadata block, e.g.:
   ```rst
   :vendor: XMOS
   :version: 1.0.0
   :description: One-line description of what this library does
   :scope: General Use
   :category: Audio
   :keywords: I2S, audio, DSP
   ```
   - Required: `:vendor:` (always `XMOS`), `:version:` (must match `settings.yml`), `:description:`.
   - Optional fields (`:scope:`, `:category:`, `:keywords:`, `:devices:`, `:hardware:`, etc.) are
     checked against a controlled vocabulary — stick to plain, descriptive, conventional values
     (e.g. scope values like `General Use`/`Demo`/`Tutorial`/`Example`; category values like
     `Audio`/`Voice`/`Vision`/`Networking`/`General purpose`/`Core & system`) rather than inventing
     new field names or highly novel values.
     - `:devices:` — the common field on `lib_*` repo READMEs, listing the **device family/
       architecture** the library supports (e.g. `:devices: xcore.ai, xcore-200`) — confirmed as
       the field actually used across the large majority of library repos checked (`lib_adat`,
       `lib_i2c`, `lib_i2s`, `lib_locks`, `lib_logging`, `lib_spdif`, `lib_sw_pll`, `lib_xassert`,
       `lib_xcore_math`, `lib_xua`, `lib_xud`, `lib_board_support`).
     - `:hardware:` — used instead of (or alongside) `:devices:` on application-note/example/
       application READMEs to name a **specific board part number** (e.g.
       `:hardware: XK-EVK-XU316` or `:hardware: XK-AUDIO-216-MC, XK-AUDIO-316-MC, XK-EVK-XU316`)
       rather than a device family — don't confuse the two when writing a new README.
4. The following sections, **in this exact order** (each its own properly over/underlined RST
   title): **Summary, Features, Known issues, Development repo, Required tools, Required libraries
   (dependencies), Related application notes, Support**. `Host system requirements` is an optional
   section that may also appear. For an application-note repo, drop **Development repo** and
   **Support**, and present the repo name in upper case throughout.
5. The whole file must be valid RST (no syntax errors — check with an RST linter before finishing).

## `CHANGELOG.rst`

```rst
<repo_name> change log
=======================

UNRELEASED
----------

  * Change not yet released

1.2.0
-----

  * ADDED: Short description of a new feature
  * FIXED: Short description of a bug fix
  * Changes to dependencies:

    - lib_xcore: 5.0.0 -> 5.1.0
    - lib_logging: Added dependency 3.0.0
    - lib_old_thing: Removed dependency
```

- Title line: `<repo_name> change log` (or `<name> library change log`), underlined with `=`.
- An `UNRELEASED` section, if present, **must be the very first entry**, above all released
  versions — never partway down the file.
- Each released version is a bare `n.n.n` header underlined with `-`.
- Change bullets are two-space-indented `* ` items, optionally prefixed `ADDED:`, `CHANGED:`,
  `FIXED:`, or `RESOLVED:`.
- Dependency changes are nested under a `  * Changes to dependencies:` bullet, each as
  `    - lib_name: Added dependency n.n.n` / `n.n.n -> n.n.n` / `Removed dependency`.
- A `Legacy release history` marker, if present, ends structured parsing — everything below it is
  free-form and left alone.

## Version consistency

The same version string must appear in: `README.rst` (`:version:` field), `settings.yml`
(`version:`), the top of `CHANGELOG.rst`, `module_build_info` (`VERSION = n.n.n`, if present),
`lib_build_info.cmake` (`set(LIB_VERSION "n.n.n")`, if present), and any `pyproject.toml`
(`version = "n.n.n"`). **Exception**: if every one of those files uses the same pre-release/alpha
version, `CHANGELOG.rst` may instead lead with an `UNRELEASED` section (not yet have a matching
numbered entry).

## `doc/rst/` structure

Every repo needs a `doc/rst/` folder containing at least one `.rst` file. That documentation must
**not** `.. include::` the top-level `README.rst` — the user guide and the README are kept
independent documents even though both describe the same library.

## Dependency version pinning

- `module_build_info`: every entry in `DEPENDENT_MODULES` needs a minimum-version constraint:
  ```
  DEPENDENT_MODULES = lib_logging(>=2.0.0) lib_xassert(>=4.0.0)
  ```
- `lib_build_info.cmake`: every entry in `LIB_DEPENDENT_MODULES` needs an exact version, each
  individually quoted, with no comparison operator:
  ```cmake
  set(LIB_DEPENDENT_MODULES "lib_logging(2.0.0)" "lib_xassert(4.0.0)")
  ```

## Compiler flags (application-note repos only)

Every `APP_COMPILER_FLAGS*` variable in every `CMakeLists.txt` must include `-g` (debug symbols) —
see [`xmos-build-system`](../xmos-build-system/SKILL.md) on why `-g` matters for `xgdb`.

## Related

See [`xmos-project-structure`](../xmos-project-structure/SKILL.md) for the broader sandbox
convention these repos live in, and [`xmos-embedded-c-practices`](../xmos-embedded-c-practices/SKILL.md) /
[`xmos-c-programming`](../xmos-c-programming/SKILL.md) for the source code itself rather than its
packaging/documentation.
