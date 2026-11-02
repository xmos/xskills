---
name: xmos-capability-discovery
description: Use when finding, selecting or recommending existing XMOS software for a requested capability before implementing new functionality; checking whether a library, reference application or example fits project requirements; or identifying a documented replacement for an existing implementation.
---

# Discover existing XMOS software

Find suitable existing XMOS software before implementing equivalent functionality.
Use official metadata and documentation to establish what is available and whether
it fits the project.

## 1. Establish the requirements

Read the project's documentation and build configuration. Identify the requested
capability, relevant hardware and performance constraints, dependency versions,
toolchain and integration requirements. Distinguish new development from maintenance;
preserve existing APIs and compatibility unless migration is requested.

## 2. Discover candidates through accessible sources

Use whichever official sources are accessible in the current environment:

- [XMOS libraries](https://www.xmos.com/libraries/), linked library landing pages,
  documentation, downloads and application notes on xmos.com.
- [Official XMOS GitHub repositories](https://github.com/xmos), their READMEs,
  documentation, examples and releases.
- Official release packages or provenance-checked local copies.

Search by the requested capability and related terms, not just an assumed repository
name. Include reference applications, examples and application notes as well as libraries.

Library landing pages are published from repository READMEs. Use `description`,
`category`, `keywords`, `devices` and `version` metadata, plus summaries and features,
to find candidates. Read beyond the metadata when it is incomplete.

Neither website is a mandatory first step. If one route is inaccessible, use another;
do not make access to one site a prerequisite for using the other. Discover actual
repository branches and release links rather than relying on guessed URLs. Failed
access or an empty search result does not establish that no implementation exists.

## 3. Use a verified version

Prefer official released documentation and source matching the project's dependency
version, regardless of which site provides them. Identify version differences and
unreleased development sources explicitly; do not combine claims from different
versions without explaining the distinction.

Local files establish project context, but may contain committed or uncommitted
modifications. Check their provenance and relevant differences from an identified
official baseline before treating them as evidence of upstream behaviour. A clean
working tree alone is insufficient. Preserve local changes and state when provenance
cannot be verified; do not reset files or upgrade dependencies to obtain a reference.

## 4. Check suitability

Read candidate documentation, build configuration and examples to verify functionality,
limitations, supported devices/architectures, toolchain and integration compatibility.
Repository names and recent activity are not evidence of suitability or support status.
Only claim support, deprecation or supersession when explicitly documented, and only
recommend a successor when the replacement relationship is confirmed.

An older release may be the correct choice for maintenance. Follow the project's
requirements rather than automatically choosing the latest implementation. Use
[the build-system skill](../xmos-build-system/SKILL.md) for subsequent dependency
configuration.

## 5. Recommend with evidence

Briefly identify the candidate and version examined, why it fits, and a useful example
or integration entry point. Cite the documentation or source inspected, including
paths and baseline identity for local evidence. Explain material limitations and
verification gaps, distinguishing published behaviour from project-specific changes.

If no suitable implementation was verified, report the search scope and remaining
uncertainty rather than asserting that none exists. Continue according to the user's
task, clearly identifying any proposed custom functionality.

## Maintaining discovery guidance

Keep capability metadata and compatibility details in the owning repository's
README/documentation. Improve upstream metadata when discovery is difficult rather
than maintaining a duplicate catalogue here. Keep this workflow capability-neutral.
