---
name: xmos-library-repo-style
description: Use when creating or editing library-style repositories for XMOS targets (lib_*, sc_*, fwk_*, sln_* or similar), maintaining source notices, LICENSE, settings.yml, README.rst, CHANGELOG.rst or agent guidance. Applies repository conventions without assuming copyright ownership, licence or vendor. Covers metadata, version consistency, doc/rst structure, dependency pinning and legacy compatibility; use alongside applicable repository checks.
---

# XMOS library repository style

Repositories for XMOS targets may adopt common library conventions (`lib_*`, and legacy
`sc_*`/`fwk_*`/`sln_*`) for packaging and documentation. Establish which conventions the
project actually requires before applying them. Prefixes are clues to repository roles,
not proof of ownership or a requirement to adopt internal XMOS infrastructure. This skill
focuses on library repos; application-note (`an*`) differences apply only where relevant.

## Ownership and licensing

Do not determine legal ownership. Preserve existing copyright, attribution and licence
notices, including third-party notices; do not judge their legitimacy. Do not infer
ownership from a `lib_*` prefix, XMOS hardware, organisation membership, the user's
employer, commit history or licence choice. An existing notice applies to its file,
not automatically to every new file.

Use only explicit project instructions supplying the notice text or template, licence
or vendor value and the files it applies to. Without such instructions, add no new
attribution and leave existing legal metadata unchanged. Continue ordinary coding
without investigating ownership or asking ownership questions. Ask only when the
requested task requires a legal-metadata edit and the necessary instructions are missing
or conflicting. Do not insert XMOS attribution, relicense code or remove existing notices
to satisfy formatting checks. Existing project instructions need no separate ownership
verification.

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

## Source notices

This skill supplies no default header. Use the project's supplied notice text or template
only when its instructions explicitly apply it to the file. Use the language's comment
syntax and place it after any shebang. Do not fill a missing holder or licence by research,
inference or copying an adjacent file. If no header policy is supplied, add no header.

- Preserve existing holders and notices; do not copy ownership from an adjacent file.
- Update year ranges only when the confirmed policy calls for it, using that file's
  history. Commit author names and dates do not establish copyright assignment.
- If history or the applicable policy is unclear, preserve the notice. Ask only if the
  requested task requires changing it; otherwise continue without a legal-metadata edit.
- Keep required licence/SPDX notices intact. Licence selection and copyright ownership
  are separate decisions; one does not establish the other.
- Do not bulk-update generated files, build output or third-party/vendored directories.

## LICENSE file

Preserve the project's existing licence files and their scope. Do not add, replace,
consolidate or delete them simply to match an XMOS template. Multiple licences may be
intentional. A repository's approved checks may require one particular root licence
file; only apply that requirement within the supplied project instructions.
If a licence is missing, do not create one unless explicitly instructed. If the requested
task requires a licence edit but the supplied terms are missing or conflicting, ask rather
than selecting a default. Formatting or adopting xskills is not authorisation to change licensing.

License files belonging to third-party code included in the repo are out of
scope: never remove or modify them. If unsure whether a license file is
third-party, do not touch it and flag it instead.

## `settings.yml`

This section applies only to repositories that use the XMOS internal schema. Do not
create this file, insert internal identifiers or change legal metadata solely because
a project targets XMOS hardware. Follow the selected schema and confirmed project policy.

- For that internal schema, the first line is:
  ```yaml
  # This file relates to internal XMOS infrastructure and should be ignored by external users
  ```
- `version:` — a semver string (`X.Y.Z`, optionally with a pre-release suffix); this must match the
  version used everywhere else (see "Version consistency" below). A `license:` key is
  not present in every repository. Inspect existing licence files and the selected
  schema to understand the configuration; neither a key nor a licence file establishes
  copyright ownership or authorises applying a new licence.
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

For projects adopting this README convention, use the following structure while
preserving the actual project identity and existing notices:

1. `:orphan:` as the very first (non-blank) line.
2. A title, over/underlined with `#` characters, of the exact form:
   ```rst
   ################################
   <repo_name>: <Descriptive Title>
   ################################
   ```
3. An RST field-list metadata block, e.g.:
   ```rst
   :vendor: <project-supplied vendor value, if required>
   :version: 1.0.0
   :description: One-line description of what this library does
   :scope: General Use
   :category: Audio
   :keywords: I2S, audio, DSP
   ```
   - Where required by the project's schema: `:vendor:`, `:version:` (consistent with
     its version metadata) and `:description:`. Preserve existing vendor metadata; use
     only an explicitly supplied value for a new field. Otherwise omit it, asking only
     if the requested task requires that field. Vendor and copyright holder are not
     interchangeable. Report a checker-policy mismatch instead of inventing metadata.
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
